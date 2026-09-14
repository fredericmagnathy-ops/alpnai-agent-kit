# ALPNAI payment operations

This page describes the prepared quotation, recovery and reporting controls. Commercial payment gates remain off. No billing review has been issued, and a review-approval workflow is not available. Publishing documentation or running a monitor does not enable commercial payments or prove a real purchase. Availability depends on the deployed service configuration and verified operation of the payment path.

## Before a payable quotation

The prepared purchase path requires an active purchasing mandate and a current approved billing-review record tied to the owner's profile revision and terms version. A self-declared address or tax identifier is not that review. Missing or invalid billing review returns HTTP `503` with `error: "billing_review_required"` and `payment_required: false`, before a facilitator operation or x402 challenge. With commercial gates off, `commercial_activation_pending` is returned instead. Neither response asks the customer to pay.

Before a payable challenge can be returned, the service stores an immutable billing snapshot alongside the result and technical payment requirements. It contains seller and customer details, terms, reviewed pricing and an integrity hash. Internal review references stay server-side. Agent and SDK responses receive monetary and terms summaries without the customer's billing details. See [billing quotations](billing-quotations.md) for private viewing and export.

The prepared arithmetic keeps the catalog amount as the total; a configured tax component is included in that amount rather than added to it. This calculation does not decide which tax treatment applies. The exact total must match the x402 request and reserved budget.

## One order, one payment attempt

The service freezes the commercial result and billing snapshot before issuing its payment challenge. The saved snapshot and approved review are checked again before further provider operations, and the reviewed context is checked when budget is reserved and settlement is claimed. A quote is not revenue or a pending transfer. A verified authorization can reserve its permitted budget; only one worker can claim the settlement attempt. Repeating the same accepted purchase follows the existing order. It must not create a second payment attempt.

If a provider times out or confirmation is uncertain, the order remains under review. Keep the original order and idempotency identifier. Do not send another payment or replace the identifier to bypass a pending result.

## Recovery after a delay

Reconciliation reads blockchain evidence; it never sends a transaction or calls the facilitator to settle again. Each authorized pass examines at most five unresolved orders, oldest reviewed first. Updating each reviewed order's timestamp lets later passes reach the rest of the backlog.

For an order without a known transaction hash, the service searches finalized USDC authorization logs from its recorded starting block or persisted scan cursor. Each pass covers one inclusive page of at most **2,000 blocks**. When that page contains no matching authorization, the cursor advances to the following block. Its guarded database update prevents an overlapping worker from overwriting newer progress. A failure leaves the page available for a later attempt.

This replaces a fixed total lookback cutoff: delayed orders can be resumed through successive pages. A large backlog still needs multiple passes. Recovery time depends on the backlog, chain finality, RPC availability and successful scheduled execution; it is not an instant-delivery promise. An existing transaction hash avoids the log search but still requires the full confirmation checks.

The initial proof decoder supports direct USDC authorization calls. It verifies the token, payer, recipient, amount, nonce, successful receipt and finalized block. Batch or proxy calls that it cannot prove remain unresolved; they are not guessed to be successful. An expired or revoked reservation can be released only if no settlement attempt was claimed. Reconciliation does not cancel an uncertain submitted payment or refund it automatically.

## Delivery follows confirmation

The confirmed settlement must be recorded successfully before the purchased result and payment receipt are delivered. A payment challenge or unresolved response does not include the commercial payload. An unresolved lookup returns HTTP `202`; cancellation before submission returns `409`. Database or malformed-record failures do not become a fabricated success.

A read-only quotation lookup returns HTTP `200` with `status: "quoted"`, `settled: false` and `payment_required: false`. Viewing or downloading that document does not submit a payment. After confirmed settlement, the payment receipt can include the frozen quotation; the account owner sees the customer copy while the agent sees its limited summary. The receipt records the ledger confirmation time separately from order creation. It is a payment receipt, not a tax invoice. No invoice-issuance workflow is implemented by this feature.

Agents can check their own order through `GET /api/v1/orders/{id}` with their agent authentication. Signed-in customers can use `GET /api/account/orders/{id}`; ownership comes from the authenticated account, not a submitted customer identifier. The account's commercial receipt view is restricted to Base mainnet orders with a matching mandate and agent. Responses are private and not cacheable.

The prepared [printable payment receipt](payment-receipts.md) is available through `GET /api/account/orders/{id}/receipt?lang=fr`, with `en` and `de` also supported. It requires the signed-in owner and a settled order whose saved receipt, result hash and any frozen billing snapshot pass validation. It reads historical order data rather than today's profile, terms or billing review. Historical orders without a snapshot receive a minimal payment record; missing customer or tax details are not invented. Printing or saving as PDF uses the browser's Print command; the server returns HTML, not a PDF file. This read does not call a payment provider or submit a transaction.

## What the dashboard counts

Commercial aggregates count only settled Base mainnet orders. Pending orders, quotes, Sepolia tests and sandbox purchases do not increase real revenue. The account lists quotations separately from pending and completed payments. Paying customers are distinct authenticated account owners, not transaction counts or unique wallet addresses. Commercial order lists expose a small set of metadata; the transaction hash is shown only after settlement.

USDC totals are gross settled receipts. They are not net profit, a bank balance, a fiat conversion or recurring subscription revenue. Fees, refunds, taxes and bank conversion require their own accounting. A statistics read failure must appear as unavailable rather than a new zero balance.

## Scheduled checks

The reconciliation workflow is **scheduled** for minutes 06, 16, 26, 36, 46 and 56 of each hour, and supports manual dispatch. The configuration does not prove that every scheduled execution occurs. Its fixed request is `POST /api/operator/payments/reconcile` with `{"action":"reconcile"}`. It uses the authorized monitor credential, refuses redirects and is restricted to the expected repository and service origin.

At the continuity review on **14 September 2026 at 09:43 UTC**, two successful manual reconciliation runs were visible and no reconciliation run had `event: schedule`. The latest verified manual run was [14 September at 05:20 UTC](https://github.com/fredericmagnathy-ops/alpnai-agent-kit/actions/runs/34809295659): zero orders checked and zero confirmed. The workflow was active on the default `main` branch and Actions was enabled. The cause of the absent scheduled runs was not established; this is not evidence of a payment-provider outage. A later manual check can verify the deployed endpoint but cannot demonstrate ten-minute scheduler continuity. Track scheduled execution, successful completion and report freshness separately.

Read-only describes its blockchain behavior: the service can update the existing ledger after verifying evidence. The exported report contains only batch counts: checked, confirmed and not confirmed. Those counts do not represent total customers, revenue or bank transfers. The workflow does not publish order identifiers, customer data, payment signatures or private keys. Deployment and successful execution remain separate from this documentation.

See [cloud automation](../CLOUD_AUTOMATION.md) for configuration and offline validation, or the payment guides in [English](en/payments.md), [French](fr/payments.md) and [German](de/payments.md).
