"""Offline importer checks; optional integration with the existing agent kit."""
import csv
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("csv_to_alpnai", ROOT / "csv_to_alpnai.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
HEADERS = ["task_id", "workflow", "variant", "cost_usd", "success", "latency_ms"]
ROW = ["task-01", "test_workflow", "baseline", "0.04", "true", "2000"]


def raw_csv(rows=None, headers=None, delimiter=","):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, delimiter=delimiter)
    writer.writerow(HEADERS if headers is None else headers)
    writer.writerows([ROW] if rows is None else rows)
    return buffer.getvalue().encode()


class CsvImportTests(unittest.TestCase):
    def test_synthetic_fixture_preserves_failed_attempts_retries_and_all_costs(self):
        data, summary = client.convert_csv((ROOT / "fixtures/attempts.synthetic.csv").read_bytes())
        self.assertEqual(data, json.loads((ROOT / "fixtures/attempts.synthetic.json").read_bytes()))
        self.assertEqual(len(data["runs"]), 10)
        self.assertEqual(sum(not r["success"] for r in data["runs"]), 4)
        self.assertEqual(summary["retry_attempts"], 2)
        self.assertEqual(summary["logical_tasks_across_variants"], 8)
        self.assertEqual(summary["workflows_with_matched_task_sets"], 1)
        self.assertEqual(summary["workflows_below_minimum_samples"], 1)
        self.assertEqual(summary["attempts_without_latency"], 0)
        self.assertTrue(all("attempt_id" not in row for row in data["runs"]))
        self.assertNotIn("config", data)

    def test_semicolon_export_mapping_ignores_extra_columns_and_retains_retry(self):
        sources = ["job_id", "pipeline", "arm", "measured_usd", "passed", "duration_ms", "request_id"]
        data, summary = client.convert_csv((ROOT / "fixtures/export.synthetic.csv").read_bytes(),
            delimiter=";", mapping=dict(zip(client.FIELDS, sources)))
        self.assertEqual(summary["ignored_columns"], 1)
        self.assertEqual(summary["retry_attempts"], 1)
        self.assertEqual([r["success"] for r in data["runs"]], [True, False, True])
        self.assertNotIn("synthetic ignored cell", client.encode_payload(data).decode())

    def test_bom_crlf_quoted_fields_tab_and_empty_lines(self):
        row = ["opaque,01", 'pipeline "A"', *ROW[2:]]
        for delimiter in [",", ";", "\t"]:
            raw = b"\xef\xbb\xbf" + raw_csv([row], delimiter=delimiter) + b"\r\n"
            data, summary = client.convert_csv(raw, delimiter=delimiter)
            self.assertEqual(data["runs"][0]["task_id"], "opaque,01")
            self.assertEqual(summary["blank_lines_skipped"], 1)

    def test_missing_duration_is_absent_never_zero(self):
        for raw in [raw_csv([[*ROW[:5], ""]]), raw_csv([ROW[:5]], HEADERS[:5])]:
            data, summary = client.convert_csv(raw)
            self.assertNotIn("latency_ms", data["runs"][0])
            self.assertEqual(summary["attempts_without_latency"], 1)

    def test_success_is_explicit_not_python_truthiness(self):
        for value, expected in [("false", False), ("FALSE", False), ("0", False), ("true", True), ("1", True)]:
            row = ROW.copy(); row[4] = value
            data, _ = client.convert_csv(raw_csv([row]))
            self.assertIs(data["runs"][0]["success"], expected)
        for value in ["", "yes", "success", "200", "0.0"]:
            row = ROW.copy(); row[4] = value
            with self.assertRaises(client.ImportError): client.convert_csv(raw_csv([row]))

    def test_missing_cost_never_estimated_or_filled(self):
        row = ROW.copy(); row[3] = ""
        with self.assertRaisesRegex(client.ImportError, "cost_usd"):
            client.convert_csv(raw_csv([row]))
        with self.assertRaisesRegex(client.ImportError, "cost_usd"):
            client.convert_csv(raw_csv([ROW[:3] + ROW[4:]], HEADERS[:3] + HEADERS[4:]))

    def test_money_rejects_fractions_of_micro_usd_without_rounding(self):
        for value in ["0.0000001", "1e-7", "0.12345600000000000000000000000000000000001",
                      "NaN", "Infinity", "-0.01", "10000.000001", "0,04", "USD 0.04"]:
            row = ROW.copy(); row[3] = value
            with self.subTest(value=value), self.assertRaises(client.ImportError):
                client.convert_csv(raw_csv([row]))
        for value, expected in [("0", 0), ("0.000001", 0.000001), ("0.0400000", .04), ("1e-6", .000001), ("10000", 10000)]:
            row = ROW.copy(); row[3] = value
            data, _ = client.convert_csv(raw_csv([row]))
            self.assertEqual(data["runs"][0]["cost_usd"], expected)

    def test_invalid_durations_and_variants_are_rejected(self):
        for column, values in [(5, ["-1", "86400001", "NaN", "Infinity", "1e-999"]), (2, ["Baseline", "test", "", " candidate"])]:
            for value in values:
                row = ROW.copy(); row[column] = value
                with self.subTest(column=column, value=value), self.assertRaises(client.ImportError):
                    client.convert_csv(raw_csv([row]))

    def test_identical_measurements_are_not_silently_deduplicated(self):
        data, summary = client.convert_csv(raw_csv([ROW, ROW]))
        self.assertEqual(len(data["runs"]), 2)
        self.assertEqual(summary["retry_attempts"], 1)
        self.assertEqual(summary["identical_measurement_rows_preserved"], 1)

    def test_attempt_id_detects_duplicates_within_task_variant(self):
        headers = HEADERS + ["attempt_id"]
        for rows in [[ROW + ["1"], ROW + ["1"]], [ROW + [""]]]:
            with self.assertRaisesRegex(client.ImportError, "attempt_id"):
                client.convert_csv(raw_csv(rows, headers))
        data, _ = client.convert_csv(raw_csv([ROW + ["1"], ROW + ["2"]], headers))
        self.assertEqual(len(data["runs"]), 2)
        other = ROW.copy(); other[2] = "candidate"
        client.convert_csv(raw_csv([ROW + ["1"], other + ["1"]], headers))

    def test_cross_workflow_task_id_is_rejected(self):
        other = ROW.copy(); other[1] = "other_workflow"
        with self.assertRaisesRegex(client.ImportError, "different workflows"):
            client.convert_csv(raw_csv([ROW, other]))

    def test_id_limits_follow_javascript_utf16_and_errors_hide_values(self):
        for column, value in [(0, "private-task-marker\n"), (0, "😀" * 65), (1, "x" * 81), (0, " x"), (0, ""),
                              (0, "\ufefftask-1"), (0, "task-1\ufeff"), (1, "\ufeffworkflow"), (1, "workflow\ufeff")]:
            row = ROW.copy(); row[column] = value
            with self.assertRaises(client.ImportError) as caught:
                client.convert_csv(raw_csv([row]))
            self.assertNotIn("private-task-marker", str(caught.exception))
        row = ROW.copy(); row[0] = "😀" * 64
        client.convert_csv(raw_csv([row]))

    def test_large_ignored_cell_within_total_input_limit_is_accepted(self):
        previous = csv.field_size_limit()
        raw = raw_csv([ROW + ["private-long-marker" + "x" * 131073]], HEADERS + ["unused_export_column"])
        data, summary = client.convert_csv(raw)
        self.assertEqual(summary["ignored_columns"], 1)
        self.assertNotIn("private-long-marker", client.encode_payload(data).decode())
        self.assertEqual(csv.field_size_limit(), previous)
        with self.assertRaises(client.ImportError): client.convert_csv(raw_csv([ROW[:-1]]))
        self.assertEqual(csv.field_size_limit(), previous)

    def test_bad_structure_encoding_and_mapping_are_rejected(self):
        values = [b"", raw_csv([]), raw_csv([ROW], HEADERS + ["task_id"]),
                  raw_csv([ROW[:-1]]), raw_csv([ROW + ["extra"]]),
                  b'task_id,workflow,variant,cost_usd,success\n"unclosed', b"\xff"]
        for raw in values:
            with self.subTest(raw=raw), self.assertRaises(client.ImportError): client.convert_csv(raw)
        for mapping in [{"prompt": "other"}, {"task_id": "absent"}, {"task_id": "workflow"}, {"latency_ms": "absent"}]:
            with self.assertRaises(client.ImportError): client.convert_csv(raw_csv(), mapping=mapping)

    def test_input_and_output_size_limits(self):
        client.convert_csv(raw_csv([ROW] * 1000))
        with self.assertRaises(client.ImportError): client.convert_csv(raw_csv([ROW] * 1001))
        with self.assertRaises(client.ImportError): client.convert_csv(b"x" * (client.MAX_CSV_BYTES + 1))
        with self.assertRaises(client.ImportError): client.encode_payload({"runs": ["x" * client.MAX_JSON_BYTES]})

    def test_config_bounds_booleans_unknowns_and_monthly_workflow_scope(self):
        config = {"minSamples": 30, "minSuccessRate": .95, "maxSuccessRateDrop": .02,
                  "maxP95LatencyMs": 3000, "monthlyTasks": 10000}
        data, _ = client.convert_csv(raw_csv(), config=config)
        self.assertEqual(data["config"], config)
        for invalid in [{"minSamples": 1}, {"minSamples": True}, {"minSamples": 2.5},
                        {"minSuccessRate": float("nan")}, {"monthlyTasks": 1000001},
                        {"maxP95LatencyMs": float("inf")}, {"unknown": 1}, []]:
            with self.subTest(config=invalid), self.assertRaises(client.ImportError):
                client.convert_csv(raw_csv(), config=invalid)
        other = ROW.copy(); other[0] = "task-02"; other[1] = "other_workflow"
        with self.assertRaisesRegex(client.ImportError, "exactly one workflow"):
            client.convert_csv(raw_csv([ROW, other]), config={"monthlyTasks": 100})

    def test_cli_creates_private_json_and_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "input.json"
            args = [sys.executable, str(ROOT / "csv_to_alpnai.py"), "--input",
                    str(ROOT / "fixtures/attempts.synthetic.csv"), "--output", str(output)]
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertNotIn("synthetic_extraction", run.stdout + run.stderr)
            self.assertIn('"retry_attempts": 2', run.stdout)
            original = output.read_bytes()
            again = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)
            self.assertEqual(output.read_bytes(), original)

    def test_cli_error_does_not_create_output_or_expose_cell_content(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "bad.csv", Path(directory) / "output.json"
            row = ROW.copy(); row[3] = "private-cost-marker"
            source.write_bytes(raw_csv([row]))
            run = subprocess.run([sys.executable, str(ROOT / "csv_to_alpnai.py"), "--input", str(source), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertFalse(output.exists())
            self.assertNotIn("private-cost-marker", run.stdout + run.stderr)

    def test_documented_mapping_and_config_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "mapped.json"
            args = [sys.executable, str(ROOT / "csv_to_alpnai.py"), "--input", str(ROOT / "fixtures/export.synthetic.csv"),
                    "--output", str(output), "--delimiter", ";", "--config", str(ROOT / "fixtures/config.example.json")]
            for field, source in zip(client.FIELDS, ["job_id", "pipeline", "arm", "measured_usd", "passed", "duration_ms", "request_id"]):
                args.extend(["--map", f"{field}={source}"])
            run = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            data = json.loads(output.read_bytes())
            self.assertEqual(data["config"]["minSamples"], 30)
            self.assertEqual(data["config"]["maxP95LatencyMs"], 3000)
            self.assertEqual(len(data["runs"]), 3)
            self.assertNotIn("synthetic ignored cell", output.read_text())

    def test_config_file_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "config.json"
            source.write_text('{"minSamples":30,"minSamples":2}')
            with self.assertRaises(client.ImportError): client.read_config(source)


if __name__ == "__main__":
    unittest.main()
