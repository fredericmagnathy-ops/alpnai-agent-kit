#!/usr/bin/env python3
"""Bounded ALPNAI cloud checks. Standard library only; sanitized reports only."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import sys
from urllib import error, parse, request

DEFAULT_BASE = "https://alpnai.com"
HTTP_TIMEOUT = 40
MAX_BODY = 2 * 1024 * 1024
MCP_VERSION = "2026-07-28"
SOURCE_STATUSES = {"baseline", "unchanged", "review_required", "unavailable"}
TOOLS = {"get_catalog", "get_free_sample", "purchase_snapshot", "purchase_changes", "purchase_evidence",
         "audit_agent_costs", "analyze_agent_latency", "check_agent_quality", "save_project_report"}
GROWTH_DECISIONS = {"collect_more_evidence", "improve_activation", "review_repeat_usage"}
RECONCILE_PATH = "/api/operator/payments/reconcile"
MAX_RECONCILE_ORDERS = 5


class CheckError(Exception):
    def __init__(self, code: str, http_status: int | None = None):
        self.code = code
        self.http_status = http_status
        super().__init__(code)


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CheckError("redirect_refused", code)


def validated_origin(value: str) -> str:
    try:
        parsed = parse.urlsplit(value)
        parsed.port
    except ValueError:
        raise CheckError("invalid_base_url") from None
    local = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if (not parsed.hostname or parsed.username is not None or parsed.password is not None
            or parsed.path not in {"", "/"} or parsed.query or parsed.fragment
            or any(c.isspace() for c in value)
            or (parsed.scheme != "https" and not (local and parsed.scheme == "http"))):
        raise CheckError("invalid_base_url")
    return value.rstrip("/")


def secret_value(value: str, required: bool = False) -> str:
    if (required and not value) or (value and (not value.isascii() or any(c.isspace() for c in value))):
        raise CheckError("missing_or_invalid_secret")
    return value


def reconciliation_origin(value: str) -> str:
    """Keep the payment-monitor credential on the production origin or loopback."""
    origin = validated_origin(value)
    if origin != DEFAULT_BASE and parse.urlsplit(origin).hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise CheckError("reconciliation_origin_not_allowed")
    return origin


class HttpClient:
    def __init__(self, base: str, bypass: str = "", timeout: float = HTTP_TIMEOUT):
        self.base = validated_origin(base)
        self.bypass = secret_value(bypass)
        self.timeout = timeout
        self.opener = request.build_opener(NoRedirect())

    def fetch(self, path: str, *, body: dict | None = None, headers: dict | None = None,
              rpc_id: int | None = None) -> tuple[dict, dict]:
        if path not in {"/api/operator/check-sources", "/api/operator/growth", "/api/v1/catalog", "/api/v1/sample", "/api/mcp", RECONCILE_PATH}:
            raise CheckError("endpoint_not_allowed")
        if path == RECONCILE_PATH:
            reconciliation_origin(self.base)
            if body != {"action": "reconcile"}:
                raise CheckError("reconciliation_action_not_allowed")
        request_headers = {"Accept": "application/json", "User-Agent": "ALPNAI-Cloud-Checks/0.1.0"}
        if self.bypass:
            request_headers["OAI-Sites-Authorization"] = "Bearer " + self.bypass
        request_headers.update(headers or {})
        encoded = None
        if body is not None:
            encoded = json.dumps(body).encode("utf-8")
            request_headers["Content-Type"] = "application/json"
        if path == "/api/mcp":
            request_headers["Accept"] = "application/json, text/event-stream"
        req = request.Request(self.base + path, data=encoded, headers=request_headers,
                              method="POST" if body is not None else "GET")
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                status = response.status
                response_headers = dict(response.headers.items())
                content_type = response.headers.get_content_type()
                if content_type not in {"application/json", "text/event-stream"} or (content_type == "text/event-stream" and path != "/api/mcp"):
                    raise CheckError("unexpected_content_type", status)
                raw = response.read(MAX_BODY + 1)
        except error.HTTPError as exc:
            raise CheckError("http_error", exc.code) from None
        except (error.URLError, OSError, socket.timeout, TimeoutError):
            raise CheckError("network_or_tls_error") from None
        if len(raw) > MAX_BODY:
            raise CheckError("response_too_large")
        try:
            text = raw.decode("utf-8")
            if content_type == "application/json":
                payload = json.loads(text)
            else:
                payload = None
                # SSE parsing is limited to this bounded health check, not a full MCP client.
                for event in text.replace("\r\n", "\n").split("\n\n"):
                    data = "\n".join(line[5:].lstrip(" ") for line in event.splitlines() if line.startswith("data:"))
                    if not data:
                        continue
                    message = json.loads(data)
                    if isinstance(message, dict) and message.get("id") == rpc_id:
                        payload = message
                        break
            if not isinstance(payload, dict):
                raise CheckError("invalid_json_contract")
            return payload, response_headers
        except (UnicodeDecodeError, ValueError):
            raise CheckError("invalid_json_contract") from None


def failure(component: str, exc: CheckError) -> dict:
    result = {"component": component, "status": "error", "code": exc.code}
    if exc.http_status is not None:
        result["http_status"] = exc.http_status
    return result


def source_check(client: HttpClient, token: str) -> list[dict]:
    token = secret_value(token, required=True)
    payload, _ = client.fetch("/api/operator/check-sources", body={}, headers={"Authorization": "Bearer " + token})
    if payload.get("claims_auto_updated") is not False:
        raise CheckError("unexpected_claim_update_policy")
    checks = payload.get("checks")
    if not isinstance(checks, list) or not 1 <= len(checks) <= 100:
        raise CheckError("invalid_source_checks")
    counts = {status: 0 for status in sorted(SOURCE_STATUSES)}
    for item in checks:
        if not isinstance(item, dict) or item.get("status") not in SOURCE_STATUSES:
            raise CheckError("invalid_source_status")
        counts[item["status"]] += 1
    # Do not export source IDs, source URLs, notes, account data or raw responses.
    attention = counts["review_required"] > 0 or counts["unavailable"] > 0
    return [{"component": "sources", "status": "attention_required" if attention else "ok",
             "source_count": len(checks), "counts": counts, "claims_auto_updated": False}]


def catalog_check(client: HttpClient) -> dict:
    payload, _ = client.fetch("/api/v1/catalog")
    products = payload.get("products")
    if (payload.get("mode") != "sandbox" or payload.get("live_payments_enabled") is not False
            or payload.get("currency") != "USDC" or not isinstance(products, list)):
        raise CheckError("invalid_sandbox_catalog")
    ids = {p.get("id") for p in products if isinstance(p, dict) and isinstance(p.get("id"), str)}
    if not {"snapshot", "changes", "evidence"}.issubset(ids):
        raise CheckError("missing_catalog_products")
    return {"component": "catalog", "status": "ok", "product_count": len(products)}


def growth_check(client: HttpClient, token: str) -> list[dict]:
    token = secret_value(token, required=True)
    payload, _ = client.fetch("/api/operator/growth", body={}, headers={"Authorization": "Bearer " + token})
    decision, totals = payload.get("decision"), payload.get("totals")
    if (decision not in GROWTH_DECISIONS or not isinstance(totals, dict)
            or payload.get("automatic_price_changes") is not False
            or payload.get("content_changes_require_validation") is not True):
        raise CheckError("invalid_growth_review")
    counts = {}
    for key in ["sessions", "registrations", "activated"]:
        value = totals.get(key)
        if type(value) is not int or not 0 <= value <= 10**12:
            raise CheckError("invalid_growth_totals")
        counts[key] = value
    if type(totals.get("real_revenue_usdc")) not in {int, float} or totals["real_revenue_usdc"] != 0:
        raise CheckError("unexpected_sandbox_revenue")
    counts["real_revenue_usdc"] = 0
    # Export only bounded numeric totals and a locally allowlisted decision, never raw fields.
    return [{"component": "growth", "status": "ok", "decision": decision, "totals": counts,
             "automatic_price_changes": False, "content_changes_require_validation": True}]


def reconciliation_check(client: HttpClient, token: str) -> list[dict]:
    """Recheck existing orders; never ask to quote, authorize, submit or resettle."""
    token = secret_value(token, required=True)
    payload, _ = client.fetch(RECONCILE_PATH, body={"action": "reconcile"},
                              headers={"Authorization": "Bearer " + token})
    if (payload.get("operation") != "read_only_chain_reconciliation"
            or payload.get("payment_operations_called") is not False):
        raise CheckError("invalid_reconciliation_policy")
    orders = payload.get("orders")
    if not isinstance(orders, list) or len(orders) > MAX_RECONCILE_ORDERS:
        raise CheckError("invalid_reconciliation_results")
    confirmed = 0
    for order in orders:
        if not isinstance(order, dict) or type(order.get("confirmed")) is not bool:
            raise CheckError("invalid_reconciliation_results")
        confirmed += int(order["confirmed"])
    # Drop order IDs, clients, addresses, signatures and all unrecognized fields.
    # A non-confirmed item can be pending, unknown or an unsubmitted reservation.
    return [{"component": "reconciliation", "status": "ok",
             "operation": "read_only_chain_reconciliation", "payment_operations_called": False,
             "counts": {"checked": len(orders), "confirmed": confirmed,
                        "not_confirmed": len(orders) - confirmed}}]


def sample_check(client: HttpClient) -> dict:
    payload, _ = client.fetch("/api/v1/sample")
    if (payload.get("mode") != "free_sample" or payload.get("payment_required") is not False
            or not isinstance(payload.get("data"), dict)):
        raise CheckError("invalid_sample_envelope")
    data = payload["data"]
    facts, sources = data.get("facts"), data.get("sources")
    if (not isinstance(data.get("snapshot_id"), str) or not data["snapshot_id"] or not isinstance(facts, list)
            or not isinstance(sources, list) or not facts or not sources):
        raise CheckError("invalid_sample_contract")
    return {"component": "sample", "status": "ok", "fact_count": len(facts), "source_count": len(sources)}


def rpc_result(payload: dict, expected_id: int) -> dict:
    if (payload.get("jsonrpc") != "2.0" or payload.get("id") != expected_id
            or "error" in payload or not isinstance(payload.get("result"), dict)):
        raise CheckError("invalid_mcp_result")
    return payload["result"]


def mcp_check(client: HttpClient) -> dict:
    meta = {"io.modelcontextprotocol/protocolVersion": MCP_VERSION,
            "io.modelcontextprotocol/clientInfo": {"name": "alpnai-cloud-health", "version": "0.1.0"},
            "io.modelcontextprotocol/clientCapabilities": {}}
    headers = {"MCP-Protocol-Version": MCP_VERSION, "Mcp-Method": "server/discover"}
    discovered, _ = client.fetch("/api/mcp", body={"jsonrpc": "2.0", "id": 1,
        "method": "server/discover", "params": {"_meta": meta}}, headers=headers, rpc_id=1)
    result = rpc_result(discovered, 1)
    versions = result.get("supportedVersions")
    if not isinstance(versions, list) or MCP_VERSION not in versions or not isinstance(result.get("capabilities"), dict):
        raise CheckError("unsupported_mcp_version")
    listed, _ = client.fetch("/api/mcp", body={"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                              "params": {"_meta": meta}},
                              headers={**headers, "Mcp-Method": "tools/list"}, rpc_id=2)
    tools = rpc_result(listed, 2).get("tools")
    if not isinstance(tools, list):
        raise CheckError("invalid_mcp_tools")
    names = {t.get("name") for t in tools if isinstance(t, dict) and isinstance(t.get("name"), str)}
    if not TOOLS.issubset(names):
        raise CheckError("missing_mcp_tools")
    return {"component": "mcp", "status": "ok", "tool_count": len(tools), "protocol_version": MCP_VERSION,
            "purchase_tools_called": False}


def run_checks(kind: str, *, base: str, token: str = "", bypass: str = "", client=None) -> dict:
    report = {"schema_version": 1, "kind": kind,
              "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "ok": False, "checks": []}
    try:
        if kind == "reconcile":
            base = reconciliation_origin(base)
        client = client or HttpClient(base, bypass)
        if kind == "sources":
            report["checks"] = source_check(client, token)
        elif kind == "growth":
            report["checks"] = growth_check(client, token)
        elif kind == "reconcile":
            report["checks"] = reconciliation_check(client, token)
        elif kind == "health":
            for name, check in [("catalog", catalog_check), ("sample", sample_check), ("mcp", mcp_check)]:
                try:
                    report["checks"].append(check(client))
                except CheckError as exc:
                    report["checks"].append(failure(name, exc))
        else:
            raise CheckError("unknown_check_kind")
    except CheckError as exc:
        component = "reconciliation" if kind == "reconcile" else kind if kind in {"sources", "growth"} else "configuration"
        report["checks"].append(failure(component, exc))
    report["ok"] = bool(report["checks"]) and all(c["status"] == "ok" for c in report["checks"])
    return report


def write_summary(report: dict) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    # Only locally defined labels and numeric counters enter the job summary.
    lines = ["## ALPNAI cloud check", "", "Result: " + ("passed" if report.get("ok") is True else "attention required"), "",
             "| Component | Status |", "|---|---|"]
    for check in report.get("checks", []):
        component = check.get("component") if check.get("component") in {"sources", "catalog", "sample", "mcp", "growth", "reconciliation", "configuration"} else "unknown"
        status = check.get("status") if check.get("status") in {"ok", "error", "attention_required"} else "error"
        lines.append(f"| {component} | {status} |")
        if check.get("decision") in GROWTH_DECISIONS:
            lines.append("| Growth decision | " + check["decision"] + " |")
        totals = check.get("totals")
        if isinstance(totals, dict):
            for label in ["sessions", "registrations", "activated", "real_revenue_usdc"]:
                count = totals.get(label)
                if type(count) is int and 0 <= count <= 10**12:
                    lines.append(f"| {label} | {count} |")
        counts = check.get("counts")
        if isinstance(counts, dict):
            for label in sorted(SOURCE_STATUSES):
                count = counts.get(label)
                if type(count) is int and 0 <= count <= 100:
                    lines.append(f"| {label} count | {count} |")
            if component == "reconciliation":
                for label in ["checked", "confirmed", "not_confirmed"]:
                    count = counts.get(label)
                    if type(count) is int and 0 <= count <= MAX_RECONCILE_ORDERS:
                        lines.append(f"| {label} orders | {count} |")
    lines += ["", "No purchases, messages or issues were created. Source checks do not automatically update factual claims.",
              "Reconciliation submits no transactions; it may update existing ledger records.", ""]
    with open(path, "a", encoding="utf-8") as stream:
        stream.write("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["sources", "health", "growth", "reconcile", "summary"])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.kind == "summary":
        try:
            report = json.loads(args.report.read_text(encoding="utf-8"))
            if not isinstance(report, dict):
                raise ValueError
            write_summary(report)
            return 0
        except (OSError, ValueError):
            print("No valid sanitized report was produced.", file=sys.stderr)
            return 1
    try:
        report = run_checks(args.kind, base=os.environ.get("ALPNAI_BASE_URL") or DEFAULT_BASE,
                            token=os.environ.get("ALPNAI_MONITOR_TOKEN", ""),
                            bypass=os.environ.get("ALPNAI_SITES_BYPASS", ""))
    except Exception:
        # Never render exceptions that may contain response bodies, headers or secrets.
        report = {"schema_version": 1, "kind": args.kind, "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                  "ok": False, "checks": [{"component": "configuration", "status": "error", "code": "unexpected_check_failure"}]}
    try:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError:
        print("Unable to write the sanitized report.", file=sys.stderr)
        return 1
    print("Cloud check passed." if report["ok"] else "Cloud check requires attention; see the sanitized report.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
