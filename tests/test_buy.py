"""Offline loopback contract tests. No AlpNAI account or external requests."""

import copy
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

SPEC = importlib.util.spec_from_file_location("alpnai_buy", Path(__file__).parents[1] / "examples" / "buy.py")
client = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(client)
KEY = "alp_test_contract_fixture_only"


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = Path(self.tmp.name) / "purchase.json"
        self.catalog = {
            "mode": "sandbox", "live_payments_enabled": False, "currency": "USDC", "network": "eip155:8453",
            "products": [{"id": "snapshot", "path": "/api/v1/snapshot", "price": 0.01, "amount": 10000},
                         {"id": "evidence", "path": "/api/v1/evidence", "price": 0.25, "amount": 250000}],
        }
        self.orders, self.calls = {}, []
        self.fail_after_first_debit = False
        self.redirect_catalog = False
        self.html_catalog = False
        self.real_receipt = False
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send_json(self, body, status=200):
                raw = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):
                fixture.calls.append((self.path, self.headers.get("Authorization"), self.headers.get("Idempotency-Key")))
                if self.path == "/api/v1/catalog":
                    if fixture.redirect_catalog:
                        self.send_response(302)
                        self.send_header("Location", fixture.base + "/must-not-visit")
                        self.end_headers()
                    elif fixture.html_catalog:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        self.wfile.write(b"<html>Sign in required</html>")
                    else:
                        self.send_json(fixture.catalog)
                    return
                if self.path not in {"/api/v1/snapshot", "/api/v1/evidence"}:
                    self.send_json({"error": "unexpected_path"}, 404)
                    return
                if self.headers.get("Authorization") != "Bearer " + KEY or self.headers.get("X-AlpNAI-Mode") != "sandbox":
                    self.send_json({"error": "missing_test_authorization"}, 401)
                    return
                idem = self.headers.get("Idempotency-Key")
                if idem in fixture.orders:
                    self.send_json({**fixture.orders[idem], "replayed": True})
                    return
                price = 0.01 if self.path.endswith("snapshot") else 0.25
                result = {"receipt": {"id": "receipt-" + str(len(fixture.orders) + 1), "agent_id": "fixture",
                                      "mode": "sandbox", "settled": fixture.real_receipt,
                                      "real_revenue_usdc": 1 if fixture.real_receipt else 0,
                                      "simulated_price_usdc": price}, "data": {"fixture": True}}
                fixture.orders[idem] = copy.deepcopy(result)
                if fixture.fail_after_first_debit:
                    fixture.fail_after_first_debit = False
                    self.send_json({"error": "response_lost_after_debit"}, 503)
                else:
                    self.send_json(result)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def buy(self, **overrides):
        args = dict(base=self.base, product="snapshot", key=KEY, maximum=Decimal("0.01"),
                    state_path=self.state, timeout=1, attempts=1)
        args.update(overrides)
        return client.buy(**args)

    def test_retries_uncertain_response_without_second_debit(self):
        self.fail_after_first_debit = True
        with self.assertRaises(client.RetryableError):
            self.buy()
        saved_id = json.loads(self.state.read_text())["idempotency_key"]
        result = self.buy()
        self.assertTrue(result["replayed"])
        self.assertEqual(len(self.orders), 1)
        self.assertEqual(set(self.orders), {saved_id})
        self.assertNotIn(KEY, self.state.read_text())

    def test_automatic_retry_reuses_id(self):
        self.fail_after_first_debit = True
        result = self.buy(attempts=2)
        self.assertTrue(result["replayed"])
        self.assertEqual(len(self.orders), 1)

    def test_price_above_local_limit_never_requests_purchase(self):
        with self.assertRaisesRegex(client.ClientError, "local per-purchase limit"):
            self.buy(maximum=Decimal("0.009"))
        self.assertEqual(len(self.orders), 0)
        self.assertEqual(len(self.calls), 1)
        self.assertIsNone(self.calls[0][1])

    def test_catalog_atomic_amount_must_agree_with_price(self):
        self.catalog["products"][0]["amount"] = 10001
        with self.assertRaisesRegex(client.ClientError, "disagree"):
            self.buy()
        self.assertEqual(len(self.orders), 0)

    def test_real_mode_refused_before_purchase(self):
        self.catalog["live_payments_enabled"] = True
        with self.assertRaisesRegex(client.ClientError, "sandbox mode"):
            self.buy()
        self.assertEqual(len(self.orders), 0)

    def test_changed_parameters_do_not_reuse_purchase_id(self):
        self.buy()
        with self.assertRaisesRegex(client.ClientError, "different purchase parameters"):
            self.buy(product="evidence", maximum=Decimal("0.25"))
        self.assertEqual(len(self.orders), 1)

    def test_no_redirect_and_no_credential_disclosure(self):
        self.redirect_catalog = True
        with self.assertRaisesRegex(client.ClientError, "Redirect refused"):
            self.buy()
        self.assertEqual(len(self.calls), 1)
        self.assertIsNone(self.calls[0][1])
        self.assertEqual(len(self.orders), 0)

    def test_html_sign_in_is_not_mistaken_for_api_data(self):
        self.html_catalog = True
        with self.assertRaisesRegex(client.ClientError, "Expected JSON"):
            self.buy()
        self.assertEqual(len(self.orders), 0)

    def test_unexpected_live_receipt_rejected_and_id_retained(self):
        self.real_receipt = True
        with self.assertRaisesRegex(client.ClientError, "unsettled sandbox"):
            self.buy()
        self.assertTrue(self.state.exists())
        self.assertEqual(json.loads(self.state.read_text())["status"], "pending")
        self.assertEqual(len(self.orders), 1)

    def test_catalog_cannot_redirect_authorized_product_request(self):
        self.catalog["products"][0]["path"] = "https://example.invalid/collect-key"
        with self.assertRaisesRegex(client.ClientError, "Unexpected product path"):
            self.buy()
        self.assertEqual(len(self.orders), 0)


if __name__ == "__main__":
    unittest.main()
