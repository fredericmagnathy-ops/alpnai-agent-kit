# Latency Lab: duration and retries

Identify slow tasks and quantify additional attempts using the same records.

[Documentation library](README.md) · [Website documentation](https://alpnai.com/en/docs)

[Français](../fr/latency.md) · [English](../en/latency.md) · [Deutsch](../de/latency.md)

## What you receive

For each version, inspect recorded task durations, P50, P95, maximum duration and retry count. Compare the same tasks after a model or workflow change.

Record duration in milliseconds in latency_ms for every attempt. duration_coverage is the proportion of tasks with durations recorded for every attempt.

## How to read P50 and P95

The calculation sums recorded attempt durations for each task. It sorts these sums and uses the nearest-rank method: ceil(0.50 × n) for P50 and ceil(0.95 × n) for P95.

For example, with 20 tasks P95 is the 19th sorted value. It describes this sample, not a guarantee for future requests.

## Measure retries

Recorded retries = attempts − distinct tasks, calculated separately for each variant. With 40 tasks and 48 attempts, you have 8 recorded retries.

Compare retry_attempts with your own retry budget. This version measures additional attempts; it does not configure a retry ceiling in your agent or provide a separate failed-retry count.

## Set a duration ceiling

In config, maxP95LatencyMs sets the recorded P95 ceiling. Latency Lab evaluates it for each group; Quality Gate uses the candidate’s check for its decision.

If any attempt is missing a duration, the group’s P50, P95 and maximum become null. within_p95_threshold is null when durations are incomplete or no ceiling was requested. Do not replace a missing duration with zero.

## Understand the duration measure

Summed durations are not end-to-end user waiting time when attempts run in parallel. They also omit waits that you did not record.

The format does not require timestamps or attempt ordering. It cannot identify the first attempt with certainty or establish that a particular failure was a retry.

---

[Previous: Spend Proof: cost per success](spend-proof.md) · [Next: Quality Gate: compare before changing](quality-gate.md)
