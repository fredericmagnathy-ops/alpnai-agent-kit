# Billing quotations

The prepared quotation feature preserves what was offered, the customer's billing details and the exact amount before a payment can be requested. It provides a private account view and JSON download. **Real purchases remain disabled.** A private operator review workflow is now available. No real customer was approved during its implementation; customers and agents cannot approve their own review. An empty quotation list is therefore expected; it is not a request to send money or add funds.

The free Spend Proof, Latency Lab and Quality Gate tools do not require a quotation or billing profile.

## Three different documents

| Document | What it means | What it does not prove |
| --- | --- | --- |
| Quotation | A saved offer containing the product, applicable terms, amounts and expiry. | Acceptance, payment, delivery or revenue. |
| Payment receipt | A confirmed payment has been recorded for the order. | A bank deposit, net profit or a tax invoice. |
| Invoice | A separate commercial/accounting document with the required particulars. | Payment unless separately confirmed. Invoice issuance is not implemented here. |

A purchasing mandate authorizes an agent within a budget. It is not a payment, invoice or substitute for the separate exact payment authorization.

## What a quotation preserves

The prepared path saves a dated, immutable billing snapshot alongside the frozen product result and payment requirements. It includes:

- Seller name, trading name, address and contact details at preparation.
- The customer's billing profile, its revision and modification date.
- The terms version, SHA-256 hash and fixed archive URL.
- Product, USDC currency, network, token contract, net amount, tax component, total, configured treatment and rate.
- Issue and expiry times, with an integrity hash covering the stored snapshot.

The account export includes these customer-facing details. Internal billing-review identifiers, evidence references and the full review record are not exported. The result being purchased is also withheld until confirmed payment.

New quotations require a valid review linked to the same owner, profile revision and terms version. A review must be approved, unexpired and contain the required supporting references. The client and agent cannot issue a review through their APIs. Entering a tax number or choosing business use in the [billing profile](billing-profile.md) does not verify those declarations or approve a tax treatment.

## Operator review and revocation

The [private operator console](https://alpnai.com/dashboard/governance#billing-review) lists up to 50 minimal dossiers per page. Full addresses, tax identifiers and supporting references load only after opening a dossier. The API requires the operator account session; an agent key or monitoring credential cannot access it. Unrevoked decisions remain reachable if a customer deletes their profile.

1. Read the customer declaration, exact profile revision and archived terms. A declared country, business use or tax identifier does not establish tax treatment.
2. Record the treatment established by an appropriately supported assessment. The form starts without a treatment, rate, evidence references or expiry. Record the legal basis, seller tax status reference and customer evidence reference. It stores references, not uploaded evidence, and does not certify that they are correct.
3. Choose an explicit future expiry. The software accepts at most 90 days; this technical limit is not a recommended legal review period. The preview shows local time and the exact UTC instant.
4. Review the summary and explicitly confirm the decision. Approval atomically checks the current profile, agent account and prior decision context. A changed dossier requires reloading and review. Duplicate submissions with the same unchanged request do not issue another decision.
5. Revoke an existing decision explicitly before replacing it, including when it has expired or the profile/terms changed. A reason and confirmation are required. The original decision and dates remain immutable; the server records the approver and revoker. Revocation does not refund money or reverse an already submitted transfer.

An uncertain response retains the same request identifier for a retry. Reloading the dossier lets the operator inspect the saved state. References and form entries stay in the current page rather than browser persistent storage; denied access clears the private view.

Approval records a human decision. It does not activate commercial gates, create a purchasing mandate, authorize a transfer, issue an invoice or submit a payment. The three free analysis tools remain available without review.

Technical endpoints: `GET /api/operator/billing` for the bounded list, `GET /api/operator/billing?user_id=…` for a dossier and `POST /api/operator/billing` for explicit approval/revocation. Mutations require the operator session, same origin and JSON. Responses are private and not cacheable. The account owner and agent APIs do not acquire these permissions.

## Exact amounts

The prepared calculation treats the catalog amount as the **total USDC amount**. If an approved treatment includes tax, the service divides that total into net and tax components; it does not add an extra amount to the catalog total. It uses integer arithmetic in millionths of USDC and rounds the net component to the nearest atomic unit, with ties rounded up. Tax is the remainder, so net plus tax equals the exact total.

The proposed one-off totals are 0.01 USDC for Snapshot, 0.05 USDC for Change Set and 0.25 USDC for Evidence Pack. These remain commercially inactive. Arithmetic support does not establish the seller's tax status or choose the treatment for a customer. There is no default approval or assumed tax exemption.

The snapshot total must match the order, token and network in the x402 payment requirements. Budget reservation and settlement use that total. Facilitator charges borne by the seller, refunds, affiliation and bank-conversion costs require separate accounting; the quotation does not calculate net profit or money available in a bank account.

## View and download

In the [customer account](https://alpnai.com/account), **Your agent's quotations** lists up to 25 recent unsubmitted Base-mainnet quotations that have a billing snapshot. It shows the product, total and expiry. Expired quotations may remain visible for reference.

**Download quotation** reads the private order endpoint and saves `alpnai-quotation-{order_id}.json` in the browser. It does not call a payment provider. Downloads contain the customer's billing details; share them only with intended recipients.

Technical read endpoints:

- `GET /api/account` includes the owner's `commercial_quotes` list.
- `GET /api/account/orders/{id}` returns the owner's quotation or order status. ChatGPT account sign-in is required; another customer's or an unknown order returns `404`.
- `GET /api/v1/orders/{id}` uses agent authentication and returns only that agent's permitted summary, without customer billing details or internal review references.

For a quotation lookup, HTTP `200` includes `status: "quoted"`, `settled: false`, `payment_required: false` and `quotation`. Account responses add `seller` and `customer` to the monetary and terms summary. Responses are private and not cacheable. The download button expects the order still to be in the quoted state; refresh the account if its state changed meanwhile.

## Expiry, changes and unavailable purchases

Quotation validity is capped at five minutes and ends sooner if the billing review expires first. The expiry prevents a new payment submission; it does not erase the historical document. An expired, **unsubmitted** quotation needs a new request and idempotency identifier. Do not use a new identifier for a submitted or uncertain payment: follow the original order through [payment recovery](payment-operations.md).

Editing or deleting the current billing profile does not rewrite or remove an existing quotation's copy. To use corrected details in a new quotation, the current profile revision needs its corresponding review. Profile deletion is not cancellation or refund of an order. The current profile, saved quotations and accounting records have separate lifecycles; this feature implements no automatic quotation purge.

With commercial gates off, a purchase attempt returns `503 commercial_activation_pending`. If that gate is configured later but the required review is missing or invalid, it returns `503 billing_review_required` with `payment_required: false`, before any facilitator operation or HTTP 402 challenge. A saved review and quotation do not switch on commercial payments. Missing review is not an instruction to pay, and filling the profile alone does not resolve it.

See the [current privacy notice](https://alpnai.com/fr/legal/privacy#billing-profile). The terms reference saved in each quotation identifies the exact version used; updated notices do not rewrite earlier archives.

[Billing profile](billing-profile.md) · [Payment operations](payment-operations.md) · [Documentation index](README.md)
