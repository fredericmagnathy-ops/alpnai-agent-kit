# Automate report delivery

Save a Projects report after each evaluation without a manual upload.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/projects-automation.md) · [English](../en/projects-automation.md) · [Deutsch](../de/projects-automation.md)

## One completed evaluation, one saved report

An agency testing several agents can spend time collecting results. Add one ALPNAI call at the end of your own pipeline: the server calculates cost, latency and quality checks, then saves the result in Projects.

Your team gets private history to compare two versions and download a report. You supply traces and success criteria; ALPNAI does not run the models or change their configuration.

## Authorize a destination once

Sign in at https://alpnai.com/projects with the account that owns the reports. Activate your key at https://alpnai.com/account if needed. Under “Reports delivered by your agent”, choose the project, consent to allowance use and select “Allow report delivery”.

Permission applies to your active agent and one fixed project. It only allows calculating and saving new reports. It cannot read previous reports, delete them, make payments or start subscriptions. “Stop report delivery” revokes access.

## Connect your pipeline

Send POST https://alpnai.com/api/v1/project-reports with Authorization: Bearer and your ALPNAI key. The body contains request_id, title and input. input uses the free tools’ runs/config format. No user_id or project is accepted: the owner grant defines the destination.

With MCP, call save_project_report with the same arguments. Check result.isError. Success returns a report identifier, saved: true and persistence: computed_summary. The account holder can read the content in Projects.

Keep each upload within 1,000 attempts and 500,000 bytes to fit both transports. Send measurements without prompts, secrets or personal data. Raw attempts are not saved in the database; aggregate results, labels and technical identifiers are stored.

Format example with two synthetic attempts, not evidence of savings. Replace measurements and generate a unique identifier for each new report.

```json
{
  "request_id": "e5b67ec8-5d1a-4abe-9e1b-5f358557db82",
  "title": "Evaluation 2026-09-15",
  "input": {
    "runs": [
      {
        "task_id": "synthetic-1",
        "workflow": "support",
        "variant": "baseline",
        "cost_usd": 0.02,
        "success": true,
        "latency_ms": 200
      },
      {
        "task_id": "synthetic-1",
        "workflow": "support",
        "variant": "candidate",
        "cost_usd": 0.01,
        "success": true,
        "latency_ms": 180
      }
    ]
  }
}
```

## Resume without counting twice

Generate and persist a UUID before each new report. After an interruption, reuse exactly the same request_id, title, data and grant. The server returns the same identifier with replayed: true and consumes no additional allowance. Different content with the same identifier is rejected.

Changing project or enabling a new grant creates a new identifier namespace. Finish pending uploads before doing so. A revoked key stops working; after key rotation, update the secret in your pipeline. Do not generate new identifiers to bypass an allowance error.

## Shared allowance, clear costs

Automatic and manual saves share the three lifetime free reports, or 100 reports per paid monthly period, or 1,200 per paid annual period. There is no overage billing or automatic upgrade to a paid plan.

Subscriptions cost 19 CHF, EUR, USD or GBP monthly, or 190 in the same currency annually. The account holder selects and confirms the subscription on the website. When allowance is exhausted, the API refuses a new saved report; free analyses remain available.

## Handle errors

401 agent_key_required: check the active key. 403 project_access_required or project_access_revoked: the owner must check permission. 409 report_limit_reached: check Projects allowance. 409 report_request_conflict: restore the original parameters. 400 invalid_report: check the input format.

After a timeout or temporary unavailability, retry with the same identifier. A deleted report cannot be recreated under the same identifier. Projects terms describe retention and billing in full.

## Ready-to-use Python client

From the repository, provide ALPNAI_AGENT_KEY through your secret manager and use your own measurements. A new state file represents a new report. After an interruption, repeat exactly the same command.

```sh
python3 examples/save_project.py --input private/attempts.json --title "Extraction v2" --state private/extraction-v2-state.json
```

The client saves the identifier and a fingerprint in a private file before sending; it refuses redirects and changed retry parameters. Do not reuse an old command after changing the project grant.

---

[Connect an agent with MCP](mcp.md) · [Projects, payments and test mode](payments.md)
