# ALPNAI agent integration kit

## TypeScript buyer integration

The [x402 buyer client](clients/x402-buyer/README.md) is now available as source for agents with an existing owner authorization, billing qualification and wallet adapter. It validates the exact quote, preserves the same purchase identity and resumes pending order checks after restart. **Offline validated; live ALPNAI collection is currently closed.** It never opens an account, changes spending permissions or purchases on its own. The Python purchase example below remains sandbox-only.

Inspect an offer without a key: [Snapshot](https://alpnai.com/api/v1/offers/snapshot), [Change Set](https://alpnai.com/api/v1/offers/changes), [Evidence Pack](https://alpnai.com/api/v1/offers/evidence). Each public descriptor gives the catalog price, access requirements, delivery contract and current availability. It is not a payable x402 quotation. Protected purchase errors include an `offer_url` and a `Link: rel="describedby"` to the corresponding descriptor.

Native MCP x402 transport is implemented: signed payloads use params._meta["x402/payment"], and confirmed receipts use result._meta["x402/payment-response"]. See the [MCP guide](docs/en/mcp.md). Commercial USDC collection remains disabled in the live catalogue; this transport update is not a paid launch. The included purchase script still performs sandbox tests only.

Have a CSV export? [Import your own attempts](onboarding/README.md) before your first audit.

[Français](README.fr.md) · [Deutsch](README.de.md)

ALPNAI gives authorized AI agents deterministic **cost, latency and quality analyses**. Compare variants on the same recorded tasks, then deliver a computed report to an owner-authorized project. Start by checking the public example before connecting your own data.

## Evaluate in two GET requests

From this repository directory, run the standalone verifier with **Node.js 18 or later**. No package installation, account, API key or wallet is required.

```sh
node examples/verify-performance-sample.mjs
```

It fetches `GET /api/v1/catalog` and `GET /api/v1/performance-sample`, independently recalculates the supplied example's costs, success counts and recorded P95, and prints `PASS` or `FAIL`. It follows no redirects, sends no credentials and performs no POST, purchase or file write. The example is synthetic: a passing check establishes reproducible arithmetic, not customer savings or a payment.

An autonomous client can read the same [public catalogue](https://alpnai.com/api/v1/catalog) and [performance example](https://alpnai.com/api/v1/performance-sample). The catalogue describes the three free analyses, access requirements and authorized report delivery; the MCP `get_catalog` tool returns the same contract. The [OpenAPI snapshot](openapi.snapshot.json) supplies detailed input/output schemas. The separate `get_free_sample` MCP tool returns dated source evidence, not this performance example.

To use your own measurements, the owner activates an agent key through [/start](https://alpnai.com/start) once. Your agent can then run the free analyses within its permissions. Saving in Projects additionally requires an explicit owner grant. A key does not authorize purchases, upgrades or production changes. [MCP integration](docs/en/mcp.md) · [Report delivery](docs/en/projects-automation.md).

**Status: public service at [alpnai.com](https://alpnai.com/); API/MCP cryptocurrency purchases remain sandbox-only.** The primary MCP endpoint is `/api/mcp`. Obtain an active pilot key through [/start](https://alpnai.com/start). Agent keys do not bypass account permissions; this kit never copies browser sessions.

## ALPNAI Projects

After the owner grants access in Projects, an agent can deliver reports automatically with `save_project_report` (MCP) or the Python client `examples/save_project.py`. Manual and automatic saves share the same allowance. [Setup](docs/en/projects-automation.md).

Save and compare your agent results in a private workspace. [Open Projects](https://alpnai.com/projects) with **Sign in with ChatGPT**: 3 saved reports free, no card. Paid plans are **19 CHF, 19 EUR, 19 USD or 19 GBP monthly** for 100 new reports per paid monthly period, or **190 CHF, 190 EUR, 190 USD or 190 GBP annually** for 1,200 per paid annual period; 10 projects. These are fixed local prices, not exchange-rate conversions. Stripe handles the separate website subscription. Its availability is shown in Projects, and access requires confirmed payment. The kit does not start subscriptions or move cryptocurrency.

[Projects guide](docs/en/projects.md) · [Terms](https://alpnai.com/en/legal/projects) · [Privacy](https://alpnai.com/en/legal/privacy)

## Documentation library

[Website documentation](https://alpnai.com/en/docs) · [Twelve practical guides](docs/en/README.md) · [Payment recovery and receipts](docs/payment-operations.md)

[FR](https://alpnai.com/fr/docs) · [EN](https://alpnai.com/en/docs) · [DE](https://alpnai.com/de/docs)

[Spend Proof](https://alpnai.com/en/tools/spend-proof) · [Latency Lab](https://alpnai.com/tools/latency-lab) · [Quality Gate](https://alpnai.com/tools/quality-gate)

All three tools accept the same records. Browser calculation and HTML/JSON exports are local; API/MCP calls send records to the server with an active key. The existing Python audit client remains specific to Spend Proof.

| Tool | Free APIs | MCP |
|---|---|---|
| Spend Proof | `POST /api/v1/spend-proof` | `audit_agent_costs` |
| Latency Lab | `POST /api/v1/latency` | `analyze_agent_latency` |
| Quality Gate | `POST /api/v1/quality-gate` | `check_agent_quality` |

[Ten MCP tools](docs/en/mcp.md): `get_catalog`, `get_free_sample`, `audit_agent_costs`, `analyze_agent_latency`, `check_agent_quality`, `save_project_report`, `get_order`, `purchase_snapshot`, `purchase_changes`, `purchase_evidence`.

MCP purchase examples remain in sandbox mode. PayAI/x402 is under validation; this repository proves no mainnet settlement. This kit executes no subscriptions, commissions or automatic bank transfers.

## Free Spend Proof audit

Supply `ALPNAI_AGENT_KEY` through your process secret store, then run the client with a private input export and a new local report path. The included file is **synthetic demonstration data**, not customer savings.

```sh
python3 examples/audit.py --input examples/spend-proof.synthetic.json --report reports/my-audit.json
```

Create the local `reports/` directory first, or select another existing private directory. The report is saved with restrictive permissions and never printed. Existing files are not overwritten. The request is a free `POST /api/v1/spend-proof` with an active Bearer key: no payment, simulated-budget debit, provider connection or report persistence on the service. No prompts, responses, customer documents or keys belong in input data.

Each row is an attempt with `task_id`, `workflow`, `variant` (`baseline` or `candidate`), `cost_usd`, `success` and optional `latency_ms`. Include all model, tool and retry costs. At most 1,000 rows and 512,000 UTF-8 bytes; monetary values use at most six decimal places. Matched task IDs, enough distinct tasks and acceptable success rates are required before a conditional opportunity is shown. `monthlyTasks` means launched baseline tasks; projected costs are normalized to the same expected number of successful tasks. Unknown experimental bias prevents automatic deployment. The client refuses redirects, logs no input or raw errors and makes no automatic retry.

This audit measures supplied traces. Paid continuous monitoring, revenue attribution and automatic model routing are not available through the kit. API evidence purchases below remain simulated.

## Evidence sandbox examples

Requires Python 3.10 or later; no packages to install. Run commands from this directory.

```sh
python3 examples/buy.py --catalog
python3 examples/buy.py --sample
```

Obtain a pilot key at [/start](https://alpnai.com/start); the operator sets the available simulated budget. The first purchase command prompts for that agent key without echoing it. For automation, supply `ALPNAI_AGENT_KEY` through your process's secret store. Do not paste keys into code, commands that enter shell history or committed files.

```sh
python3 examples/buy.py --product snapshot --max-usdc 0.01 --state .alpnai/snapshot-001.json
```

Run **the identical command** to retry the same purchase. The state file preserves the purchase ID across process restarts; a successful replay should return the same receipt, with `replayed: true`. Do not delete the state after a timeout. A different product, date or key requires a different state file only when you intend a genuinely new purchase.

```sh
python3 examples/buy.py --product changes --since 2026-06-01 --max-usdc 0.05 --state .alpnai/changes-001.json
python3 examples/buy.py --product evidence --max-usdc 0.25 --state .alpnai/evidence-001.json
```

Set `ALPNAI_BASE_URL` or `--base-url` to an operator-authorized HTTPS origin. HTTP is accepted only for loopback testing. The client refuses redirects and catalog-supplied paths outside its fixed product routes. Default timeout: 10 seconds per network operation; at most 3 purchase attempts. `--timeout` permits up to 60 seconds and `--attempts` up to 4. Each retry keeps the same purchase ID. Retries occur only for temporary network failures or HTTP 429/500/502/503/504.

## What the client checks

Before purchasing, it fetches the live catalog without an agent key and requires `mode: sandbox`, `live_payments_enabled: false`, `currency: USDC` and `network: eip155:8453`. It checks the product path, numeric price, six-decimal atomic amount and your local `--max-usdc` limit. The saved state contains a key hash, parameters, purchase ID and receipt; it does not store the raw key.

The limit applies to **one logical simulated purchase**, not a global allowance across state files. The server separately enforces the agent's total test budget. Catalog checking is not an atomic price reservation: this API has no server-side maximum-price parameter, so a price change between requests could affect the simulated debit. The client rejects a mismatched receipt, preserves state and stops. It is not a production payment safeguard.

A valid sandbox receipt must include `mode: sandbox`, `settled: false`, `real_revenue_usdc: 0` and the expected `simulated_price_usdc`, together with a receipt ID and data object. No wallet private key or recovery phrase is requested. USDC here labels simulated amounts; no cryptocurrency is moved.

## Contract and evidence scope

| Route | Current sandbox contract |
|---|---|
| `GET /api/v1/catalog` | Free product metadata and proposed prices |
| `GET /api/v1/performance-sample` | Public synthetic measurements and calculated performance outputs; no account or payment |
| `GET /api/v1/sample` | Free dated evidence sample |
| `GET /api/v1/snapshot` | 0.01 simulated USDC |
| `GET /api/v1/changes?since=YYYY-MM-DD` | 0.05 simulated USDC; collection events after the date |
| `GET /api/v1/evidence` | 0.25 simulated USDC; evidence and methodology |
| `POST /api/v1/spend-proof` | Free audit with an active Bearer agent key; no payment or server-side report persistence |
| `POST /api/v1/latency` | Free P50/P95, coverage and retry analysis; active key required |
| `POST /api/v1/quality-gate` | Free comparison and success checks; active key required |
| `POST /api/mcp` | Streamable HTTP; see [MCP notes](mcp/README.md) |

Purchase headers are `Authorization: Bearer <test-key>`, `X-ALPNAI-Mode: sandbox` and `Idempotency-Key: <persisted-id>`. IDs contain 8–100 letters, digits, underscores or hyphens. The included [catalog sample](examples/catalog.sample.json) and [OpenAPI snapshot](openapi.snapshot.json) are contract snapshots, not a measurement of current uptime. Provenance is recorded in [contract-provenance.json](contract-provenance.json).

The initial collection is dated 14 September 2026 and concerns OpenAI's confidential draft S-1 announcement of 8 June 2026. It is limited, curated coverage. Change Set filters dated events in that collection; it does not compare arbitrary historical snapshots. Null IPO fields do not establish the absence of later announcements. Source references remain available in the returned data. ALPNAI is independent of OpenAI and does not sell shares, allocations or investment recommendations.

## Prepared cloud monitoring

The public repository is [fredericmagnathy-ops/alpnai-agent-kit](https://github.com/fredericmagnathy-ops/alpnai-agent-kit), with MCP namespace `io.github.fredericmagnathy-ops/alpnai`. This revision is validated offline; inspect GitHub Actions for the latest cloud results.

Three prepared GitHub Actions workflows check sources every six hours at minute 17 UTC, catalog/sample/ten MCP tools daily at 07:43 UTC, and reconcile existing payment records at minutes 06, 16, 26, 36, 46 and 56 of every hour. Reconciliation reads the chain and may update existing ledger records; it never submits a payment, settlement or bank transfer. It exports only checked/confirmed/not-confirmed counts for at most five orders. Each can also be run manually after deployment. The source check records monitoring results, preserves factual claims and fails when review is required or a source is unavailable. Health checks use MCP `server/discover` and `tools/list` with version `2026-07-28`; they never call purchase tools.

Configure the endpoint and authorized secrets, deploy the API and place the workflows on the repository's default branch before activation. Reports contain only statuses and counts, are retained for seven days and produce a job summary. A failed run can trigger GitHub notifications according to account settings. Schedules can be delayed and do not constitute a continuous-service guarantee. Setup, exact variables, permissions and limitations: [Cloud automation](CLOUD_AUTOMATION.md).

The daily workflow also records an aggregate growth diagnosis using a separate authorized step. The active primary domain is `https://alpnai.com`; use this direct origin in `ALPNAI_BASE_URL`.

## Verify locally

```sh
python3 -m unittest discover -s tests -v
node --test tests/performance-sample.test.mjs
```

Tests run solely against in-process mocks or a loopback HTTP server with synthetic data. They cover a response lost after a simulated debit, retries across process state, price ceilings, catalog consistency, mode checks, parameter binding, redirects, HTML sign-in responses and invalid receipts. Cloud tests also verify secret handling, aggregate reports, source-review failures and MCP discovery without purchases. These tests neither check a production deployment nor prove financial facts. No keys or external accounts are required.

Errors 401/403 require reviewing access, revocation or budget; 409 means an ID was reused with different parameters. After a crash, a `.lock` file may remain: confirm no client is running before removing only that lock, while keeping the purchase state. Local state and receipts belong in the ignored `.alpnai/` directory.

## License and contact

The [MIT license](LICENSE) covers Python code only. API data, source documents, trademarks and other assets are outside that grant; consult [service terms](https://alpnai.com/legal) and the original sources. This kit sends no marketing messages and performs no external listings. Integration contact: [frederic@alpnor.com](mailto:frederic@alpnor.com).
