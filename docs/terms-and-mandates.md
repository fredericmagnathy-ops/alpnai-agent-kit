# Terms, consent and purchasing mandates

ALPNAI identifies the service conditions by a version and a SHA-256 fingerprint. The [current conditions](https://alpnai.com/en/legal/terms) display their version and provide a downloadable JSON archive containing the public documents in French, English and German.

The current reference is `service-2026-09-14-v2`. Its [fixed archive](https://alpnai.com/legal/versions/service-2026-09-14-v2.json) preserves the text associated with that identifier. The fingerprint is calculated over the compact JSON serialization. Historical archives must not be amended under their existing version.

## Test registration

The registration page submits explicit consent, its displayed version and fingerprint, and the chosen language. The server compares them with its own published reference before creating an agent. An absent or stale reference returns `409 terms_changed`; the page clears consent and asks the customer to review the new document.

The initial registration records the version, language and creation timestamp against the authenticated account. Rotating a key preserves that original registration and the budget already used. It is not recorded as a new historical acceptance. Existing records are never retroactively relabelled as consent to newer conditions.

## Commercial mandates

The payment flow remains closed during validation. When enabled, preparation requires the current version, fingerprint and explicit agreement. The message presented for signature includes the version, fingerprint, archive address, language, wallet, agent, network, spending limit and expiry.

Confirmation checks both the submitted reference and the version stored in the pending mandate. A valid signature cannot revive a mandate prepared under stale terms. The update also checks that version when activating the mandate. Revocation does not require accepting new terms and remains available while commerce is disabled.

A mandate sets a limit; it is not a payment. Each purchase still needs its own exact USDC authorization. The client must never automatically accept updated conditions or generate a new signature when it receives `terms_changed`.

## Scope

These controls establish which document the application presented and recorded. They do not by themselves complete billing, determine tax treatment, validate a real settlement, or activate paid services. Buyer identity, total price, delivery and accounting remain separate parts of the commercial flow.

See [payment operations](payment-operations.md) and the [payment guide](en/payments.md).
