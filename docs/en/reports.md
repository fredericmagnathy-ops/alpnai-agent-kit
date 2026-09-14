# Reports and exports

A readable report for your team and structured JSON for your tools.

[Documentation library](README.md) · [Website documentation](https://alpnai.com/en/docs)

[Français](../fr/reports.md) · [English](../en/reports.md) · [Deutsch](../de/reports.md)

## Choose the right format

JSON preserves metrics, checks, decisions and settings in a reusable format. HTML presents results for reading, sharing or printing.

Files are generated locally from the same calculations. No language-model writing service is needed to generate the report.

## Download your analysis

Run a valid analysis first, then use the module’s JSON or HTML download. The browser saves the file to your device.

For PDF, open the HTML and choose Print, then Save as PDF where your browser supports it. The PDF is produced by your browser, not an external conversion service.

## Read a report from the API

The Spend Proof API returns an envelope containing mode, payment_required, persisted and data. The report is in data. The script below reads the response saved by the API-page example.

It extracts the report into audit-report.json. It adds no generated commentary and sends no information elsewhere.

```python
import json
from pathlib import Path

response = json.loads(Path("audit-response.json").read_text(encoding="utf-8"))
if response.get("error"):
    raise SystemExit(response["error"])
report = response["data"]
for item in report["workflows"]:
    print(item["workflow"], item["decision"])
    print(item["baseline"]["cost_per_successful_task_usd"])
    print(item["candidate"]["cost_per_successful_task_usd"])
Path("audit-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
```

## Keep results interpretable

Keep the dataset provenance and test thresholds. Synthetic examples must remain labeled after export. Protect reports when identifiers reveal information about your business.

Local exports are not invoices or payment evidence. The page does not provide a cloud audit history: save the report before closing your session.

---

[Previous: Quality Gate: compare before changing](quality-gate.md) · [Next: HTTP API](api.md)
