#!/usr/bin/env python3
"""Free Spend Proof audit client. Python 3.10+, standard library; no purchases."""
from __future__ import annotations

import argparse
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib import error, parse, request

DEFAULT_BASE = "https://alpnai.com"
MAX_INPUT_BYTES = 512000
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
ENDPOINT = "/api/v1/spend-proof"


class AuditClientError(Exception):
    """Locally defined errors contain no server body, input traces or credentials."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise AuditClientError("Redirect refused; no key or trace data was forwarded.")


def origin(value: str) -> str:
    try:
        p = parse.urlsplit(value)
        p.port
        local = p.hostname in {"127.0.0.1", "localhost", "::1"}
        if (not p.hostname or p.username is not None or p.password is not None
                or p.path not in {"", "/"} or p.query or p.fragment
                or any(c.isspace() for c in value)
                or (p.scheme != "https" and not (local and p.scheme == "http"))):
            raise ValueError
    except (ValueError, TypeError):
        raise AuditClientError("Use an HTTPS origin without credentials, path or query; HTTP is allowed only for loopback tests.") from None
    return value.rstrip("/")


def reject_constant(_value):
    raise ValueError("Non-finite number")


def validate_input(raw: bytes) -> bytes:
    if len(raw) > MAX_INPUT_BYTES:
        raise AuditClientError("Input exceeds the 512000-byte limit.")
    try:
        data = json.loads(raw, parse_constant=reject_constant)
        if not isinstance(data, dict) or set(data) - {"runs", "config"}:
            raise ValueError
        runs = data.get("runs")
        if not isinstance(runs, list) or not 1 <= len(runs) <= 1000:
            raise ValueError
        for row in runs:
            required = {"task_id", "workflow", "variant", "cost_usd", "success"}
            if not isinstance(row, dict) or not required.issubset(row) or set(row) - (required | {"latency_ms"}):
                raise ValueError
            for field, limit in [("task_id", 128), ("workflow", 80)]:
                v = row[field]
                if not isinstance(v, str) or not 1 <= len(v) <= limit or v.strip() != v or any(ord(c) < 32 or ord(c) == 127 for c in v):
                    raise ValueError
            if row["variant"] not in {"baseline", "candidate"} or type(row["success"]) is not bool:
                raise ValueError
            cost = row["cost_usd"]
            if type(cost) not in {int, float} or not math.isfinite(cost) or not 0 <= cost <= 10000:
                raise ValueError
            micro = Decimal(str(cost)) * 1000000
            if micro != micro.to_integral_value():
                raise ValueError
            if "latency_ms" in row and (type(row["latency_ms"]) not in {int, float}
                    or not math.isfinite(row["latency_ms"]) or not 0 <= row["latency_ms"] <= 86400000):
                raise ValueError
        config = data.get("config", {})
        if not isinstance(config, dict) or set(config) - {"minSamples", "minSuccessRate", "maxSuccessRateDrop", "maxP95LatencyMs", "monthlyTasks"}:
            raise ValueError
        limits = {"minSamples": (2, 500, True), "minSuccessRate": (0, 1, False),
                  "maxSuccessRateDrop": (0, 1, False), "maxP95LatencyMs": (0, 86400000000, False),
                  "monthlyTasks": (1, 1000000, True)}
        for key, value in config.items():
            low, high, integer = limits[key]
            if type(value) not in {int, float} or not math.isfinite(value) or not low <= value <= high or (integer and value != int(value)):
                raise ValueError
    except (ValueError, TypeError, UnicodeDecodeError, OverflowError):
        raise AuditClientError("Invalid audit input. Supply only opaque task IDs, workflow, variant, complete costs, success and optional duration/configuration.") from None
    # Preserve exact supplied bytes after validation. No prompts or arbitrary extra fields are accepted.
    return raw


def audit(*, base: str, key: str, raw: bytes, timeout: float = 20, opener=None) -> dict:
    base = origin(base)
    if not isinstance(key, str) or not re.fullmatch(r"alp_test_[A-Za-z0-9_-]{8,256}", key):
        raise AuditClientError("Set an active sandbox agent key in ALPNAI_AGENT_KEY; never supply a wallet key.")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise AuditClientError("Timeout must be within (0, 60] seconds.")
    body = validate_input(raw)
    client = opener or request.build_opener(NoRedirect())
    req = request.Request(base + ENDPOINT, data=body, method="POST", headers={
        "Accept": "application/json", "Content-Type": "application/json",
        "Authorization": "Bearer " + key, "User-Agent": "ALPNAI-Spend-Proof-Kit/0.2.0",
    })
    try:
        with client.open(req, timeout=timeout) as response:
            if response.headers.get_content_type() != "application/json":
                raise AuditClientError("Expected a JSON audit response; no response content was logged.")
            output = response.read(MAX_RESPONSE_BYTES + 1)
    except error.HTTPError as exc:
        code = exc.code
        message = {400: "Invalid audit input.", 401: "An active agent key is required.",
                   403: "Access or origin rejected.", 404: "Audit endpoint unavailable.",
                   413: "Input exceeds the service limit.", 429: "Service rate limit reached.",
                   503: "Audit temporarily unavailable."}.get(code, "Request rejected.")
        raise AuditClientError(f"HTTP {code}: {message}") from None
    except (error.URLError, OSError, TimeoutError):
        raise AuditClientError("Network or TLS failure. No response content was logged.") from None
    if len(output) > MAX_RESPONSE_BYTES:
        raise AuditClientError("Audit response exceeds the local limit.")
    try:
        payload = json.loads(output, parse_constant=reject_constant)
        if (not isinstance(payload, dict) or payload.get("mode") != "free_audit"
                or payload.get("payment_required") is not False or payload.get("persisted") is not False):
            raise ValueError
        report = payload.get("data")
        if (not isinstance(report, dict) or report.get("purpose") != "cost_per_successful_agent_task_audit"
                or report.get("automatic_deployment_authorized") is not False
                or not isinstance(report.get("workflows"), list) or not report["workflows"]):
            raise ValueError
        for workflow in report["workflows"]:
            if (not isinstance(workflow, dict) or workflow.get("automatic_deployment_authorized") is not False
                    or "realized_savings_usd" not in workflow or workflow["realized_savings_usd"] is not None):
                raise ValueError
    except (ValueError, TypeError, UnicodeDecodeError):
        raise AuditClientError("Unexpected audit contract. No payment or deployment authorization was accepted.") from None
    return payload


def write_report(path: Path, report: dict) -> None:
    try:
        encoded = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
    except (OSError, ValueError, TypeError):
        raise AuditClientError("Report could not be saved. Choose a new file in an existing private directory; existing files are never overwritten.") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Private JSON trace export, at most 512000 bytes")
    parser.add_argument("--report", type=Path, required=True, help="New private report file; existing files are never overwritten")
    parser.add_argument("--base-url", default=os.environ.get("ALPNAI_BASE_URL") or DEFAULT_BASE)
    parser.add_argument("--timeout", type=float, default=20)
    args = parser.parse_args()
    try:
        if args.report.exists():
            raise AuditClientError("The report file already exists; choose a new path. No request was sent.")
        with args.input.open("rb") as stream:
            raw = stream.read(MAX_INPUT_BYTES + 1)
        report = audit(base=args.base_url, key=os.environ.get("ALPNAI_AGENT_KEY", ""), raw=raw, timeout=args.timeout)
        write_report(args.report, report)
        print("Audit report saved to the selected local file. No purchase or automatic deployment was requested.")
        return 0
    except AuditClientError as exc:
        print(f"ALPNAI: {exc}", file=sys.stderr)
        return 2
    except OSError:
        print("ALPNAI: Input could not be read. No trace content was logged.", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("Audit interrupted. No purchase was requested.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
