# Data and access

Prepare minimal records and choose where the calculation runs.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/security.md) · [English](../en/security.md) · [Deutsch](../de/security.md)

## Browser calculation

Local tools calculate using records loaded into the page. Record contents are not sent to the API for this calculation. HTML and JSON exports are created on your device.

The page may load its resources and, with your consent, measure journey events. Local calculation does not mean the entire site works offline.

## Calculation through API or MCP

With API or MCP, records are sent to the server for calculation. They are not saved in the audit application database. Account data, hashed keys and pilot receipts are handled separately.

Your infrastructure and the host may produce technical logs. Send only calculation inputs, even when the response contains persisted:false.

## What belongs in the records

Use opaque identifiers such as task-001. Provide costs, variant, success and duration. Keep customer names, emails, documents, prompts and detailed responses in your own environment.

Contract fields are strict. Do not put secrets in task_id or workflow: a text field is not unrestricted storage.

## Protect and replace a key

An active key allows authorized calls for its account. Keep it server-side or in your local environment; do not add it to a public repository or code distributed to website visitors.

Replace a lost key through the supported flow; the old key is revoked and previously used test budget is retained. The audit needs no MetaMask password, private key or recovery phrase.

---

[Projects, payments and test mode](payments.md)
