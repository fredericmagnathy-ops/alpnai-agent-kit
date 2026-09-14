# ALPNAI payment operations

This page describes the implemented recovery and reporting controls. Publishing documentation or running a monitor does not enable commercial payments or prove a real purchase. Availability depends on the deployed service configuration and verified operation of the payment path.

## One order, one payment attempt

The service freezes a commercial result before issuing its payment challenge. A quote is not revenue. A verified authorization can reserve its permitted budget; only one worker can claim the settlement attempt. Repeating the same accepted purchase follows the existing order. It must not create a second payment attempt.

If a provider times out or confirmation is uncertain, the order remains under review. Keep the original order and idempotency identifier. Do not send another payment or replace the identifier to bypass a pending result.

## Recovery after a delay

Reconciliation reads blockchain evidence; it never sends a transaction or calls the facilitator to settle again. Each authorized pass examines at most five unresolved orders, oldest reviewed first. Updating each reviewed order's timestamp lets later passes reach the rest of the backlog.

For an order without a known transaction hash, the service searches finalized USDC authorization logs from its recorded starting block or persisted scan cursor. Each pass covers one inclusive page of at most **2,000 blocks**. When that page contains no matching authorization, the cursor advances to the following block. Its guarded database update prevents an overlapping worker from overwriting newer progress. A failure leaves the page available for a later attempt.

This replaces a fixed total lookback cutoff: delayed orders can be resumed through successive pages. A large backlog still needs multiple passes. Recovery time depends on the backlog, chain finality, RPC availability and successful scheduled execution; it is not an instant-delivery promise. An existing transaction hash avoids the log search but still requires the full confirmation checks.

The initial proof decoder supports direct USDC authorization calls. It verifies the token, payer, recipient, amount, nonce, successful receipt and finalized block. Batch or proxy calls that it cannot prove remain unresolved; they are not guessed to be successful. An expired or revoked reservation can be released only if no settlement attempt was claimed. Reconciliation does not cancel an uncertain submitted payment or refund it automatically.

## Delivery follows confirmation

The confirmed settlement must be recorded successfully before the purchased result and payment receipt are delivered. A payment challenge or unresolved response does not include the commercial payload. An unresolved lookup returns HTTP `202`; cancellation before submission returns `409`. Database or malformed-record failures do not become a fabricated success.

Agents can check their own order through `GET /api/v1/orders/{id}` with their agent authentication. Signed-in customers can use `GET /api/account/orders/{id}`; ownership comes from the authenticated account, not a submitted customer identifier. The account's commercial receipt view is restricted to Base mainnet orders with a matching mandate and agent. Responses are private and not cacheable.

## What the dashboard counts

Commercial aggregates count only settled Base mainnet orders. Pending orders, quotes, Sepolia tests and sandbox purchases do not increase real revenue. Paying customers are distinct authenticated account owners, not transaction counts or unique wallet addresses. Commercial order lists expose a small set of metadata; the transaction hash is shown only after settlement.

USDC totals are gross settled receipts. They are not net profit, a bank balance, a fiat conversion or recurring subscription revenue. Fees, refunds, taxes and bank conversion require their own accounting. A statistics read failure must appear as unavailable rather than a new zero balance.

## Scheduled checks

The prepared reconciliation workflow runs at minutes 06, 16, 26, 36, 46 and 56 of each hour, and supports manual dispatch. Its fixed request is `POST /api/operator/payments/reconcile` with `{"action":"reconcile"}`. It uses the authorized monitor credential, refuses redirects and is restricted to the expected repository and service origin.

Read-only describes its blockchain behavior: the service can update the existing ledger after verifying evidence. The exported report contains only batch counts: checked, confirmed and not confirmed. Those counts do not represent total customers, revenue or bank transfers. The workflow does not publish order identifiers, customer data, payment signatures or private keys. Deployment and successful execution remain separate from this documentation.

See [cloud automation](../CLOUD_AUTOMATION.md) for configuration and offline validation, or the payment guides in [English](en/payments.md), [French](fr/payments.md) and [German](de/payments.md).
