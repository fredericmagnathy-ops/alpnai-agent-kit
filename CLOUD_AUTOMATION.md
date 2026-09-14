# Prepared cloud checks

Prepared for `fredericmagnathy-ops/alpnai-agent-kit` on 14 September 2026. These files have not created a repository, published a site, installed secrets or executed a GitHub run. They are intended to be activated by the operator after deployment. They perform no purchases, subscription renewals, wallet operations, outreach, issue creation or source-claim publication.

## Schedule and checks

| Workflow | UTC schedule | Work performed |
|---|---|---|
| `.github/workflows/source-monitor.yml` | 00:17, 06:17, 12:17, 18:17 daily | Authorized `POST /api/operator/check-sources` |
| `.github/workflows/daily-health.yml` | 07:43 daily | Public catalog, sample and MCP discovery; separate authorized `POST /api/operator/growth` |

Both support `workflow_dispatch`. The source endpoint records monitoring results in the service database. It returns `claims_auto_updated: false`: a changed source triggers review, rather than rewriting evidence. Source states `review_required` and `unavailable` fail the run; `baseline` and `unchanged` pass. Configuration, access, network and response-contract errors also fail the run.

The public health check is tied to the prepared **sandbox** contract. It checks three product IDs, a populated evidence sample and six expected MCP tools, including `audit_agent_costs`, with version `2026-07-28`. It makes no `tools/call` request. If the service later enables real payments or changes the contract, review this probe before changing its expectations. A green check establishes only these bounded responses, not source accuracy, coverage, revenue or overall uptime.

The separate growth step records the service's aggregate 30-day diagnosis. It retains only numeric totals for sessions, registrations, activated pilots and zero sandbox revenue, plus one allowed decision: `collect_more_evidence`, `improve_activation` or `review_repeat_usage`. A valid diagnosis passes even when more evidence is needed; it is not a business-performance guarantee. Malformed data, unexpected real revenue or access failures fail the run. The endpoint records its diagnosis but does not automatically change prices or publish content.

## Operator setup after deployment

1. Publish the service at an HTTPS origin that the operator authorizes the workflow to call. The active primary origin is `https://alpnai.com`, verified by the operator. Set `ALPNAI_BASE_URL` to this direct origin; the probe refuses redirects. This kit revision is tested offline, so inspect GitHub Actions for its latest deployed outcome.
2. Put the kit on the default branch of [the public repository](https://github.com/fredericmagnathy-ops/alpnai-agent-kit). Enable Actions according to the repository's policy. Jobs intentionally skip other repository names, including forks.
3. In repository **Settings → Secrets and variables → Actions**, configure the values below. Never commit them or paste them into logs. No secrets are needed to prepare or run offline tests.
4. Run each workflow manually in Actions after the endpoint and secrets are ready. Inspect the summary and JSON artifact. Only then use the scheduled results operationally.

| Setting | Type | Purpose |
|---|---|---|
| `ALPNAI_BASE_URL` | Repository variable, optional | Authorized HTTPS origin; defaults to the expected site. No path, query, credentials or fragment. |
| `ALPNAI_MONITOR_TOKEN` | Repository secret, required for source monitor and daily growth review | Same value as the service's authorized `MONITOR_TOKEN`. Sent only to `/api/operator/check-sources` and `/api/operator/growth` as `Authorization: Bearer …`; never to the public health endpoints. |
| `ALPNAI_SITES_BYPASS` | Repository secret, optional | Operator-provided Site access token when platform access requires it. Sent as `OAI-Sites-Authorization: Bearer …`. It does not replace the monitor token or a purchase key. |

For compatibility with an earlier configuration spelling, workflows also accept `ALPNAl_BASE_URL` (lowercase final `l`) when the canonical variable is absent. Prefer `ALPNAI_BASE_URL` everywhere.

Secrets are scoped to the individual probe step. The workflow token has `contents: read`; checkout does not persist credentials. The Python client refuses HTTP redirects, bounds each network operation to 40 seconds and response bodies to 2 MiB. Each job has a five-minute maximum. It does not print exception bodies, request headers, secrets or raw responses. No retries are performed by the cloud probe; the next scheduled or manually authorized run checks again.

Actions are pinned to full commit IDs resolved from official `v7` tags on 14 September 2026: checkout `3d3c42e5aac5ba805825da76410c181273ba90b1`, setup-python `5fda3b95a4ea91299a34e894583c3862153e4b97`, upload-artifact `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a`. Official major-version release records: [checkout v7.0.0](https://github.com/actions/checkout/releases/tag/v7.0.0), [setup-python v7.0.0](https://github.com/actions/setup-python/releases/tag/v7.0.0), [upload-artifact v7.0.0](https://github.com/actions/upload-artifact/releases/tag/v7.0.0). Tag resolutions are also recorded in the provenance file; later updates require reviewing and changing the pinned IDs.

## Reports and notifications

Artifacts contain a schema version, check kind, UTC check time, success boolean, fixed status/error/decision labels and aggregate counts. They exclude source URLs, source IDs, source notes, evidence text, account information, wallet addresses and tokens. Files are retained for seven days. Temporary local reports belong under ignored `reports/`.

An always-run step writes a sanitized GitHub job summary, and another attempts to upload the minimal report. The final step returns a nonzero exit code when the probe fails. This makes the workflow fail and allows normal GitHub notifications according to the operator's account settings; the kit does not send messages or create GitHub issues. A runner or checkout failure can prevent report creation.

[GitHub schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule) run from the default branch, can be delayed during high load and may be dropped. Scheduled workflows in public repositories can be disabled after 60 days without repository activity. They are not a continuous-service guarantee. [Job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary) and [artifact retention](https://github.com/actions/upload-artifact#retention-period) follow GitHub's documented behavior.

## Offline verification

```sh
python3 -m unittest discover -s tests -v
```

The mock tests check redirects, secret exclusion, failure signaling, MCP metadata and lack of purchases. They do not contact the hosted service or GitHub. Once configured and authorized, the same probe can be run from the operator's own environment using its secret store:

```sh
python3 scripts/check_cloud.py health --report reports/daily-health.json
python3 scripts/check_cloud.py sources --report reports/source-monitor.json
python3 scripts/check_cloud.py growth --report reports/growth-review.json
```

These latter commands make real endpoint calls; `sources` records a source-monitoring result and `growth` records an aggregate diagnosis. They remain separate from the offline test command.

The sample probe validates the envelope `{mode:"free_sample",payment_required:false,data:SNAPSHOT}` before checking its snapshot ID, facts and sources. MCP discovery uses `/api/mcp`. Health monitoring lists tools without invoking the audit or any purchase.
