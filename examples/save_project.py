#!/usr/bin/env python3
"""Save a computed ALPNAI report through an owner-granted write-only agent. Python 3.10+."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import time
from urllib import error, parse, request
import uuid

# Same input validator as the free audit client shipped beside this file.
from audit import AuditClientError, MAX_INPUT_BYTES, validate_input

DEFAULT_BASE = "https://alpnai.com"
ENDPOINT = "/api/v1/project-reports"
MAX_RESPONSE_BYTES = 16384


class ClientError(Exception):
    """Messages never contain input, provider bodies, or credentials."""


class RetryableError(ClientError):
    """Retain the state: the same UUID must be used when delivery is uncertain."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ClientError("Redirect refused. No credential or measurements were forwarded.")


def origin(value: str, *, allow_loopback: bool = False) -> str:
    try:
        p = parse.urlsplit(value)
        port = p.port
        if p.username is not None or p.password is not None or p.path not in {"", "/"} or p.query or p.fragment or any(c.isspace() for c in value):
            raise ValueError
        canonical = p.scheme == "https" and p.hostname == "alpnai.com" and port in {None, 443}
        loopback = allow_loopback and p.scheme == "http" and p.hostname in {"127.0.0.1", "::1", "localhost"}
        if not canonical and not loopback:
            raise ValueError
    except (TypeError, ValueError):
        raise ClientError("Use https://alpnai.com. A loopback HTTP origin requires --allow-loopback for local tests.") from None
    return DEFAULT_BASE if canonical else value.rstrip("/")


def valid_uuid(value) -> bool:
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value.lower()
    except (ValueError, TypeError, AttributeError):
        return False


@contextlib.contextmanager
def locked_state(path: Path):
    try:
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.is_symlink():
            raise ClientError("State symlinks are refused; use a private regular file.")
        lock = path.with_name(path.name + ".lock")
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise ClientError("This state is locked. If a process crashed, confirm it has stopped before removing only its .lock file.") from None
    except OSError:
        raise ClientError("Unable to lock the private state file. No request was sent.") from None
    try:
        os.close(fd)
        yield
    finally:
        lock.unlink(missing_ok=True)


def state_for(path: Path, fingerprint: str) -> dict:
    if path.exists():
        try:
            fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            with os.fdopen(fd, "rb") as stream:
                info = os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > 4096 or (os.name != "nt" and info.st_mode & 0o077):
                    raise ValueError
                state = json.loads(stream.read(4097))
            if (not isinstance(state, dict) or set(state) != {"version", "request_id", "fingerprint"}
                    or state["version"] != 1 or state["fingerprint"] != fingerprint or not valid_uuid(state["request_id"])):
                raise ValueError
            return state
        except (OSError, ValueError, TypeError, UnicodeDecodeError):
            raise ClientError("State is unreadable, not private, or belongs to different input, title, origin or credentials. Keep it; reuse its original parameters for a retry.") from None
    state = {"version": 1, "request_id": str(uuid.uuid4()), "fingerprint": fingerprint}
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(state, stream, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        # Preserve the UUID before any server quota can be consumed, including process restarts.
        if os.name != "nt":
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    except OSError:
        raise ClientError("Could not persist private request state. No report was submitted.") from None
    finally:
        temporary.unlink(missing_ok=True)
    return state


def send(client, url: str, key: str, body: bytes, timeout: float) -> dict:
    req = request.Request(url, data=body, method="POST", headers={"Accept": "application/json", "Content-Type": "application/json",
                          "Authorization": "Bearer " + key, "User-Agent": "ALPNAI-Projects-Kit/0.1.0"})
    try:
        with client.open(req, timeout=timeout) as response:
            if response.headers.get_content_type() != "application/json":
                raise ClientError("Unexpected response format. Keep the state for a retry; no response content was logged.")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except error.HTTPError as exc:
        code = exc.code
        if code in {429, 500, 502, 503, 504}:
            raise RetryableError(f"HTTP {code}: Temporary service limit or failure. Keep the same state for a retry.") from None
        message = {400: "Invalid report input.", 401: "Use an active ALPNAI agent key.",
                   403: "Owner must enable write-only project access for this key in Projects; revoked keys cannot submit.",
                   404: "Project report endpoint unavailable.", 409: "Report quota or request conflict. Check Projects; keep the same state when retrying.",
                   410: "The original report was deleted; a replay cannot recreate it.", 413: "Report or input exceeds the limit.",
                   415: "JSON content is required."}.get(code, "Request rejected; keep the state.")
        raise ClientError(f"HTTP {code}: {message}") from None
    except (error.URLError, OSError, TimeoutError):
        raise RetryableError("Network or TLS failure. Outcome may be unknown; keep the same state for a retry.") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ClientError("Response exceeds the local limit. Keep the state; no response content was logged.")
    try:
        data = json.loads(raw)
        if (not isinstance(data, dict) or not valid_uuid(data.get("id")) or type(data.get("replayed")) is not bool
                or data.get("saved") is not True or data.get("persistence") != "computed_summary" or data.get("payment_authorized") is not False):
            raise ValueError
    except (ValueError, TypeError, UnicodeDecodeError):
        raise ClientError("Unexpected report confirmation. Keep the state for a retry; no payment authorization was accepted.") from None
    # Whitelist only opaque confirmation fields; arbitrary server data never reaches stdout.
    return {name: data[name] for name in ["id", "replayed", "saved", "persistence", "payment_authorized"]}


def save_project(*, base: str, key: str, raw: bytes, title: str, state_path: Path,
                 timeout: float = 20, attempts: int = 3, allow_loopback: bool = False, opener=None) -> dict:
    base = origin(base, allow_loopback=allow_loopback)
    if not isinstance(key, str) or not re.fullmatch(r"alp_test_[A-Za-z0-9_-]{8,256}", key):
        raise ClientError("Set an active ALPNAI agent key in ALPNAI_AGENT_KEY; never provide a wallet key.")
    if (not isinstance(title, str) or not title.strip() or len(title) > 80
            or re.search(r"[\x00-\x1f\x7f\u202a-\u202e\u2066-\u2069]", title)):
        raise ClientError("Use a report title of 1–80 characters without control characters.")
    if (type(timeout) not in {int, float} or not math.isfinite(timeout) or not 0 < timeout <= 60
            or type(attempts) is not int or not 1 <= attempts <= 4):
        raise ClientError("Use timeout within (0, 60] seconds and 1–4 attempts.")
    try:
        data = json.loads(validate_input(raw))
    except AuditClientError:
        raise ClientError("Invalid measurements. Use the same JSON format as Spend Proof; omit prompts, secrets and extra fields.") from None
    title = title.strip()
    canonical_input = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    fingerprint = hashlib.sha256(json.dumps([base, ENDPOINT, title, canonical_input, hashlib.sha256(key.encode()).hexdigest()],
                                            separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    with locked_state(state_path):
        state = state_for(state_path, fingerprint)
        body = json.dumps({"request_id": state["request_id"], "title": title, "input": json.loads(canonical_input)},
                          sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
        client = opener or request.build_opener(NoRedirect())
        for attempt in range(attempts):
            try:
                return send(client, base + ENDPOINT, key, body, timeout)
            except RetryableError:
                if attempt + 1 == attempts:
                    raise
                time.sleep(min(2 ** attempt, 4))
    raise ClientError("Report confirmation unavailable; keep the same state.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Private measurements JSON; maximum 512000 bytes")
    parser.add_argument("--title", required=True, help="Report version name; no credentials or sensitive text")
    parser.add_argument("--state", type=Path, required=True, help="Private UUID state: reuse this path and original parameters for retries")
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--allow-loopback", action="store_true", help="Permit localhost HTTP only for explicit local testing")
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    try:
        with args.input.open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        result = save_project(base=args.base_url, key=os.environ.get("ALPNAI_AGENT_KEY", ""), raw=raw, title=args.title,
                              state_path=args.state, timeout=args.timeout, attempts=args.attempts, allow_loopback=args.allow_loopback)
        print(json.dumps(result, sort_keys=True))
        return 0
    except ClientError as exc:
        print(f"ALPNAI: {exc}", file=sys.stderr)
        return 2
    except OSError:
        print("ALPNAI: Could not read private input or state. Keep state files for retries.", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("ALPNAI: Interrupted. Keep the state and reuse it: delivery may already have succeeded.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
