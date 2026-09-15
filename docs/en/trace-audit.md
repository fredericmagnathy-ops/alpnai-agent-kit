# Trace Audit: agent-event costs without an account

Send recorded event costs and explicit whole-task outcomes. Receive exact totals, cost per confirmed success, failed-task costs, repeated-call candidates and evidence-linked next steps.

**Free. No key, wallet, subscription, external model call or server-side input storage.** Unlike the three paired-comparison APIs, this route accepts your own measurements without an agent key.

## Run a real calculation

```sh
python3 examples/trace_audit.py --input examples/trace-events.synthetic.json --report trace-result.json
```

Python 3.10+; standard library only. The example is synthetic, not measured customer savings. The client sends that input to ALPNAI over HTTPS, refuses redirects, does not retry and saves the result to a new private local file. Select a new report path for another run.

If Python reports a certificate error, install the trusted CA bundle for your Python distribution; never disable TLS verification. On macOS installations using the system PEM bundle, set `SSL_CERT_FILE=/etc/ssl/cert.pem` when running the command.

Direct API:

```sh
curl https://alpnai.com/api/v1/trace-audit \
  -H 'Content-Type: application/json' \
  --data-binary @examples/trace-events.synthetic.json
```

`GET https://alpnai.com/api/v1/trace-audit` returns the input example and its calculated result. [Full schema](https://alpnai.com/openapi.json) · [Interactive tool](https://alpnai.com/en/tools/trace-audit).

## Connect an MCP client

Add Streamable HTTP endpoint **https://alpnai.com/api/mcp/public**, with no authentication. It exposes only `get_trace_example` and `audit_agent_trace`. The latter accepts the same JSON input as REST. HTTP JSON and SSE responses must be supported by the client. No private report or payment tools are exposed here.

This is distinct from the main `/api/mcp` endpoint, whose protected operations retain their authorization requirements. A compatible client's custom MCP connection is not a listing or endorsement in ChatGPT or Claude's app directories.

## Data contract

- `events`: 1–1,000 events, total request at most 256,000 UTF-8 bytes.
- Each event: unique opaque `event_id`, `task_id`, `tool`, recorded `cost_usd`; optional `latency_ms` and caller-computed `input_hash`.
- Costs: USD, finite, nonnegative, at most six decimal places. Include all costs represented by each event; do not count the same charge twice.
- `outcomes`: optional array of whole-task verdicts, one per task: `success`, `failed` or `unknown`. An omitted task is unknown. A successful HTTP response is not a business outcome.
- IDs and fingerprints: 1–128 ASCII characters matching `^[A-Za-z0-9_.:@/-]+$`. Never send prompts, answers, secrets or customer documents.

## Read the example

The six example events cost **$0.40**: **$0.16** on successful tasks, **$0.20** on failed tasks and **$0.04** on tasks with unknown outcomes. One task succeeded, so cost per confirmed success is **$0.40**, including failed and unknown costs. One additional matching call cost **$0.04**; it overlaps the failed-task cost and must not be added again.

Repeated calls are review candidates, not proven waste. Validate whether caching or deduplication preserves correctness and authorization before changing an agent. ALPNAI does not deploy changes or claim realized savings. Missing source events cannot be inferred.

Browser calculations stay local. REST/MCP input is processed for that request and not stored as a report; aggregate operational counters contain no event IDs, prompts or input payloads. Private Projects storage is a separate opt-in service and currently saves the paired cost/latency/quality reports. Export this Trace Audit result as JSON.
