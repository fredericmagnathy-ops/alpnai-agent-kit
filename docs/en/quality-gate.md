# Quality Gate: compare before changing

Inspect success, cost and latency before adopting a candidate.

[Documentation library](README.md) · [Website documentation](https://alpnai.com/en/docs)

[Français](../fr/quality-gate.md) · [English](../en/quality-gate.md) · [Deutsch](../de/quality-gate.md)

## Define your thresholds

By default, each version needs at least 30 distinct tasks. The candidate must succeed on at least 95% of tasks and lose no more than 2 percentage points against the baseline.

Add this object under config in the record file. maxP95LatencyMs and monthlyTasks are optional; the other values shown are defaults.

```json
{
  "minSamples": 30,
  "minSuccessRate": 0.95,
  "maxSuccessRateDrop": 0.02,
  "maxP95LatencyMs": 3000,
  "monthlyTasks": 10000
}
```

## Read the checks

both_variants checks that both versions exist. minimum_distinct_tasks_per_variant checks the sample minimum. same_task_set requires exactly matching identifiers.

observed_success_rate checks success thresholds; recorded_latency checks the requested ceiling; lower_cost_per_successful_task requires strictly lower cost per success. pass means satisfied, fail not satisfied, unknown undetermined and not_requested not requested.

## What to do with the decision

missing_comparison: add the missing version. collect_more_data: complete the sample or task matching. quality_regression: inspect failures under your criteria.

latency_data_required: complete durations. latency_regression: the ceiling is exceeded. no_economic_advantage: cost per success is not lower. candidate_for_controlled_trial: prepare a limited trial.

## Prepare a controlled trial

Keep the data, configuration and report. Record what changed between versions, success criteria and any missing costs. Then define a limited trial population and duration.

The report contains automatic_deployment_authorized:false. A positive check triggers no model change, purchase or production deployment.

## What thresholds do not prove

These checks use observed rates. The 95% Wilson intervals are descriptive and assume independent tasks. They do not establish causality or a statistically proven improvement.

experimental_bias_control remains unknown: shared identifiers do not prove randomization. Evaluate your success criteria and task representativeness separately.

---

[Previous: Latency Lab: duration and retries](latency.md) · [Next: Reports and exports](reports.md)
