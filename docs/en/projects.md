# ALPNAI Projects — save the evidence behind your agent decisions

Revision: 14 September 2026.

Compare the cost, success rate and latency of two versions before deciding which one to keep. Projects saves aggregate **Spend Proof, Latency Lab and Quality Gate** results in your private account, with JSON downloads and printable reports. Your measurements determine the result; a projection is not a guarantee of savings.

[Open Projects](https://alpnai.com/projects) · [Terms](https://alpnai.com/en/legal/projects) · [Privacy](https://alpnai.com/en/legal/privacy)

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/projects.md) · [English](../en/projects.md) · [Deutsch](../de/projects.md)

## Access and plans

Sign in with ChatGPT. Projects belongs to the authenticated account holder; an agent API key does not unlock its reports or billing. No wallet is required.

| Plan | Price | New saved reports |
|---|---|---|
| Free access | No card | 3 for the lifetime of the account |
| Monthly | 19 CHF, 19 EUR, 19 USD or 19 GBP per month | 100 per paid monthly period |
| Annual | 190 CHF, 190 EUR, 190 USD or 190 GBP per year | 1,200 per paid annual period |

Projects supports 10 projects and at most 2,400 stored reports. Deleting a report does not restore quota; there is no overage billing. CHF, EUR, USD and GBP are separate fixed local prices, not exchange-rate conversions. Stripe displays the tax-inclusive total before confirmation. Subscription availability is shown in Projects.

## Start with your own measurements

1. Sign in, name your project and version, then import the JSON measurements described in the [Spend Proof guide](spend-proof.md).
2. Select **Calculate and save**. Saving sends measurements to ALPNAI for calculation. The database stores aggregate results and labels, not raw attempts or prompts. Include no secrets or personal identifiers.
3. Save another version, select up to two reports and compare. Download the JSON details or a printable report.

## Subscription and invoices

Choose your currency and period, accept Projects terms, then use Stripe checkout. Free access never automatically becomes paid. Paid access starts after confirmed payment; returning from Stripe alone is not proof of payment. Use **Subscription and invoices** to manage billing or stop the next renewal. A failed payment grants no new period. Existing reports remain downloadable after expiry.

This agent kit's API/MCP purchases remain **sandbox only**. Projects subscriptions are a separate website service; the kit neither starts nor renews them and performs no cryptocurrency transfer.

Support: [frederic@alpnor.com](mailto:frederic@alpnor.com).

## Automate report delivery

An agency testing several agents can spend time collecting results. Add one ALPNAI call at the end of your own pipeline: the server calculates cost, latency and quality checks, then saves the result in Projects.

save_project_report calculates and saves a report in the project explicitly authorized by its owner, using the existing Projects allowance. It requires request_id, title and input. Guide: https://alpnai.com/en/docs/projects-automation.

Automatic and manual saves share the three lifetime free reports, or 100 reports per paid monthly period, or 1,200 per paid annual period. There is no overage billing or automatic upgrade to a paid plan.

---

[Your first audit](quickstart.md) · [Spend Proof: cost per success](spend-proof.md)
