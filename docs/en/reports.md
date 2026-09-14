# Reports and exports

A readable report for your team and structured JSON for your tools.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/reports.md) · [English](../en/reports.md) · [Deutsch](../de/reports.md)

## Choose the right format

JSON preserves metrics, checks, decisions and settings in a reusable format. HTML presents results for reading, sharing or printing.

In the free browser tools, files are generated locally from the same calculations. Projects also lets you download aggregate results saved to your account. No language-model writing service is needed to generate these reports.

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

Local exports are not invoices or payment evidence. The free browser tools retain no cloud history: download their report before closing the page. To deliberately save analyses online, use Projects with your ChatGPT account.

## Save reports in Projects

Projects stores aggregate results, project/version names and identifiers needed for tracking. Saving a report sends measurements to the server for calculation; raw attempts and prompts are not stored in the database. Local analysis or a free analysis API call does not automatically create a Projects report.

The signed-in account holder can compare up to two reports and download their JSON or a printable report. Existing reports remain downloadable after a subscription ends. Deletion removes content and labels without restoring quota; a fingerprint and technical tracking data remain.

---

[Quality Gate: compare before changing](quality-gate.md) · [HTTP API](api.md)
