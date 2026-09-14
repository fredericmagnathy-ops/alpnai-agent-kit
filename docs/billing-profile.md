# Private billing profile

An ALPNAI account owner can optionally save contact details for future billing documents. Open the [customer account](https://alpnai.com/account), sign in through ChatGPT, and expand **Billing profile**. The form is available in French, English and German. Free tools do not require a billing profile.

This feature stores a current, editable profile. It does not place an order, authorize payment, issue an invoice, verify identity or decide tax treatment. No billing-profile snapshot is attached to an order yet. The API reports `tax_status: "not_verified"` and `commercial_use: "not_enabled"` when reading or saving a profile.

## Private access

`/api/account/billing` is an account endpoint, not an agent API or MCP tool. It uses the signed-in ChatGPT account session. An agent key does not grant access. The server derives the owner from the authenticated session; clients cannot select another owner through a request field.

Responses use `Cache-Control: private, no-store`. Mutations require a same-origin browser request with `Content-Type: application/json`; cross-site requests are refused. Use the account form rather than exporting session cookies or placing credentials in scripts.

## Fields

The API requires every key below. For an optional text field, send an empty string (`""`) rather than omitting it or sending `null`.

| Key | Accepted value | Maximum length |
| --- | --- | --- |
| `customer_type` | `individual` or `business`; declared personal or business use | Exact enum |
| `legal_name` | Required legal name | 160 |
| `address_line1` | Required address | 160 |
| `address_line2` | Optional address continuation | 160 |
| `city` | Required city | 100 |
| `region` | Optional region/state | 100 |
| `postal_code` | Optional postal code | 24 |
| `country_code` | Required uppercase two-letter country code from the form's supported list | 2 |
| `tax_id` | Optional business tax identifier, self-declared and unverified | 64 |

The form initially selects personal use; this does not classify a purchase as B2C or B2B for tax purposes. A country selection does not verify residence, establishment or place of supply. A tax identifier does not establish an exemption or reverse-charge eligibility. Do not enter a social security number in this field.

Lengths are measured using JavaScript string length. Text is normalized to Unicode NFC and trimmed. Both raw and normalized lengths are checked; control characters and the blocked bidirectional formatting controls are rejected. Unknown profile keys are rejected. The JSON request body limit is 5,000 bytes.

## Read and create

`GET /api/account/billing` returns the saved `profile`, its `revision` and `updated_at`. With no saved profile, all three are `null`. Read the current state before modifying it. For example, from a signed-in page on ALPNAI:

```js
const response = await fetch('/api/account/billing', { cache: 'no-store' });
if (!response.ok) throw new Error(`Billing profile: HTTP ${response.status}`);
const current = await response.json();
```

Create with `PUT /api/account/billing`, using `revision: null` only when no profile exists. This example contains fictional contact details:

```json
{
  "revision": null,
  "profile": {
    "customer_type": "individual",
    "legal_name": "Alex Example",
    "address_line1": "12 Example Street",
    "address_line2": "",
    "city": "Geneva",
    "region": "",
    "postal_code": "1201",
    "country_code": "CH",
    "tax_id": ""
  }
}
```

Successful creation returns HTTP `201`, the normalized profile, a new UUID revision and an ISO timestamp. Saving the profile is independent of accepting commercial terms or issuing a purchasing mandate.

## Update without overwriting another change

To update, send the complete profile in a `PUT` request with the latest revision returned by `GET` or a successful save. HTTP `200` returns a new revision. Revisions are lowercase UUID v4 values; reuse the server's current value, rather than generating one yourself.

If another tab has changed or deleted the profile, the server returns HTTP `409` with `error: "profile_changed"`. Creating with `revision: null` when a profile already exists also returns `409`. These checks prevent silent overwrites, including after deletion and recreation.

The account form preserves unsaved entries after a conflict. **Reload** replaces those entries with the latest stored profile. Compare or copy your edits before reloading, then apply the intended changes to the current version. After an ambiguous network failure, read the profile before retrying a mutation.

## Delete

`DELETE /api/account/billing` accepts only the latest revision:

```json
{
  "revision": "6b270b90-d790-4aba-8d21-9a12527f803e"
}
```

Replace the example with the server-returned revision. A successful deletion returns HTTP `200` with `profile`, `revision` and `updated_at` set to `null`. A missing or outdated profile returns `409`. The account form asks for confirmation before deletion.

## Errors

| HTTP | Error | Next step |
| --- | --- | --- |
| `400` | `invalid_request` | Check JSON, top-level keys and revision format. |
| `400` | `invalid_profile` | Correct the returned `fields`; an unknown profile key is reported as `profile`. |
| `401` | `sign_in_required` | Sign in to the account. |
| `403` | `origin_forbidden` | Use the same-origin account form with JSON requests. |
| `409` | `profile_changed` | Read the current profile and reconcile edits. |
| `413` | `body_too_large` | Reduce the request below the body limit. |
| `503` | `billing_unavailable` | Keep unsaved entries and try reading again later. |

## Retention and current limits

The current application database row contains the account identifier, profile, revision and modification timestamp. It can be viewed, corrected or deleted. Deletion removes that row; it does not promise immediate erasure from provider backups or logs. There is no automatic inactivity purge.

The form does not send billing details to the blockchain, the payment facilitator or journey measurement, and does not authorize marketing. Future order and accounting records need their own dated snapshots and applicable retention rules; editing a current profile must not rewrite historical records. That order-snapshot integration is not implemented by this feature.

See the [billing-profile privacy notice](https://alpnai.com/fr/legal/privacy#billing-profile). The current legal-document bundle is [service-2026-09-14-v3](https://alpnai.com/legal/versions/service-2026-09-14-v3.json); the [v2 archive](https://alpnai.com/legal/versions/service-2026-09-14-v2.json) remains a separate historical document and does not contain this new section.

[Back to documentation](README.md)
