# Payments and test mode

Distinguish free audits, simulated purchases and x402 settlement under validation.

## What can be used today

Spend Proof and local calculations require no payment. The Evidence pilot lets you try purchases using a key and a fictitious budget.

An x402 integration using PayAI is prepared for USDC on Base, but the mainnet payment flow remains under validation. Code being present does not establish that a real sale or complete settlement has occurred.

## Try without transferring funds

This request calls an existing route in sandbox mode. Its receipt contains settled:false, real_revenue_usdc:0 and a simulated price. No wallet connection is needed.

Repeat the same request with the same Idempotency-Key to retrieve the same purchase. Reusing the identifier with different parameters causes a conflict; use a new identifier for a new order.

```bash
curl --fail-with-body --silent --show-error \
  'https://alpnai.com/api/v1/snapshot' \
  --header "Authorization: Bearer ${ALPNAI_AGENT_KEY}" \
  --header 'X-ALPNAI-Mode: sandbox' \
  --header 'Idempotency-Key: docs_demo_20260914_001'
```

## Understand the planned x402 exchange

Before any 402 request, the prepared flow requires a valid profile and billing review tied to the accepted terms. The quotation then fixes the total and details used. Entering a profile is not tax verification; no review-issuance workflow is open yet.

The server prepares an order and supplies payment requirements in a 402 response. An authorized buyer agent can then produce the matching authorization. The service checks amount, network, recipient and mandate before settlement.

The facilitator helps verify and settle payment. A pending or unknown state requires checking the original order; it should not trigger a new automatic spend.

## Recover an order and its receipt

A pending order keeps the same identifier. Reconciliation searches finalized blocks for payment evidence in bounded pages with a persisted resume position. An outage or delay never triggers another settlement attempt.

A reservation abandoned before any attempt is released when the quote expires. Once an attempt has begun, it remains under review: elapsed time alone never releases its budget.

After confirmation, the owner can retrieve the receipt and result from their customer workspace. Revenue counters include only confirmed USDC settlements on Base; sandbox purchases and testnet payments are excluded.

## Print a confirmed receipt

In your account, a confirmed order offers “Receipt and result” for the JSON file and “Printable receipt” for a readable page. Open the page, then use your browser’s Print command to print or save a PDF.

The receipt retains the associated quotation’s details and amounts even if the profile changes. It shows the confirmation recorded in UTC, transaction and document hashes. An older order without frozen billing details remains a minimal receipt. This document does not replace a tax invoice.

Only the owning account can open this private document. No printable receipt is produced for an unconfirmed order; viewing it contacts no facilitator and makes no payment. Real purchases remain disabled.

```http
GET /api/account/orders/{order_id}/receipt?lang=en
```

## From wallet to bank

The proposed payment is USDC on Base into the seller’s wallet, accessible through MetaMask. Converting these proceeds into CHF or EUR and transferring them to a bank uses a separate provider.

This route does not depend on Coinbase Business. The conversion provider must accept the seller’s activity and bank account; its rates, fees and timing apply. The customer buys a service, not an investment, return or IPO allocation.

[ALPNAI documentation](https://alpnai.com/en/docs/payments)
