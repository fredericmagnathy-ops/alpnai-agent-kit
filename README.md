# AlpNAI agent integration kit

[Français](README.fr.md) · [Deutsch](README.de.md)

Connect an authorized agent to the **AlpNAI sandbox** and inspect a dated, source-linked evidence collection. This standalone kit contains a Python client, MCP message examples and local contract tests. It does not run the server, settle cryptocurrency, create a wallet, renew a subscription or contact prospective customers.

**Status: prepared pilot assets, not published or activated by this kit; no real payments.** The default URL is [alpnai.frederic150452.chatgpt.site](https://alpnai.frederic150452.chatgpt.site/). Site visibility is controlled by its operator. If an endpoint returns a ChatGPT sign-in page, the API is not directly accessible to this client: an agent key does not bypass platform access. Use the operator's documented accessible deployment when available; this kit does not copy browser sessions or circumvent sign-in.

## Quick start

Requires Python 3.10 or later; no packages to install. Run commands from this directory.

```sh
python3 examples/buy.py --catalog
python3 examples/buy.py --sample
```

After deployment, obtain a pilot key at [/start](https://alpnai.frederic150452.chatgpt.site/start); the operator sets the available simulated budget. The first purchase command prompts for that agent key without echoing it. For automation, supply `ALPNAI_AGENT_KEY` through your process's secret store. Do not paste keys into code, commands that enter shell history or committed files.

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
| `GET /api/v1/sample` | Free dated evidence sample |
| `GET /api/v1/snapshot` | 0.01 simulated USDC |
| `GET /api/v1/changes?since=YYYY-MM-DD` | 0.05 simulated USDC; collection events after the date |
| `GET /api/v1/evidence` | 0.25 simulated USDC; evidence and methodology |
| `POST /mcp` | Streamable HTTP; see [MCP notes](mcp/README.md) |

Purchase headers are `Authorization: Bearer <test-key>`, `X-AlpNAI-Mode: sandbox` and `Idempotency-Key: <persisted-id>`. IDs contain 8–100 letters, digits, underscores or hyphens. The included [catalog sample](examples/catalog.sample.json) and [OpenAPI snapshot](openapi.snapshot.json) are prepared contract snapshots, not confirmation that the hosted API is publicly accessible. Provenance is recorded in [contract-provenance.json](contract-provenance.json).

The initial collection is dated 14 September 2026 and concerns OpenAI's confidential draft S-1 announcement of 8 June 2026. It is limited, curated coverage. Change Set filters dated events in that collection; it does not compare arbitrary historical snapshots. Null IPO fields do not establish the absence of later announcements. Source references remain available in the returned data. AlpNAI is independent of OpenAI and does not sell shares, allocations or investment recommendations.

## Prepared cloud monitoring

The intended repository is [fredericmagnathy-ops/alpnai-agent-kit](https://github.com/fredericmagnathy-ops/alpnai-agent-kit), with MCP namespace `io.github.fredericmagnathy-ops/alpnai`. Publication is a separate operator action.

Two prepared GitHub Actions workflows check sources every six hours at minute 17 UTC and catalog/sample/MCP daily at 07:43 UTC. Each can also be run manually after deployment. The source check records monitoring results, preserves factual claims and fails when review is required or a source is unavailable. Health checks use MCP `server/discover` and `tools/list` with version `2026-07-28`; they never call purchase tools.

Configure the endpoint and authorized secrets, deploy the API and place the workflows on the repository's default branch before activation. Reports contain only statuses and counts, are retained for seven days and produce a job summary. A failed run can trigger GitHub notifications according to account settings. Schedules can be delayed and do not constitute a continuous-service guarantee. Setup, exact variables, permissions and limitations: [Cloud automation](CLOUD_AUTOMATION.md).

The daily workflow also records an aggregate growth diagnosis using a separate authorized step. The future primary domain is `https://alpnai.com`; configure `ALPNAI_BASE_URL` once the domain is connected and verified.

## Verify locally

```sh
python3 -m unittest discover -s tests -v
```

Tests run solely against in-process mocks or a loopback HTTP server with synthetic data. They cover a response lost after a simulated debit, retries across process state, price ceilings, catalog consistency, mode checks, parameter binding, redirects, HTML sign-in responses and invalid receipts. Cloud tests also verify secret handling, aggregate reports, source-review failures and MCP discovery without purchases. These tests neither check a production deployment nor prove financial facts. No keys or external accounts are required.

Errors 401/403 require reviewing access, revocation or budget; 409 means an ID was reused with different parameters. After a crash, a `.lock` file may remain: confirm no client is running before removing only that lock, while keeping the purchase state. Local state and receipts belong in the ignored `.alpnai/` directory.

## License and contact

The [MIT license](LICENSE) covers Python code only. API data, source documents, trademarks and other assets are outside that grant; consult [service terms](https://alpnai.frederic150452.chatgpt.site/legal) and the original sources. This kit sends no marketing messages and performs no external listings. Integration contact: [frederic@alpnor.com](mailto:frederic@alpnor.com).
