# MCP integration notes

Prepared on 14 September 2026. Endpoint: `https://alpnai.com/api/mcp`.

Use an MCP host with Streamable HTTP support. `server.template.json` is a **Registry publication template**, not a universal host configuration file. Its intended namespace is `io.github.fredericmagnathy-ops/alpnai`, with repository `https://github.com/fredericmagnathy-ops/alpnai-agent-kit`. Authenticate as that verified publisher and verify public endpoint access before publication. These assets are prepared, not published by this kit. A private Site's ChatGPT access gate is separate from an ALPNAI test key.

`requests.example.json` shows messages **in order**, not a JSON-RPC batch to send as one body. The prepared ALPNAI server uses the strict `2026-07-28` contract and rejects legacy initialization. This is based on the local application and installed SDK, not a remote availability test. Begin with `server/discover` and confirm that `supportedVersions` contains `2026-07-28`. Do not send `initialize` or `notifications/initialized` to this server.

Send each message as its own HTTP POST with `Content-Type: application/json`, `Accept: application/json, text/event-stream`, `MCP-Protocol-Version: 2026-07-28` and `Mcp-Method` equal to the JSON-RPC method. For `tools/call`, also send `Mcp-Name` equal to the tool name. Every request includes the `_meta` protocol version, client information and client capabilities shown in the file. A full host must support the chosen version and transport; the bounded cloud health check only performs discovery and tool listing.

Inspect `tools/list` and `get_catalog` first. The documented server exposes eight tools: `get_catalog`, `get_free_sample`, the free `audit_agent_costs`, `analyze_agent_latency`, `check_agent_quality`, and the sandbox `purchase_snapshot`, `purchase_changes`, `purchase_evidence`. Purchase tools receive `idempotency_key` in arguments and `Authorization: Bearer <pilot-test-key>` in the HTTP header. Obtain a pilot key through `/start`. `purchase_changes` accepts an optional `since` date. Persist a fresh ID before a new purchase; every retry of that purchase keeps the same ID, key and arguments. The server adapter sets sandbox mode internally.

Purchase tools create simulated receipts and consume the operator-issued test budget. Check the advertised price before calling, then verify `receipt.mode == "sandbox"`, `settled == false`, `real_revenue_usdc == 0` and the expected `simulated_price_usdc`. Inspect `isError` in MCP results. A tool call is not a real payment, a subscription or permission to spend cryptocurrency.

The exact runtime version and application file hashes are recorded in `../contract-provenance.json`. General publication references: [remote Registry entries](https://modelcontextprotocol.io/registry/remote-servers), [publisher authentication](https://modelcontextprotocol.io/registry/authentication).

## Free cost audit

`audit_agent_costs` accepts the same `{runs, config?}` input as `POST /api/v1/spend-proof`. Send an active `Authorization: Bearer <pilot-test-key>` and `Mcp-Name: audit_agent_costs`. It consumes no purchase budget, makes no external model call and persists no report. The example contains only two matched synthetic tasks, so it should request more evidence under the default 30-task threshold. Use `examples/spend-proof.synthetic.json` for a larger explicitly fictional example. Do not supply prompts, customer documents or secrets. The HTTP API returns `{mode:"free_audit",payment_required:false,persisted:false,data:report}`; MCP returns the report as structured content. The old `/mcp` path is not the production endpoint.

## Latency Lab and Quality Gate

`analyze_agent_latency` and `check_agent_quality` accept the same `{runs, config?}` input and active Bearer key as `audit_agent_costs`. Send the selected tool name in both `params.name` and `Mcp-Name`. They perform free calculations without purchases or changes to an agent.

The HTTP equivalents are `POST /api/v1/latency` and `POST /api/v1/quality-gate`; both use the `{mode:"free_audit",payment_required:false,persisted:false,data:report}` envelope. Latency returns `groups` with `p50_ms`, `p95_ms`, `max_ms`, `duration_coverage` and `retry_attempts`. Quality returns `workflows` with comparisons, gates, decisions and success rates.

A recorded task duration is the sum of its attempt durations, not wall time for parallel work. Percentiles use nearest rank and become null if a group's task durations are incomplete. Retry count is attempts minus tasks. No separate failed-retry counter or automatic retry cap is provided. Quality gates use customer-supplied success labels and never authorize deployment.

Guides: [English](../docs/en/mcp.md) · [Français](../docs/fr/mcp.md) · [Deutsch](../docs/de/mcp.md). The existing request fixture still illustrates discovery, a sandbox purchase and a cost audit; selecting either new analysis tool uses the same audit arguments.

These notes document the application contract. Registry assets remain templates, and PayAI/x402 mainnet settlement is under validation. They are not evidence of a Registry listing or a real payment.
