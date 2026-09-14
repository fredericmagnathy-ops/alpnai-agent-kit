# Source monitoring and evidence freshness

ALPNAI monitors changes in official references. Detection produces a review signal; it never publishes a new investment claim or executes a trade.

## Three separate channels

| Channel | Official reference | What is compared |
| --- | --- | --- |
| S-1 announcement | [OpenAI announcement](https://openai.com/index/openai-submits-confidential-s-1/) | Normalized page text |
| Company structure | [OpenAI structure](https://openai.com/our-structure/) | Normalized page text |
| IPO news discovery | [OpenAI news RSS](https://openai.com/news/rss.xml) | Title, canonical link, date and description for entries mentioning IPO, S-1 or initial public offering |

The RSS is a detection channel outside the sold reference corpus. Reading its metadata does not verify the linked article. The two reference pages have returned access challenges during automated checks; an accessible RSS must not conceal those failures.

## Status contract

- `baseline`: the first readable, valid response establishes a comparison fingerprint.
- `unchanged`: the fingerprint matches the most recent valid response.
- `review_required`: content changed and needs verification before facts can be published.
- `unavailable`: retrieval or validation failed. The previous valid reference is preserved.

`claims_auto_updated` is always `false`. A baseline is not a new factual verification. An empty filtered feed does not mean that no IPO exists. Keyword matching can miss relevant announcements or include unrelated discussion; follow-up verification is essential.

## Reading limits and privacy

Each public request is limited to twelve seconds and two megabytes. Redirects, malformed XML, unexpected content types, external entities and challenge pages are rejected. No authentication credentials are sent to the reference publisher. There is no access-control bypass.

The database stores diagnostic status, fingerprints and timestamps. It does not copy full articles into monitoring records. The RSS fingerprint is stable when unrelated news is added or reordered. A detected change never rewrites the product's dated facts.

## Scheduled checks

The private check runs through the ALPNAI source-monitor workflow every six hours, subject to GitHub scheduling delays. A report remains failed when any reference is unavailable or requires review, even if other channels work. Public workflow artifacts contain sanitized counts, not private credentials or detailed account records.

An operator can inspect the source checks from the private console. Monitoring is not a guaranteed real-time alert service. iPhone push delivery and automatic investment execution are not active.

See [payment operations](payment-operations.md) for the separate commercial ledger and [documentation](README.md) for API integration.
