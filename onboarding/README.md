# CSV import for ALPNAI

[Français](README.fr.md) · [Deutsch](README.de.md)

Turn recorded attempts into JSON for **Spend Proof, Latency Lab and Quality Gate**. Python 3.10 or later; no dependencies. Conversion runs entirely on your computer, without an account, key or network request.

## Try it in one minute

Run from this directory:

```sh
mkdir -p .alpnai
python3 csv_to_alpnai.py --input fixtures/attempts.synthetic.csv --output .alpnai/example.json
```

The fixture is **synthetic**: 10 attempts, 4 tasks per variant, 2 retries in total, complete recorded durations. The engine calculates USD 0.18 / 0.09 in total costs, 3 successful tasks out of 4 in each variant, and recorded P95 values of 3,200 / 1,800 ms for baseline / candidate. These figures verify the calculation; they are not customer savings. Four tasks per variant leave the default decision at `collect_more_data`.

Then replace `--input` with your export and choose a new output name. Existing files are never overwritten. Only counts and format errors appear in the terminal; the JSON contains your IDs and measurements. New files use permissions `0600` on compatible systems.

## What one row means

**One row = one complete task attempt.** Keep every failed attempt and retry with its own cost and duration. If a task attempt contains several provider calls, aggregate those calls in your telemetry before importing. Do not treat each individual call as a separate task attempt or invent rows from an aggregate retry count.

| Column | Expected value |
|---|---|
| `task_id` | Stable opaque task ID; use the same IDs for both variants. 1–128 UTF-16 code units. |
| `workflow` | Process name, 1–80 UTF-16 code units. A task ID cannot belong to different workflows. |
| `variant` | Exactly `baseline` or `candidate`. |
| `cost_usd` | Complete recorded cost of **this attempt** in USD, including models, tools, retrieval and other calls. From 0 to 10,000 USD, at most six decimal places. |
| `success` | `true` / `false` (case insensitive) or `1` / `0`, based on your evaluation of the task result. An HTTP 200 response does not prove task success. |
| `latency_ms` | Optional: recorded attempt duration in milliseconds, from 0 to 86,400,000. A blank cell remains missing. |
| `attempt_id` | Optional: unique attempt ID within one task and variant, 1–256 UTF-16 code units. Repeated IDs cause an error. This column is excluded from the JSON. |

IDs cannot contain control characters or leading/trailing whitespace. Headers are case sensitive. Other columns are ignored and excluded from the JSON; keep prompts, documents and secrets out of the selected fields.

The converter **does not invent prices, convert currencies or estimate costs from tokens**. If you only have token counts, first supply measured costs from your system. Use a decimal point even in semicolon-separated CSV files. Fractions of a micro-USD are rejected without rounding; aggregate costs correctly upstream.

ALPNAI groups attempts by `workflow`, `variant`, `task_id`. A task succeeds if any attempt succeeds, and every recorded attempt cost counts. P95 uses the sum of recorded attempt durations per task. This sum is not elapsed wall time for parallel operations. A missing duration prevents a complete P95 for the affected variant.

## Map an existing export

`--map FIELD=COLUMN` maps an ALPNAI field to your source header. Quote the whole mapping when a column name contains spaces. This example is ready to run:

```sh
python3 csv_to_alpnai.py --input fixtures/export.synthetic.csv --output .alpnai/mapped-export.json --delimiter ';' --map task_id=job_id --map workflow=pipeline --map variant=arm --map cost_usd=measured_usd --map success=passed --map latency_ms=duration_ms --map attempt_id=request_id
```

Supported delimiters: comma (default), `;`, and `tab`. Input must be UTF-8; a UTF-8 BOM is accepted. Local CSV limit: 2 MiB. ALPNAI limits: 1,000 attempts and 512,000 UTF-8 bytes of JSON. When splitting exports, keep each task's attempts and both variants together in complete task sets.

Without `attempt_id`, identical measurements are preserved and flagged: they might be actual retries or duplicated telemetry. Check the original export. The importer never silently deduplicates them.

## Use the JSON

**Browser:** open [Spend Proof](https://alpnai.com/en/tools/spend-proof), [Latency Lab](https://alpnai.com/en/tools/latency-lab) or [Quality Gate](https://alpnai.com/en/tools/quality-gate) and paste the JSON into the data field. Browser calculations run locally. Saving in Projects is a separate action that transmits data to the service.

**Python kit:** from the root of the [ALPNAI agent kit](https://github.com/fredericmagnathy-ops/alpnai-agent-kit), supply an active key through your process secret manager as `ALPNAI_AGENT_KEY`, then use actual paths for the JSON and a new report:

```sh
python3 examples/audit.py --input /private/path/my-attempts.json --report /private/path/my-report.json
```

This command sends the traces to `POST /api/v1/spend-proof` with Bearer authentication. The audit is free and returns `payment_required:false` and `persisted:false`; it does not save a report in Projects. The other free APIs accept the same JSON: `POST /api/v1/latency` and `POST /api/v1/quality-gate`. The existing `audit.py` client is dedicated to Spend Proof.

A comparison requires matching task IDs, a common success definition and at least 30 distinct tasks per variant by default. A successful import cannot prove complete billing records or an unbiased task sample. It does not authorize automatic deployment.

## Optional thresholds and verification

`--config fixtures/config.example.json` includes the file's explicit thresholds: 30 tasks minimum, 95% minimum success, at most a 2 percentage point success drop, and a 3,000 ms P95 limit. Adjust the latency limit for your use case. Without this option, the JSON omits configuration and the engine uses its defaults. You can add `monthlyTasks` for a single workflow; it means baseline tasks launched per month. Any resulting projection remains conditional.

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

20 offline tests cover values, retries, errors, mappings, limits and files. To verify the kit's actual command, replace the path:

```sh
python3 tests/check_kit_command.py --kit /path/to/alpnai-agent-kit
```

