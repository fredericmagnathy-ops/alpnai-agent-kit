"""Offline audit-client tests; only synthetic data and loopback HTTP."""
from contextlib import redirect_stdout, redirect_stderr
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("audit_client", Path(__file__).parents[1] / "examples" / "audit.py")
client = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(client)
KEY = "alp_test_synthetic_secret_123456"
INPUT = {"runs": [{"task_id": "opaque-1", "workflow": "private-workflow-marker", "variant": "baseline", "cost_usd": 0.01, "success": True}]}
REPORT = {"mode": "free_audit", "payment_required": False, "persisted": False, "data": {
    "purpose": "cost_per_successful_agent_task_audit", "automatic_deployment_authorized": False,
    "workflows": [{"workflow": "private-workflow-marker", "automatic_deployment_authorized": False, "realized_savings_usd": None}]}}


class Response:
    def __init__(self, value, content_type="application/json"):
        self.headers = Message(); self.headers["Content-Type"] = content_type
        self.raw = json.dumps(value).encode() if isinstance(value, dict) else value
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, limit): return self.raw[:limit]


class AuditTests(unittest.TestCase):
    def test_posts_fixed_endpoint_with_key_and_no_payment_headers(self):
        opener = Mock(); opener.open.return_value = Response(REPORT)
        result = client.audit(base=client.DEFAULT_BASE, key=KEY, raw=json.dumps(INPUT).encode(), opener=opener)
        self.assertEqual(result, REPORT)
        req = opener.open.call_args.args[0]
        self.assertEqual(req.full_url, "https://alpnai.com/api/v1/spend-proof")
        self.assertEqual(req.method, "POST")
        self.assertEqual(req.get_header("Authorization"), "Bearer " + KEY)
        self.assertFalse(req.has_header("Payment-signature"))
        self.assertEqual(json.loads(req.data), INPUT)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 20)

    def test_invalid_or_missing_key_never_sends_input(self):
        for key in ["", "0xwalletkey", KEY + "\n", KEY + "\rAuthorization: x"]:
            opener = Mock()
            with self.assertRaises(client.AuditClientError): client.audit(base=client.DEFAULT_BASE, key=key, raw=b"{}", opener=opener)
            opener.open.assert_not_called()

    def test_private_fields_bad_numbers_and_oversized_data_are_rejected(self):
        cases = [b" " * 512001, b'{"runs":[]}', b'{"runs":NaN}', b'{}',
            json.dumps({**INPUT, "prompt": "private"}).encode(),
            json.dumps({"runs": [{**INPUT["runs"][0], "cost_usd": -1}]}).encode(),
            json.dumps({"runs": [{**INPUT["runs"][0], "response": "private"}]}).encode(),
            json.dumps({**INPUT, "config": {"monthlyTasks": 0}}).encode()]
        for raw in cases:
            opener = Mock()
            with self.assertRaises(client.AuditClientError): client.audit(base=client.DEFAULT_BASE, key=KEY, raw=raw, opener=opener)
            opener.open.assert_not_called()

    def test_unexpected_paid_persisted_or_deployment_response_is_rejected(self):
        for payload in [{**REPORT, "payment_required": True}, {**REPORT, "persisted": True},
                        {**REPORT, "data": None}, {**REPORT, "data": {**REPORT["data"], "automatic_deployment_authorized": True}}]:
            opener = Mock(); opener.open.return_value = Response(payload)
            with self.assertRaises(client.AuditClientError): client.audit(base=client.DEFAULT_BASE, key=KEY, raw=json.dumps(INPUT).encode(), opener=opener)

    def test_html_response_and_secret_exception_are_not_rendered(self):
        opener = Mock(); opener.open.return_value = Response(b"private-response", "text/html")
        with self.assertRaises(client.AuditClientError) as caught: client.audit(base=client.DEFAULT_BASE, key=KEY, raw=json.dumps(INPUT).encode(), opener=opener)
        self.assertNotIn("private-response", str(caught.exception))
        opener.open.side_effect = TimeoutError(KEY)
        with self.assertRaises(client.AuditClientError) as caught: client.audit(base=client.DEFAULT_BASE, key=KEY, raw=json.dumps(INPUT).encode(), opener=opener)
        self.assertNotIn(KEY, str(caught.exception))

    def test_refuses_invalid_origins_before_transmitting(self):
        for origin in ["http://example.invalid", "https://user:secret@example.invalid", "https://example.invalid/a", "https://example.invalid?x", "https://example.invalid:bad"]:
            opener = Mock()
            with self.assertRaises(client.AuditClientError): client.audit(base=origin, key=KEY, raw=json.dumps(INPUT).encode(), opener=opener)
            opener.open.assert_not_called()

    def test_redirect_does_not_forward_key_or_trace_body(self):
        requests = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_POST(self):
                requests.append(self.path); self.rfile.read(int(self.headers.get("Content-Length", "0")))
                self.send_response(307); self.send_header("Location", "/not-visited"); self.end_headers()
            def do_GET(self):
                requests.append(self.path); self.send_response(200); self.end_headers()
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True); thread.start()
        try:
            with self.assertRaises(client.AuditClientError): client.audit(base=f"http://127.0.0.1:{server.server_port}", key=KEY, raw=json.dumps(INPUT).encode())
            self.assertEqual(requests, ["/api/v1/spend-proof"])
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_cli_writes_private_selected_report_without_printing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.json"; target = Path(directory) / "report.json"
            source.write_text(json.dumps(INPUT))
            with patch.dict(os.environ, {"ALPNAI_AGENT_KEY": KEY}), patch.object(client.sys, "argv", ["audit.py", "--input", str(source), "--report", str(target)]), patch.object(client, "audit", return_value=REPORT), redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
                self.assertEqual(client.main(), 0)
            self.assertEqual(json.loads(target.read_text()), REPORT)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.assertNotIn(KEY, out.getvalue() + err.getvalue())
            self.assertNotIn("private-workflow-marker", out.getvalue() + err.getvalue())

    def test_existing_report_never_overwritten_or_network_called(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "report.json"; target.write_text("original")
            with patch.object(client.sys, "argv", ["audit.py", "--input", "unused.json", "--report", str(target)]), patch.object(client, "audit") as run, redirect_stderr(io.StringIO()):
                self.assertEqual(client.main(), 2)
            run.assert_not_called(); self.assertEqual(target.read_text(), "original")

    def test_synthetic_example_has_matched_tasks_and_valid_limits(self):
        raw = (Path(__file__).parents[1] / "examples" / "spend-proof.synthetic.json").read_bytes()
        client.validate_input(raw)
        rows = json.loads(raw)["runs"]
        self.assertEqual({r["task_id"] for r in rows if r["variant"] == "baseline"}, {r["task_id"] for r in rows if r["variant"] == "candidate"})
        self.assertGreaterEqual(len(rows), 60)


if __name__ == "__main__": unittest.main()
