# Printable payment receipts

The prepared receipt page lets an account owner keep a readable record of a confirmed USDC payment. It is available in French, English and German, with a layout suitable for printing. **Commercial payments remain disabled and no real sale is established by this feature.** An empty account does not require a deposit or test payment.

A payment receipt records confirmed settlement. It is not a tax invoice, proof of a bank transfer or a calculation of net profit. The separate [quotation](billing-quotations.md) describes the offer before payment; preparing or downloading one does not create a receipt for a paid order.

## Open, print or save

1. Sign in through ChatGPT and open the [customer account](https://alpnai.com/account).
2. In **Orders and payments**, a confirmed order has **Receipt and result** for the JSON download and **Printable receipt** for the readable document.
3. Open **Printable receipt**, then use the browser's **Print** command. Choose a printer or **Save as PDF** where supported by the browser and operating system.

The server generates an HTML page. It does not generate or store a PDF, open a print dialog automatically, email the document or initiate a payment. Saving a PDF creates a local file through the browser. The printable page includes the delivered result's hash, rather than the purchased result itself; use **Receipt and result** for the separate JSON result download.

## Route and language

```text
GET /api/account/orders/{id}/receipt?lang=fr
GET /api/account/orders/{id}/receipt?lang=en
GET /api/account/orders/{id}/receipt?lang=de
```

Replace `{id}` with the actual order identifier from your account. If `lang` is omitted, the page uses French. Unsupported values, duplicate `lang` parameters or any other query parameter return `400 invalid_document_options`.

This is a private account route using the signed-in ChatGPT session. An agent API key does not grant access. The server checks that the order belongs to the account's agent and has a matching Base-mainnet mandate. An unknown order or another customer's order returns `404`; users cannot select a different owner through a parameter.

The agent's existing JSON order endpoint remains `GET /api/v1/orders/{id}` with agent authentication. It does not expose the customer's private billing copy.

## What appears on the document

A valid receipt shows the order reference, product, total paid in USDC, order-preparation time and the time ALPNAI recorded confirmation, in UTC. It includes the Base network, payer and receiving addresses, transaction identifier and delivered-result hash.

When the order contains a complete, valid frozen billing snapshot, the document also shows the seller and customer details saved with that quotation, the quoted net and tax components, saved terms version and hash, and quotation hash. A supplied customer tax identifier is labelled **declared**, not independently verified by this document. The receipt reproduces the saved amounts; it does not decide a new tax treatment.

The confirmation timestamp is the ledger recording time, not a claim about the precise time of a bank deposit or a fresh blockchain lookup. Links to the transaction on BaseScan and the saved terms archive can be opened separately.

## Historical integrity

The renderer requires the order to be `settled`. It validates the saved successful receipt against the order's transaction, amount, network and USDC payment requirements. It checks the frozen result hash and, where present, the billing-snapshot hash, associated amounts, identifiers and saved terms reference.

It does **not** load today's billing profile, today's terms or the current billing-review status. Later profile edits, profile deletion, quotation expiry or a later terms version must not rewrite a historical receipt. Rendering performs no new provider settlement or blockchain transaction.

For an older order with no billing snapshot, the page provides a minimal payment record and explicitly says that frozen billing details are absent. It does not reconstruct a customer identity, seller billing identity or tax breakdown from current settings. An incomplete or corrupted snapshot is an error, not a reason to silently downgrade to that historical fallback.

## Privacy and errors

The page contains no scripts, remote fonts, images or other remotely loaded assets. It returns private, non-cacheable HTML with indexing disabled and a restrictive content-security policy. External links are ordinary links; opening the page does not fetch those destinations. The document may contain customer contact details and payment addresses, so downloaded or printed copies should be shared only with intended recipients.

| Response | Meaning | Next step |
| --- | --- | --- |
| `200 text/html` | A validated historical payment receipt can be displayed. | Read, print or save through the browser. |
| `400 invalid_document_options` | Invalid language or query parameters. | Use one supported `lang` value. |
| `401 sign_in_required` | No authenticated account session. | Sign in to your account. |
| `404 order_not_found` | No accessible Base-mainnet order with that identifier. | Open the order from your own account. |
| `409 receipt_not_confirmed` | The order is not settled; `payment_required` is false. | Follow the existing order status. Do not send a second payment. |
| `503 receipt_unavailable` | Required data is missing, invalid or unavailable. | Keep the order reference and retry reading later; do not create another payment. |

Downloading a receipt does not resolve a pending payment, issue a refund or produce a tax invoice. For delayed confirmation, follow [payment recovery](payment-operations.md). For the current handling of billing data, see the [privacy notice](https://alpnai.com/fr/legal/privacy#billing-profile).

[Payment operations](payment-operations.md) · [Billing quotations](billing-quotations.md) · [Documentation index](README.md)
