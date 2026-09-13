#!/usr/bin/env python3
"""AlpNAI sandbox client. Python 3.10+, standard library only. No wallet signing."""

from __future__ import annotations

import argparse
import contextlib
from datetime import date
from decimal import Decimal, InvalidOperation
import getpass
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import time
from urllib import error, parse, request
import uuid


DEFAULT_BASE = "https://alpnai.frederic150452.chatgpt.site"
MAX_BODY_BYTES = 2 * 1024 * 1024
PRODUCTS = {"snapshot", "changes", "evidence"}


class ClientError(Exception):
    """A failure that must not result in a new logical purchase."""


class RetryableError(ClientError):
    """An uncertain or temporary response; retry with the SAME purchase ID."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ClientError(
            "Redirect refused. The Site may require ChatGPT access. "
            "No agent key was forwarded to the redirect destination."
        )


def base_url(value: str) -> str:
    parsed = parse.urlsplit(value)
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if (
        not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
        or (parsed.scheme != "https" and not (local and parsed.scheme == "http"))
    ):
        raise ClientError("Use an HTTPS origin without credentials, path or query; HTTP is allowed only on loopback for tests.")
    return value.rstrip("/")


def money(value, label: str, *, allow_zero: bool = False) -> Decimal:
    if isinstance(value, bool):
        raise ClientError(f"Invalid {label}.")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise ClientError(f"Invalid {label}.") from None
    if not result.is_finite() or result < 0 or (not allow_zero and result == 0):
        raise ClientError(f"{label} must be a finite {'non-negative' if allow_zero else 'positive'} number.")
    return result


def request_json(url: str, headers: dict[str, str], timeout: float) -> dict:
    opener = request.build_opener(NoRedirect())
    req = request.Request(url, headers={"Accept": "application/json", "User-Agent": "AlpNAI-Sandbox-Kit/0.1.0", **headers})
    try:
        with opener.open(req, timeout=timeout) as response:
            if response.headers.get_content_type() != "application/json":
                raise ClientError("Expected JSON. An HTML sign-in page requires Site access; this client does not bypass platform authentication.")
            raw = response.read(MAX_BODY_BYTES + 1)
    except error.HTTPError as exc:
        messages = {
            400: "Invalid request or idempotency key.",
            401: "Access denied: check Site visibility/access and the operator-issued agent key.",
            403: "Budget exhausted, agent revoked or origin forbidden.",
            404: "Endpoint unavailable.",
            409: "Idempotency conflict. Keep the original parameters for this state file.",
        }
        if exc.code in {429, 500, 502, 503, 504}:
            raise RetryableError(f"HTTP {exc.code}: service temporarily unavailable or payments disabled.") from None
        raise ClientError(f"HTTP {exc.code}: {messages.get(exc.code, 'Request rejected.')}") from None
    except (error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError):
        raise RetryableError("Network or TLS failure. The purchase outcome may be unknown; retain the same state file.") from None
    if len(raw) > MAX_BODY_BYTES:
        raise ClientError("Response exceeds the client size limit.")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ClientError("Response is not valid JSON.") from None
    if not isinstance(payload, dict):
        raise ClientError("Expected a JSON object.")
    return payload


def quoted_product(catalog: dict, product: str, maximum: Decimal) -> tuple[dict, Decimal]:
    if catalog.get("mode") != "sandbox" or catalog.get("live_payments_enabled") is not False:
        raise ClientError("Catalog does not explicitly confirm sandbox mode with live payments disabled.")
    if catalog.get("currency") != "USDC" or catalog.get("network") != "eip155:8453":
        raise ClientError("Unexpected catalog currency or network.")
    items = catalog.get("products")
    if not isinstance(items, list):
        raise ClientError("Invalid product catalog.")
    matches = [item for item in items if isinstance(item, dict) and item.get("id") == product]
    if len(matches) != 1:
        raise ClientError("The requested product is missing or ambiguous.")
    item = matches[0]
    if item.get("path") != "/api/v1/" + product:
        raise ClientError("Unexpected product path. No key will be sent to a catalog-supplied destination.")
    price = money(item.get("price"), "catalog price", allow_zero=True)
    amount = item.get("amount")
    if isinstance(amount, bool) or not isinstance(amount, int) or Decimal(amount) != price * 1_000_000:
        raise ClientError("Catalog price and atomic amount disagree.")
    if price > maximum:
        raise ClientError("Catalog price exceeds the local per-purchase limit. No purchase requested.")
    return item, price


@contextlib.contextmanager
def locked_state(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = path.with_name(path.name + ".lock")
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ClientError(f"State file is locked: {lock}. If its process crashed, confirm no client is running before removing only the lock file.") from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink(missing_ok=True)


def write_state(path: Path, state: dict) -> None:
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def validate_receipt(result: dict, expected: Decimal, maximum: Decimal) -> None:
    receipt = result.get("receipt")
    if not isinstance(receipt, dict) or not isinstance(result.get("data"), dict):
        raise ClientError("Response lacks a valid receipt or data object. Retain the state file.")
    if receipt.get("mode") != "sandbox" or receipt.get("settled") is not False:
        raise ClientError("Receipt does not confirm an unsettled sandbox purchase. Stop and review.")
    if money(receipt.get("real_revenue_usdc"), "real revenue", allow_zero=True) != 0:
        raise ClientError("Receipt reports real revenue. This client is for sandbox use only.")
    charged = money(receipt.get("simulated_price_usdc"), "simulated price", allow_zero=True)
    if charged != expected or charged > maximum:
        raise ClientError("Receipt price differs from the checked catalog price or exceeds the local limit. The simulated debit may already exist; do not create a new purchase ID.")
    if not isinstance(receipt.get("id"), str) or not receipt["id"]:
        raise ClientError("Receipt ID is missing. Retain the state file.")


def buy(*, base: str, product: str, key: str, maximum: Decimal, state_path: Path,
        since: str | None = None, timeout: float = 10, attempts: int = 3) -> dict:
    base = base_url(base)
    if product not in PRODUCTS:
        raise ClientError("Unsupported product.")
    if not key.startswith("alp_test_") or any(c.isspace() for c in key):
        raise ClientError("Use an operator-issued alp_test_ agent key, never a wallet private key.")
    if since is not None:
        try:
            valid_date = date.fromisoformat(since).isoformat() == since
        except (ValueError, TypeError):
            valid_date = False
        if product != "changes" or not valid_date:
            raise ClientError("--since accepts an actual YYYY-MM-DD date for changes only.")
    if not 0 < timeout <= 60 or not 1 <= attempts <= 4:
        raise ClientError("Timeout must be within (0, 60] seconds and attempts within 1–4.")
    maximum = money(maximum, "local maximum")
    with locked_state(state_path):
        catalog = request_json(base + "/api/v1/catalog", {}, timeout)
        item, price = quoted_product(catalog, product, maximum)
        binding = {"base_url": base, "product": product, "since": since,
                   "agent_key_sha256": hashlib.sha256(key.encode()).hexdigest()}
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
            except (ValueError, UnicodeDecodeError, OSError):
                raise ClientError("Cannot read purchase state. Do not delete it or generate a new ID while the previous outcome is unknown.") from None
            if not isinstance(state, dict) or state.get("binding") != binding:
                raise ClientError("State belongs to different purchase parameters or credentials. Reuse the original parameters; use a new state file only for a genuinely new purchase.")
            if money(state.get("expected_price_usdc"), "stored price", allow_zero=True) != price:
                raise ClientError("Catalog price changed since this purchase was created. Retain the state and review before retrying.")
            idem = state.get("idempotency_key")
            if not isinstance(idem, str) or not (8 <= len(idem) <= 100) or any(not(c.isascii() and (c.isalnum() or c in "_-")) for c in idem):
                raise ClientError("Stored idempotency key is invalid. Retain the state for review.")
        else:
            state = {"version": 1, "binding": binding, "idempotency_key": uuid.uuid4().hex,
                     "expected_price_usdc": str(price), "status": "pending"}
            write_state(state_path, state)  # Persist before any simulated debit can occur.
        url = base + item["path"]
        if since is not None:
            url += "?" + parse.urlencode({"since": since})
        headers = {"Authorization": "Bearer " + key, "X-AlpNAI-Mode": "sandbox",
                   "Idempotency-Key": state["idempotency_key"]}
        for attempt in range(attempts):
            try:
                result = request_json(url, headers, timeout)
                validate_receipt(result, price, maximum)
                state.update(status="completed", receipt=result["receipt"])
                write_state(state_path, state)
                return result
            except RetryableError:
                if attempt + 1 == attempts:
                    raise
                time.sleep(min(2 ** attempt, 4))
    raise ClientError("Purchase did not complete.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("ALPNAI_BASE_URL", DEFAULT_BASE))
    discovery = parser.add_mutually_exclusive_group()
    discovery.add_argument("--catalog", action="store_true", help="Read the free catalog without an agent key")
    discovery.add_argument("--sample", action="store_true", help="Read the free dated sample without an agent key")
    parser.add_argument("--product", choices=sorted(PRODUCTS), default="snapshot")
    parser.add_argument("--since", help="Date for changes only: YYYY-MM-DD")
    parser.add_argument("--max-usdc", help="Required positive local limit for ONE logical simulated purchase")
    parser.add_argument("--state", type=Path, default=Path(".alpnai/purchase.json"), help="Keep this file when retrying the same purchase")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    try:
        base = base_url(args.base_url)
        if not 0 < args.timeout <= 60:
            raise ClientError("Timeout must be within (0, 60] seconds.")
        if args.catalog or args.sample:
            endpoint = "/api/v1/catalog" if args.catalog else "/api/v1/sample"
            result = request_json(base + endpoint, {}, args.timeout)
        else:
            if args.max_usdc is None:
                raise ClientError("Set --max-usdc explicitly before a simulated purchase.")
            key = os.environ.get("ALPNAI_AGENT_KEY") or getpass.getpass("Operator-issued sandbox agent key: ")
            result = buy(base=base, product=args.product, key=key, maximum=money(args.max_usdc, "local maximum"),
                         state_path=args.state, since=args.since, timeout=args.timeout, attempts=args.attempts)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ClientError, OSError) as exc:
        print(f"AlpNAI: {exc}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("Stopped. Keep the state file for any retry; an interrupted purchase may already have a receipt.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
