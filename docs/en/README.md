# ALPNAI documentation

From records to a decision you can inspect.

[Website documentation](https://alpnai.com/en/docs) · [Integration kit](../../README.md)

[Français](../fr/README.md) · [English](../en/README.md) · [Deutsch](../de/README.md)

Documentation covers free calculations and the pilot. It claims no directory listing, real sale or successful bank conversion.

## Free tools

[Spend Proof](https://alpnai.com/en/tools/spend-proof) · [Latency Lab](https://alpnai.com/en/tools/latency-lab) · [Quality Gate](https://alpnai.com/en/tools/quality-gate)

All three tools accept the same records. Browser calculation and HTML/JSON exports are local; API/MCP calls send records to the server with an active key. The existing Python audit client remains specific to Spend Proof.

## Get started

| Page | Purpose |
|---|---|
| [Understand ALPNAI](introduction.md) | Compare agents by cost, recorded duration and success on the same tasks. |
| [Your first audit](quickstart.md) | Generate a complete example, run the calculation and retrieve an explained result. |

## Tools

| Page | Purpose |
|---|---|
| [Spend Proof: cost per success](spend-proof.md) | Include failures and retries to compare the cost of recorded outcomes. |
| [Latency Lab: duration and retries](latency.md) | Identify slow tasks and quantify additional attempts using the same records. |
| [Quality Gate: compare before changing](quality-gate.md) | Inspect success, cost and latency before adopting a candidate. |
| [Reports and exports](reports.md) | A readable report for your team and structured JSON for your tools. |

## Integrations

| Page | Purpose |
|---|---|
| [HTTP API](api.md) | Submit records from a script and retrieve the same structured calculation. |
| [Connect an agent with MCP](mcp.md) | Discover tools and call audit_agent_costs with your records. |

## Trust

| Page | Purpose |
|---|---|
| [Payments and test mode](payments.md) | Distinguish free audits, simulated purchases and x402 settlement under validation. |
| [Data and access](security.md) | Prepare minimal records and choose where the calculation runs. |

## Free APIs

| POST | Tool |
|---|---|
| `/api/v1/spend-proof` | Spend Proof |
| `/api/v1/latency` | Latency Lab |
| `/api/v1/quality-gate` | Quality Gate |

[Eight MCP tools](mcp.md)

MCP purchase examples remain in sandbox mode. PayAI/x402 is under validation; this repository proves no mainnet settlement. This kit executes no subscriptions, commissions or automatic bank transfers.
