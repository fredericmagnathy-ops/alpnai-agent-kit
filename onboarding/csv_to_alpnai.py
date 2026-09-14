#!/usr/bin/env python3
"""Convert recorded attempt costs from CSV to ALPNAI JSON, entirely offline.

Python 3.10+, standard library only. No prices, token-cost estimates or API calls.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
import io
import json
import math
import os
from pathlib import Path
import re
import sys

REQUIRED = ("task_id", "workflow", "variant", "cost_usd", "success")
OPTIONAL = ("latency_ms", "attempt_id")
FIELDS = REQUIRED + OPTIONAL
MAX_CSV_BYTES = 2 * 1024 * 1024
MAX_JSON_BYTES = 512000
MAX_RUNS = 1000
CONFIG_LIMITS = {
    "minSamples": (2, 500, True),
    "minSuccessRate": (0, 1, False),
    "maxSuccessRateDrop": (0, 1, False),
    "maxP95LatencyMs": (0, 86400000000, False),
    "monthlyTasks": (1, 1000000, True),
}
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


class ImportError(ValueError):
    """Messages identify fields and row numbers without exposing cell values."""


def text_value(value: str, field: str, line: int, limit: int) -> str:
    # The service is JavaScript: its string limits count UTF-16 code units.
    units = len(value.encode("utf-16-le")) // 2
    # JavaScript trim() also treats U+FEFF as whitespace; Python strip() does not.
    if (not 1 <= units <= limit or value != value.strip() or value.startswith("\ufeff") or value.endswith("\ufeff")
            or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ImportError(f"CSV line {line}, {field}: use 1–{limit} characters without controls or surrounding spaces.")
    return value


def number_value(value: str, field: str, line: int, maximum: int) -> int | float:
    value = value.strip()
    try:
        if len(value) > 100 or not NUMBER.fullmatch(value):
            raise ValueError
        decimal = Decimal(value)
        if not decimal.is_finite() or not 0 <= decimal <= maximum:
            raise ValueError
        digits = decimal.as_tuple()
        # Inspect digits without Decimal context rounding even very precise inputs.
        if field == "cost_usd" and digits.exponent < -6 and any(digits.digits[digits.exponent + 6:]):
            raise ImportError(f"CSV line {line}, cost_usd: supply whole micro-USD (at most six decimal places); costs are never rounded.")
        result = float(decimal)
        if not math.isfinite(result) or (decimal != 0 and result == 0):
            raise ValueError
        return int(result) if result.is_integer() else result
    except (InvalidOperation, OverflowError, ValueError) as exc:
        if isinstance(exc, ImportError):
            raise
        raise ImportError(f"CSV line {line}, {field}: supply a finite number from 0 to {maximum} using a decimal point.") from None


def validate_config(config: object, workflows: set[str]) -> dict:
    if not isinstance(config, dict) or set(config) - set(CONFIG_LIMITS):
        raise ImportError("Config must be an object containing only the five documented ALPNAI thresholds/volume fields.")
    for field, value in config.items():
        low, high, integer = CONFIG_LIMITS[field]
        if (type(value) not in {int, float} or not low <= value <= high
                or (integer and value != int(value))):
            raise ImportError(f"Config {field}: supply {'an integer' if integer else 'a number'} from {low} to {high}.")
    if "monthlyTasks" in config and len(workflows) != 1:
        raise ImportError("Config monthlyTasks requires exactly one workflow; import workflows separately.")
    return config.copy()


def convert_csv(raw: bytes, *, delimiter: str = ",", mapping: dict[str, str] | None = None,
                config: dict | None = None) -> tuple[dict, dict]:
    """Return an API input and aggregate import checks. Never infer or merge attempts."""
    if len(raw) > MAX_CSV_BYTES:
        raise ImportError("CSV exceeds the local 2 MiB limit; split complete task sets upstream.")
    if delimiter not in {",", ";", "\t"}:
        raise ImportError("Delimiter must be comma, semicolon, or tab.")
    mapping = mapping or {}
    if set(mapping) - set(FIELDS) or any(not isinstance(v, str) or not v for v in mapping.values()):
        raise ImportError("Mappings must use the documented ALPNAI fields and nonempty CSV column names.")
    sources = {field: mapping.get(field, field) for field in FIELDS}
    if len(set(sources.values())) != len(sources):
        raise ImportError("Each ALPNAI field must map to a different CSV column.")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ImportError("CSV must use UTF-8 encoding; a UTF-8 BOM is accepted.") from None
    # The whole input is bounded already; large ignored export columns are valid.
    previous_field_limit = csv.field_size_limit(MAX_CSV_BYTES)
    reader = csv.reader(io.StringIO(content, newline=""), delimiter=delimiter, strict=True)
    try:
        headers = next(reader, None)
        if not headers or any(not h for h in headers) or len(set(headers)) != len(headers):
            raise ImportError("CSV needs a header with distinct, nonempty column names.")
        for field in REQUIRED:
            if sources[field] not in headers:
                raise ImportError(f"Missing CSV column for {field}; rename the header or use --map.")
        for field in mapping:
            if sources[field] not in headers:
                raise ImportError(f"Mapped CSV column for {field} is missing.")
        indexes = {field: headers.index(source) for field, source in sources.items() if source in headers}
        ignored = len(headers) - len(indexes)
        runs, tasks, workflow_for_task, seen_ids, identical = [], {}, {}, set(), set()
        identical_rows = missing_durations = blank_lines = 0
        for cells in reader:
            line = reader.line_num
            if not cells:
                blank_lines += 1
                continue
            if len(cells) != len(headers):
                raise ImportError(f"CSV line {line}: the number of cells differs from the header; check quoting and delimiter.")
            if len(runs) >= MAX_RUNS:
                raise ImportError("ALPNAI accepts at most 1000 attempts; split complete task sets upstream.")
            row = {field: cells[index] for field, index in indexes.items()}
            task = text_value(row["task_id"], "task_id", line, 128)
            workflow = text_value(row["workflow"], "workflow", line, 80)
            variant = row["variant"]
            if variant not in {"baseline", "candidate"}:
                raise ImportError(f"CSV line {line}, variant: supply baseline or candidate.")
            success = row["success"].strip().lower()
            if success not in {"true", "false", "1", "0"}:
                raise ImportError(f"CSV line {line}, success: supply true/false or 1/0 from your task evaluation.")
            if task in workflow_for_task and workflow_for_task[task] != workflow:
                raise ImportError(f"CSV line {line}, task_id: the same task cannot belong to different workflows.")
            workflow_for_task[task] = workflow
            run = {"task_id": task, "workflow": workflow, "variant": variant,
                   "cost_usd": number_value(row["cost_usd"], "cost_usd", line, 10000),
                   "success": success in {"true", "1"}}
            if row.get("latency_ms", "").strip():
                run["latency_ms"] = number_value(row["latency_ms"], "latency_ms", line, 86400000)
            else:
                missing_durations += 1
            task_key = (workflow, variant, task)
            if "attempt_id" in row:
                attempt = text_value(row["attempt_id"], "attempt_id", line, 256)
                attempt_key = (*task_key, attempt)
                if attempt_key in seen_ids:
                    raise ImportError(f"CSV line {line}, attempt_id: repeated ID within one task and variant; deduplicate the source export.")
                seen_ids.add(attempt_key)
            fingerprint = tuple(run.items())
            if fingerprint in identical:
                identical_rows += 1
            identical.add(fingerprint)
            tasks[task_key] = tasks.get(task_key, 0) + 1
            runs.append(run)
    except csv.Error:
        raise ImportError(f"CSV near line {reader.line_num}: invalid quoting or an oversized cell.") from None
    finally:
        csv.field_size_limit(previous_field_limit)
    if not runs:
        raise ImportError("CSV must include at least one attempt after its header.")
    workflows = set(workflow_for_task.values())
    payload = {"runs": runs}
    if config is not None:
        payload["config"] = validate_config(config, workflows)
    min_samples = payload.get("config", {}).get("minSamples", 30)
    paired = below_minimum = 0
    for workflow in workflows:
        baseline = {t for w, v, t in tasks if w == workflow and v == "baseline"}
        candidate = {t for w, v, t in tasks if w == workflow and v == "candidate"}
        paired += bool(baseline and baseline == candidate)
        below_minimum += min(len(baseline), len(candidate)) < min_samples
    summary = {"attempts": len(runs), "logical_tasks_across_variants": len(tasks),
               "retry_attempts": sum(count - 1 for count in tasks.values()),
               "workflows": len(workflows), "workflows_with_matched_task_sets": paired,
               "workflows_below_minimum_samples": below_minimum,
               "attempts_without_latency": missing_durations,
               "identical_measurement_rows_preserved": identical_rows,
               "ignored_columns": ignored, "blank_lines_skipped": blank_lines}
    return payload, summary


def encode_payload(payload: dict) -> bytes:
    encoded = (json.dumps(payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")
    if len(encoded) > MAX_JSON_BYTES:
        raise ImportError("Output exceeds ALPNAI's 512000-byte limit; split complete task sets upstream.")
    return encoded


def read_bounded(path: Path, maximum: int) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise ImportError(f"Input file exceeds its {maximum}-byte limit.")
    return raw


def no_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ImportError("Config contains duplicate keys.")
        result[key] = value
    return result


def read_config(path: Path) -> dict:
    try:
        value = json.loads(read_bounded(path, 4096), object_pairs_hook=no_duplicates)
        if not isinstance(value, dict):
            raise ValueError
        return value
    except (ValueError, UnicodeDecodeError, RecursionError):
        raise ImportError("Config must be a valid UTF-8 JSON object with unique keys.") from None


def save_new(path: Path, encoded: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="UTF-8 CSV with one row per recorded attempt")
    parser.add_argument("--output", type=Path, required=True, help="New local JSON file in an existing private directory")
    parser.add_argument("--delimiter", choices=[",", ";", "tab"], default=",")
    parser.add_argument("--map", action="append", default=[], metavar="FIELD=COLUMN", help="Map an ALPNAI field to a source header; repeat as needed")
    parser.add_argument("--config", type=Path, help="Optional ALPNAI config JSON object; default service thresholds otherwise")
    args = parser.parse_args()
    try:
        mapping = {}
        for item in args.map:
            field, separator, source = item.partition("=")
            if not separator or field not in FIELDS or not source or field in mapping:
                raise ImportError("Use --map FIELD=COLUMN once per documented ALPNAI field.")
            mapping[field] = source
        if os.path.lexists(args.output):
            raise ImportError("Output already exists; choose a new file. Nothing was overwritten.")
        config = read_config(args.config) if args.config else None
        payload, summary = convert_csv(read_bounded(args.input, MAX_CSV_BYTES),
                                       delimiter="\t" if args.delimiter == "tab" else args.delimiter,
                                       mapping=mapping, config=config)
        encoded = encode_payload(payload)
        save_new(args.output, encoded)
        print("ALPNAI JSON saved locally. No data was transmitted.")
        print(json.dumps(summary, sort_keys=True))
        if summary["identical_measurement_rows_preserved"]:
            print("Check repeated measurements against source attempt IDs; all rows were preserved.")
        if summary["attempts_without_latency"]:
            print("Some durations are missing; affected variants cannot produce a complete recorded P95.")
        if summary["workflows_below_minimum_samples"] or summary["workflows_with_matched_task_sets"] != summary["workflows"]:
            print("Comparison needs matched task IDs and enough distinct tasks per variant; import success is not an audit decision.")
        return 0
    except ImportError as exc:
        print(f"ALPNAI: {exc}", file=sys.stderr)
        return 2
    except OSError:
        print("ALPNAI: Could not read or write the selected file. Choose a new output in an existing private directory.", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print("Import interrupted. No data was transmitted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
