# HTTP API

Submit records from a script and retrieve the same structured calculation.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/api.md) · [English](../en/api.md) · [Deutsch](../de/api.md)

## Get a key

Open /start, sign in and create test access. The service generates the key; copy it when shown. alp_test_… describes its format, not a value to invent.

Store the key in an ALPNAI_AGENT_KEY environment variable on your machine or server. A wallet address does not replace this key.

## Calculate an audit

Prepare audit.json using the quickstart, then run this request. POST /api/v1/spend-proof expects runs/config JSON and an active key. No payment header is required for this free audit.

The example saves the response as audit-response.json. It reads your environment variable instead of embedding the key in code.

```bash
curl --fail-with-body --silent --show-error \
  'https://alpnai.com/api/v1/spend-proof' \
  --header "Authorization: Bearer ${ALPNAI_AGENT_KEY}" \
  --header 'Content-Type: application/json' \
  --data-binary @audit.json \
  --output audit-response.json
```

## Contract and data size

Limits: 1 to 1,000 attempts, at most 512,000 UTF-8 bytes. An attempt cost ranges from USD 0 to 10,000; a duration from 0 to 86,400,000 ms. Unknown fields and incorrect value types are rejected.

A successful response contains mode:"free_audit", payment_required:false, persisted:false and data. persisted:false means records are not saved in the application database, not that all infrastructure logs are erased.

## Handle errors

400 invalid_audit_input: correct JSON, fields or limits. 401 agent_key_required: check the key and its active state. 403 origin_forbidden: cross-origin browser requests are rejected.

413 body_too_large: reduce the file while retaining complete matched tasks. 503 audit_unavailable: processing failed; use bounded retries. A collect_more_data decision in a 200 response is an analysis result, not an HTTP failure.

## Other available routes

All three free calculations accept the same JSON and key: POST /api/v1/spend-proof, POST /api/v1/latency and POST /api/v1/quality-gate. Replace only the path in the example above to select a calculation.

The latency API returns groups including p50_ms, p95_ms, max_ms and retry_attempts; quality-gate returns workflows with comparison, gates, decision and success rates. GET /openapi.json describes the contract; GET /api/v1/catalog and GET /api/v1/sample are public. HTML export is still generated locally.

---

[Reports and exports](reports.md) · [Connect an agent with MCP](mcp.md)
