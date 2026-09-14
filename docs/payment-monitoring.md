# Payment monitoring and freshness

**Release status:** published on 14 September 2026 at 11:21 UTC. The private panel and its initially empty state were verified in the operator console. Commercial payments remain disabled, and these controls do not establish a real sale.

The monitor answers three questions: when did reconciliation last start, when did an attempt finish, and when did a pass last finish without an error? It makes missing or interrupted checks visible without submitting a new payment.

## Owner console

The **Order monitoring** panel is in the [operator governance page](https://alpnai.com/dashboard/governance#payment-monitoring). It is reserved for the signed-in site operator, not ordinary customer accounts or agent keys. Labels are available in French, English and German; displayed dates use `Europe/Zurich`.

- **Refresh status** reads the recorded state. It does not run reconciliation.
- **Check orders now** requests one authorized reconciliation pass, then reads its state. The pass can update existing ledger records after checking evidence; it does not submit a payment again.
- While the page is visible, status refreshes approximately once per minute. Closing the page stops that browser refresh; it is not the background scheduler.

The panel sends no email, message, SMS or iPhone notification. A visible recent status proves only the recorded pass, not regular automatic execution or a transfer to a bank.

## Three bounded records

The database keeps three operational snapshots and a sequence counter. It does not append an unlimited run history.

| Returned field | Meaning |
| --- | --- |
| `latest` | Most recently started recorded attempt; it may still be running. |
| `last_completed` | Most recent recorded attempt that finished, including a degraded or failed attempt. |
| `last_clean` | Most recent attempt that finished with status `completed` and no recorded errors. |

Each snapshot exposes start and finish times, trigger, status and the aggregate counts `checked`, `confirmed` and `errors`. A database-allocated sequence orders attempts, including starts within the same millisecond. An older worker finishing late cannot overwrite a newer attempt's snapshot. Here, “most recent” follows attempt sequence rather than whichever worker happens to finish last.

The status response does not expose run identifiers, sequence numbers, order identifiers, customer details, payment addresses or secrets. These operational snapshots are separate from order and payment records. Existing GitHub runs are not backfilled into this new server-side tracking.

## Read the status correctly

| `status` | Interpretation |
| --- | --- |
| `not_observed` | No latest attempt has been recorded by this monitor. |
| `running` | The latest attempt is still marked running and started no more than five minutes ago. |
| `interrupted` | The latest attempt is still marked running more than five minutes after starting. It may have stopped or be taking too long. |
| `attention` | The latest attempt finished with `degraded` or `failed`. A recent older success does not hide this result. |
| `stale` | With no running or failed latest attempt taking priority, there is no clean completion or the last clean completion is more than 30 minutes old. |
| `recent` | The latest attempt completed and the recorded clean completion is no more than 30 minutes old. |

The five-minute and 30-minute values are operational thresholds, not promised delivery times. `interrupted` is a derived status: it does not kill a worker or cancel a payment. Running/interrupted and failed/degraded latest attempts take priority over the freshness label. `last_clean_age_seconds` remains available to show the age of an earlier clean pass.

**Clean does not mean every order was confirmed.** A valid check can examine zero orders, or leave an order pending without encountering an error. It proves that pass completed without a recorded operational error; it does not prove a real transfer or eliminate all pending work.

## API access

### Read only

```text
GET /api/operator/payments/reconcile
```

GET requires the signed-in site operator. A monitor token alone does not grant access to this status endpoint. It reads saved operational state and returns private, non-cacheable JSON. The following is an illustrative empty-state response, not a live measurement:

```json
{
  "status": "not_observed",
  "checked_at": "2026-09-14T11:00:00.000Z",
  "freshness_minutes": 30,
  "last_clean_age_seconds": null,
  "latest": null,
  "last_completed": null,
  "last_clean": null,
  "scheduled_cadence_verified": false,
  "payment_operations_called": false,
  "notifications_active": false
}
```

Malformed stored state or impossible future timestamps produce `503 reconciliation_status_unavailable`, not a fabricated recent success. Unauthorized access returns `403 operator_only`.

### Request one reconciliation pass

```text
POST /api/operator/payments/reconcile
Content-Type: application/json
```

```json
{"action":"reconcile"}
```

POST accepts either the existing authorized monitor credential, or a same-origin JSON request from the signed-in operator. Its body must contain exactly the `action` key and is limited to 1,024 bytes. Invalid actions return `400`; an oversized body returns `413`; unauthorized requests return `403`. Only an authorized, valid request starts a tracked attempt.

Each pass examines at most five existing unresolved orders. It reads blockchain evidence and may record a verified settlement or release a reservation that was never submitted. It never calls the payment facilitator to settle again. The private POST response can contain examined order identifiers; the GET monitoring projection and exported GitHub summary omit them.

A pass with no operational errors returns HTTP `200` and `check_status: "completed"`. Per-order failures, including RPC exceptions, are counted and produce HTTP `503` with `check_status: "degraded"`; remaining orders can still be checked. A broader failure is recorded as `failed` where possible and returns `503 reconciliation_unavailable`. If even recording completion fails, a later read can show `interrupted` or unavailable status. Errors preserve the original payment context and are not an instruction to send another payment.

## Remote checks and scheduled checks are different

`trigger: "monitor"` means the request used the authorized remote monitor credential. A manually dispatched GitHub run also uses that credential. `trigger: "operator"` means the console operator initiated it. Neither field proves GitHub's `event: schedule`, so the response deliberately retains `scheduled_cadence_verified: false`.

Independent GitHub evidence now includes a [successful scheduled reconciliation run at 10:05 UTC on 14 September 2026](https://github.com/fredericmagnathy-ops/alpnai-agent-kit/actions/runs/34831397005). Its report recorded zero orders checked and zero confirmed. This is a genuine scheduled execution, but a single run does not prove the configured ten-minute cadence. At the separate audit completed at 10:49 UTC, this was the only scheduled reconciliation run visible; health had none, and source monitoring had one scheduled failure.

The earlier observation at 09:43 UTC that no scheduled reconciliation was visible is historical, not the current conclusion. The new server monitor adds evidence of observed requests and their freshness; it does not infer a reliable cron schedule, backfill earlier GitHub runs or send alerts by itself.

See [payment operations and recovery](payment-operations.md) for the configured cadence and reconciliation limits, and [printable payment receipts](payment-receipts.md) for confirmed historical documents.

[Documentation index](README.md)
