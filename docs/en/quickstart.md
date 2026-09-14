# Your first audit

Generate a complete example, run the calculation and retrieve an explained result.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/quickstart.md) · [English](../en/quickstart.md) · [Deutsch](../de/quickstart.md)

## 1. Create a demonstration file

The Python script below creates audit.json with 40 tasks per version, or 80 attempts. All data is synthetic. Both versions succeed on the same 39 tasks.

You can also load the demonstration provided in the tool without installing Python.

```python
import json
from pathlib import Path

runs = []
for number in range(1, 41):
    task_id = f"demo-{number:03d}"
    for variant, cost, latency in [
        ("baseline", 0.04, 2200),
        ("candidate", 0.025, 1600),
    ]:
        runs.append({
            "task_id": task_id,
            "workflow": "invoice_fields",
            "variant": variant,
            "cost_usd": cost,
            "success": number != 40,
            "latency_ms": latency,
        })

audit = {"runs": runs, "config": {"maxP95LatencyMs": 3000}}
Path("audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
```

## 2. Analyze the records

Open Spend Proof, load audit.json or paste its contents, then run the analysis. Start with default thresholds; the example adds only a P95 ceiling of 3,000 ms.

For your own data, keep an opaque identifier per task, shared by baseline and candidate. Each additional attempt is a separate row.

## 3. Read the result

The baseline costs USD 1.60 in total; the candidate costs USD 1.00. Each achieves 39 successes out of 40 tasks. Recorded P95 is 2,200 ms and 1,600 ms respectively.

With this synthetic data, the expected decision is candidate_for_controlled_trial. This means a candidate for a controlled trial, not permission to deploy automatically.

## 4. Save and repeat with your data

Download JSON for another application and HTML to read or print the report. Keep the example clearly marked as synthetic.

Repeat with complete costs and success criteria defined before the test. The API page explains how to automate this free calculation.

---

[Understand ALPNAI](introduction.md) · [Projects: private reports and subscriptions](projects.md)
