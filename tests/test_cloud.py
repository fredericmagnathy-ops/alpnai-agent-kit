"""Offline tests for cloud probes, secret handling and sanitized reports."""

from contextlib import redirect_stdout
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("cloud_checks", Path(__file__).parents[1] / "scripts" / "check_cloud.py")
cloud = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cloud)
TOKEN = "synthetic_monitor_secret"
BYPASS = "synthetic_bypass_secret"


class FakeResponse:
    def __init__(self, payload, content_type="application/json", status=200):
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        self.raw = json.dumps(payload).encode() if isinstance(payload, dict) else payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.raw[:limit]


class CloudTests(unittest.TestCase):
    def test_growth_exports_only_aggregate_totals_and_allowed_decision(self):
        client = Mock()
        client.fetch.return_value = ({"decision": "collect_more_evidence", "totals": {
            "sessions": 5, "registrations": 2, "activated": 1, "real_revenue_usdc": 0,
            "private": TOKEN}, "channels": [{"email": "private@example.invalid"}],
            "automatic_price_changes": False, "content_changes_require_validation": True}, {})
        report = cloud.run_checks("growth", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
        self.assertTrue(report["ok"])
        self.assertEqual(report["checks"][0]["decision"], "collect_more_evidence")
        self.assertEqual(set(report["checks"][0]["totals"]), {"sessions", "registrations", "activated", "real_revenue_usdc"})
        self.assertNotIn(TOKEN, json.dumps(report))
        self.assertNotIn("private@example.invalid", json.dumps(report))
        self.assertEqual(client.fetch.call_args.args[0], "/api/operator/growth")
        self.assertEqual(client.fetch.call_args.kwargs["headers"]["Authorization"], "Bearer " + TOKEN)

    def test_growth_rejects_unknown_decision_and_unsafe_totals(self):
        valid = {"decision": "improve_activation", "totals": {
            "sessions": 201, "registrations": 21, "activated": 1, "real_revenue_usdc": 0},
            "automatic_price_changes": False, "content_changes_require_validation": True}
        for payload in [{**valid, "decision": TOKEN}, {**valid, "totals": {**valid["totals"], "sessions": TOKEN}},
                        {**valid, "totals": {**valid["totals"], "real_revenue_usdc": 1}}]:
            client = Mock()
            client.fetch.return_value = (payload, {})
            report = cloud.run_checks("growth", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
            self.assertFalse(report["ok"])
            self.assertNotIn(TOKEN, json.dumps(report))

    def test_growth_without_token_makes_no_request(self):
        client = Mock()
        report = cloud.run_checks("growth", base=cloud.DEFAULT_BASE, client=client)
        self.assertFalse(report["ok"])
        client.fetch.assert_not_called()

    def test_sources_drop_notes_source_ids_and_personal_fields(self):
        client = Mock()
        client.fetch.return_value = ({"claims_auto_updated": False, "checks": [
            {"source_id": "private@example.invalid", "status": "baseline", "note": TOKEN},
            {"source_id": BYPASS, "status": "unchanged", "note": "private@example.invalid"},
        ]}, {})
        report = cloud.run_checks("sources", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
        self.assertTrue(report["ok"])
        self.assertEqual(report["checks"][0]["counts"]["baseline"], 1)
        encoded = json.dumps(report)
        self.assertNotIn(TOKEN, encoded)
        self.assertNotIn(BYPASS, encoded)
        self.assertNotIn("private@example.invalid", encoded)
        self.assertEqual(client.fetch.call_args.kwargs["headers"]["Authorization"], "Bearer " + TOKEN)

    def test_review_and_unavailable_both_fail_the_report(self):
        for status in ["review_required", "unavailable"]:
            client = Mock()
            client.fetch.return_value = ({"claims_auto_updated": False, "checks": [{"status": status}]}, {})
            report = cloud.run_checks("sources", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
            self.assertFalse(report["ok"])
            self.assertEqual(report["checks"][0]["status"], "attention_required")

    def test_missing_monitor_token_makes_no_request(self):
        client = Mock()
        report = cloud.run_checks("sources", base=cloud.DEFAULT_BASE, client=client)
        self.assertFalse(report["ok"])
        client.fetch.assert_not_called()

    def test_unknown_source_status_never_enters_report(self):
        client = Mock()
        client.fetch.return_value = ({"claims_auto_updated": False, "checks": [{"status": TOKEN}]}, {})
        report = cloud.run_checks("sources", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
        self.assertFalse(report["ok"])
        self.assertNotIn(TOKEN, json.dumps(report))

    def test_health_checks_never_call_purchase_tools_or_send_monitor_token(self):
        client = Mock()
        client.fetch.side_effect = [
            ({"mode": "sandbox", "live_payments_enabled": False, "currency": "USDC",
              "products": [{"id": p} for p in ["snapshot", "changes", "evidence"]]}, {}),
            ({"mode": "free_sample", "payment_required": False, "data": {"snapshot_id": "synthetic", "facts": [{"private": TOKEN}], "sources": [{"private": BYPASS}]}}, {}),
            ({"jsonrpc": "2.0", "id": 1, "result": {"supportedVersions": [cloud.MCP_VERSION], "capabilities": {}}}, {}),
            ({"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": tool} for tool in cloud.TOOLS]}}, {}),
        ]
        report = cloud.run_checks("health", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
        self.assertTrue(report["ok"])
        self.assertNotIn(TOKEN, json.dumps(report))
        self.assertNotIn(BYPASS, json.dumps(report))
        for call in client.fetch.call_args_list:
            self.assertNotIn("Authorization", call.kwargs.get("headers", {}))
            body = call.kwargs.get("body", {})
            self.assertNotEqual(body.get("method"), "tools/call")
        mcp_calls = [call for call in client.fetch.call_args_list if call.args[0] == "/api/mcp"]
        self.assertEqual([call.kwargs["body"]["method"] for call in mcp_calls], ["server/discover", "tools/list"])
        for call in mcp_calls:
            self.assertEqual(call.kwargs["headers"]["Mcp-Method"], call.kwargs["body"]["method"])
            self.assertEqual(call.kwargs["headers"]["MCP-Protocol-Version"], "2026-07-28")
            self.assertEqual(call.kwargs["body"]["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"], "2026-07-28")

    def test_http_sends_bypass_and_monitor_headers_with_timeout_40(self):
        client = cloud.HttpClient(cloud.DEFAULT_BASE, BYPASS)
        client.opener = Mock()
        client.opener.open.return_value = FakeResponse({"checks": []})
        client.fetch("/api/operator/check-sources", body={}, headers={"Authorization": "Bearer " + TOKEN})
        call = client.opener.open.call_args
        req = call.args[0]
        headers = {k.lower(): v for k, v in req.header_items()}
        self.assertEqual(headers["authorization"], "Bearer " + TOKEN)
        self.assertEqual(headers["oai-sites-authorization"], "Bearer " + BYPASS)
        self.assertEqual(call.kwargs["timeout"], 40)
        self.assertEqual(req.method, "POST")

    def test_sample_accepts_real_envelope_shape_and_exports_only_counts(self):
        client = Mock()
        client.fetch.return_value = ({"mode": "free_sample", "payment_required": False,
            "data": {"snapshot_id": "synthetic-2026-09-14", "facts": [{"value": TOKEN}],
                     "sources": [{"url": "https://example.invalid/source"}]}}, {})
        self.assertEqual(cloud.sample_check(client), {"component": "sample", "status": "ok", "fact_count": 1, "source_count": 1})

    def test_sample_rejects_missing_or_invalid_envelope_and_data(self):
        data = {"snapshot_id": "synthetic", "facts": [{}], "sources": [{}]}
        valid = {"mode": "free_sample", "payment_required": False, "data": data}
        for payload in [data, {"mode": "free_sample", "payment_required": False},
                        {**valid, "data": None}, {**valid, "data": []}, {**valid, "data": {}},
                        {**valid, "payment_required": True}, {**valid, "payment_required": 0},
                        {**valid, "mode": "paid"}, {**valid, "data": {**data, "facts": []}}]:
            with self.subTest(payload=payload):
                client = Mock(); client.fetch.return_value = (payload, {})
                with self.assertRaises(cloud.CheckError): cloud.sample_check(client)

    def test_mcp_requires_free_audit_tool_without_invoking_it(self):
        client = Mock()
        client.fetch.side_effect = [
            ({"jsonrpc": "2.0", "id": 1, "result": {"supportedVersions": [cloud.MCP_VERSION], "capabilities": {}}}, {}),
            ({"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": name} for name in cloud.TOOLS - {"audit_agent_costs"}]}}, {}),
        ]
        with self.assertRaises(cloud.CheckError) as caught: cloud.mcp_check(client)
        self.assertEqual(caught.exception.code, "missing_mcp_tools")

    def test_mcp_unsupported_version_stops_before_tools_list(self):
        client = Mock()
        client.fetch.return_value = ({"jsonrpc": "2.0", "id": 1,
            "result": {"supportedVersions": ["2025-11-25"], "capabilities": {}}}, {})
        with self.assertRaises(cloud.CheckError) as caught:
            cloud.mcp_check(client)
        self.assertEqual(caught.exception.code, "unsupported_mcp_version")
        self.assertEqual(client.fetch.call_count, 1)

    def test_timeout_error_message_is_not_exported(self):
        client = cloud.HttpClient(cloud.DEFAULT_BASE)
        client.opener = Mock()
        client.opener.open.side_effect = TimeoutError(TOKEN)
        report = cloud.run_checks("sources", base=cloud.DEFAULT_BASE, token=TOKEN, client=client)
        self.assertFalse(report["ok"])
        self.assertEqual(report["checks"][0]["code"], "network_or_tls_error")
        self.assertNotIn(TOKEN, json.dumps(report))

    def test_sse_response_is_matched_to_json_rpc_id(self):
        client = cloud.HttpClient(cloud.DEFAULT_BASE)
        client.opener = Mock()
        body = b'event: message\ndata: {"jsonrpc":"2.0","id":2,"result":{"tools":[]}}\n\n'
        client.opener.open.return_value = FakeResponse(body, "text/event-stream")
        result, _ = client.fetch("/api/mcp", body={"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, rpc_id=2)
        self.assertEqual(result["id"], 2)

    def test_redirect_never_forwards_either_secret(self):
        calls = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                calls.append(self.path)
                self.send_response(302)
                self.send_header("Location", "/must-not-visit")
                self.end_headers()

            def do_GET(self):
                calls.append(self.path)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{}')

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            report = cloud.run_checks("sources", base=base, token=TOKEN, bypass=BYPASS)
            self.assertFalse(report["ok"])
            self.assertEqual(report["checks"][0]["code"], "redirect_refused")
            self.assertEqual(calls, ["/api/operator/check-sources"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_cli_writes_report_and_returns_nonzero_without_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            with patch.dict(os.environ, {"ALPNAI_MONITOR_TOKEN": "", "ALPNAI_SITES_BYPASS": ""}), \
                    patch.object(cloud.sys, "argv", ["check_cloud.py", "sources", "--report", str(path)]), \
                    redirect_stdout(io.StringIO()) as captured:
                code = cloud.main()
            self.assertEqual(code, 1)
            self.assertFalse(json.loads(path.read_text())["ok"])
            self.assertNotIn(TOKEN, captured.getvalue())

    def test_summary_accepts_only_local_labels_and_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.md"
            with patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(path)}):
                cloud.write_summary({"ok": False, "checks": [{"component": TOKEN, "status": BYPASS,
                    "note": "private@example.invalid", "counts": {"review_required": 1}}]})
            text = path.read_text()
            for secret in [TOKEN, BYPASS, "private@example.invalid"]:
                self.assertNotIn(secret, text)


if __name__ == "__main__":
    unittest.main()
