# Spend Proof: cost per success

Include failures and retries to compare the cost of recorded outcomes.

[Documentation library](README.md) · [ALPNAI](https://alpnai.com/en/docs)

[Français](../fr/spend-proof.md) · [English](../en/spend-proof.md) · [Deutsch](../de/spend-proof.md)

## The data format

Each row represents an attempt: task_id, workflow, variant, cost_usd and success are required. latency_ms is optional. Field names remain in English in every language.

This two-row example shows the format; it does not meet the default requirement of 30 distinct tasks per version for a comparison.

```json
{
  "runs": [
    {
      "task_id": "task-01",
      "workflow": "invoice_fields",
      "variant": "baseline",
      "cost_usd": 0.04,
      "success": true,
      "latency_ms": 2200
    },
    {
      "task_id": "task-01",
      "workflow": "invoice_fields",
      "variant": "candidate",
      "cost_usd": 0.025,
      "success": true,
      "latency_ms": 1600
    }
  ]
}
```

## Which costs to include

Include model, tool, retrieval and other call costs needed for the attempt. Record failed attempts too. Convert all values to USD before import.

cost_usd accepts at most six decimal places. Aggregate finer-grained costs correctly upstream. A string such as "0.04" is not a number and is rejected.

## How cost is calculated

Attempts are grouped by workflow, variant and task_id. A task is considered successful if at least one recorded attempt has success:true. All its costs count.

Cost per successful task = total attempt cost ÷ successful tasks. With no successes the result is null: a finite cost per success cannot be calculated.

## A comparable monthly projection

monthlyTasks is the monthly number of tasks launched by the baseline. It can be used for one workflow only. The projection then compares the same expected volume of successful results.

It appears only for a candidate eligible for a controlled trial. It excludes integration, migration, evaluation and the business value of errors. realized_savings_usd remains null: a projection is not realized savings.

## Prepare a sound comparison

Use exactly the same task_id values for both variants and the same definition of success. A task_id cannot belong to multiple workflows. Separate environments or test sets before export.

Duplicate rows count as additional attempts. Deduplicate telemetry upstream. The engine cannot detect a missing bill or prove that your sample represents every customer.

---

[Projects: private reports and subscriptions](projects.md) · [Latency Lab: duration and retries](latency.md)
