# Understand ALPNAI

Compare agents by cost, recorded duration and success on the same tasks.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/introduction.md) · [English](../en/introduction.md) · [Deutsch](../de/introduction.md)

## The question to answer

An agent can become cheaper per call but more expensive per result when it retries or fails. ALPNAI starts from recorded attempts and groups them by task.

Compare a baseline with a candidate. The result helps you decide what to test next.

## Choose your tool

Spend Proof compares cost per successful task. Latency Lab examines P50, P95 and recorded retries. Quality Gate checks thresholds before a limited trial.

All three views use the same record format. Download JSON for an agent and a readable HTML report for your team.

## A simple workflow

Prepare matching task identifiers for both versions. Import full costs, your success labels and durations where available. Analyze, inspect the checks and save the report.

Browser calculation requires no account. The API and MCP require an active ALPNAI key; the audit remains free.

Projects adds private history and comparisons of saved reports. Sign in with ChatGPT to use three free reports or choose a Stripe subscription. This workspace is separate from the free APIs/MCP and crypto purchases in test mode.

## What the measurement means

Results describe the data supplied. ALPNAI does not replace your definition of a good result or modify your agents. A promising candidate still needs testing in your environment.

OpenAI IPO Evidence services are a separate pilot. Their test purchases and simulated budgets are not sales or investments.

## Evaluate from an agent, without an account

GET /api/v1/performance-sample returns a synthetic example’s measurements and the actual computed cost, latency and quality results. No account, wallet or payment is needed for this example.

The REST catalog and MCP get_catalog describe the same analyses, inputs, outputs, prices and access requirements. Activate a key once to analyze your own measurements; your agent can then call the tools without intervention from the ALPNAI operator.

The kit’s verify-performance-sample.mjs fetches the catalog and sample, recalculates the metrics and returns PASS or FAIL. It makes no purchase. A passing check validates the example and arithmetic, not cryptocurrency settlement.

```
GET https://alpnai.com/api/v1/catalog
GET https://alpnai.com/api/v1/performance-sample
```

---

[Your first audit](quickstart.md)
