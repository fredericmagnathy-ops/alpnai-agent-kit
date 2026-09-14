# Payments and test mode

Distinguish free audits, simulated purchases and x402 settlement under validation.

[Documentation library](README.md) · [Website documentation](https://alpnai.com/en/docs)

[Français](../fr/payments.md) · [English](../en/payments.md) · [Deutsch](../de/payments.md)

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

The server prepares an order and supplies payment requirements in a 402 response. An authorized buyer agent can then produce the matching authorization. The service checks amount, network, recipient and mandate before settlement.

The facilitator helps verify and settle payment. A pending or unknown state requires checking the original order; it should not trigger a new automatic spend.

## From wallet to bank

The proposed payment is USDC on Base into the seller’s wallet, accessible through MetaMask. Converting these proceeds into CHF or EUR and transferring them to a bank uses a separate provider.

This route does not depend on Coinbase Business. The conversion provider must accept the seller’s activity and bank account; its rates, fees and timing apply. The customer buys a service, not an investment, return or IPO allocation.

---

[Previous: Connect an agent with MCP](mcp.md) · [Next: Data and access](security.md)
