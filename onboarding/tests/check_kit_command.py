#!/usr/bin/env python3
"""Verify the existing kit's real audit CLI against a loopback HTTP fixture.

No external requests or account credentials. Run with --kit /path/to/agent-kit.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--kit", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
kit_client = args.kit.resolve() / "examples/audit.py"
if not kit_client.is_file():
    parser.error("The selected kit must contain examples/audit.py.")
expected = json.loads((root / "fixtures/attempts.synthetic.json").read_bytes())
synthetic_key = "alp_test_synthetic_loopback_only"
seen = []
response = {"mode": "free_audit", "payment_required": False, "persisted": False,
            "data": {"purpose": "cost_per_successful_agent_task_audit", "automatic_deployment_authorized": False,
                     "workflows": [{"workflow": "synthetic_extraction", "decision": "collect_more_data",
                                    "automatic_deployment_authorized": False, "realized_savings_usd": None}]}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        seen.append((self.path, self.headers.get("Authorization"), self.headers.get("Content-Type"), json.loads(raw)))
        body = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
thread.start()
try:
    with tempfile.TemporaryDirectory() as directory:
        converted, report = Path(directory) / "input.json", Path(directory) / "report.json"
        imported = subprocess.run([sys.executable, str(root / "csv_to_alpnai.py"), "--input",
                                   str(root / "fixtures/attempts.synthetic.csv"), "--output", str(converted)],
                                  capture_output=True, text=True, timeout=15)
        assert imported.returncode == 0, imported.stderr
        checked = subprocess.run([sys.executable, str(kit_client), "--input", str(converted), "--report", str(report),
                                  "--base-url", f"http://127.0.0.1:{server.server_port}"],
                                 env={**os.environ, "ALPNAI_AGENT_KEY": synthetic_key, "NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"},
                                 capture_output=True, text=True, timeout=15)
        assert checked.returncode == 0, checked.stderr
        assert seen == [("/api/v1/spend-proof", "Bearer " + synthetic_key, "application/json", expected)]
        assert json.loads(report.read_bytes()) == response
        assert synthetic_key not in checked.stdout + checked.stderr
        print("Real kit CLI sent the converted JSON to POST /api/v1/spend-proof and saved the loopback fixture response. No external request.")
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
