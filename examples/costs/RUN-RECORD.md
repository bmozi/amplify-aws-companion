# One experiment, one cost and cleanup record

Copy this template outside tracked source before a real run. Keep private account/resource identifiers and billing evidence out of a public companion repository. Blank entries mean unknown, not zero or passed. This template is not authorization to deploy.

| Field | Record |
| --- | --- |
| Run ID, owner and learning question | |
| Source commit and infrastructure plan reviewed | |
| Account, region, caller identity and resource scope | |
| Plan/credit eligibility checked at UTC time | |
| Private per-credit terms receipt digest, review time and each selected service's eligibility or no-credit budget decision | |
| Current balance, expiry and protected reserve | |
| Price sources, region, date and exact units | |
| Quantity bounds: requests, retries, duration, concurrency, storage/retention | |
| A03 schedule mode, recurrence/end, delivery and Lambda retry limits (if opted in) | |
| Schedule inspector, interval, both failure queues, destination-delivery alarm and due-age check (if opted in) | |
| Subtotal, contingency and maximum estimated run | |
| Other experiments already consuming the same reserve | |
| Active-run ledger source, owner check time and zero-other-runs finding; recheck before a GitHub publication | |
| Expected start, stop and cleanup deadlines | |
| Publication stop procedure; Hosting and backend removal-or-retention choices; bounded retained-cost basis and deadline | |
| Actual start and last-work timestamps | |
| Stop conditions and responsible operator | |
| Actual usage counters, with source and time window | |
| Resources removed, removal status and reinspection time | |
| Schedule/group, dedicated tick Lambda, failure queues, async config and alarms removed (if opted in) | |
| Resources retained, owner, purpose, expected ongoing cost and removal date | |
| Shared resources excluded from deletion | |
| Billing observation time and covered usage window | |
| Usage cost before credits; credits/refunds separately | |
| Estimate-versus-observed difference and attribution uncertainty | |
| Later reconciliation due date and final disposition | |

The experiment is not fully reconciled merely because a destroy command succeeded or the immediate bill says zero. Keep cleanup status and billing reconciliation status separate. A later bill can include usage from before removal; investigate timestamps before calling it a continuing leak.

## Arithmetic practice before a real run

```sh
python3 examples/costs/lifecycle-exercise.py
```

This uses invented generic rates, an invented USD 80 balance and the existing calculator. Two versus 72 running hours change an estimate from USD 0.39 to USD 5.64 including contingency. The longer case fails both the USD 4 planning rule and USD 75 reserve. These are fictional calculations, not today's balance, AWS prices or a runtime cutoff.

A deliberately wrong unit still produces mathematically consistent output. The calculator cannot know that a typed per-request price was copied from a per-million quote. Verify the source, unit conversion and completeness independently.

For the opt-in A03 schedule, compare the [dated pending Ohio scenario](ohio-scheduled-due-tick-2026-10-19.json) with the actual plan before filling this record. Its public-rate arithmetic is USD 0.3741473750000 after contingency on invented quantities, while the account, operator and seven cost-driver decisions remain pending. The four added scheduled meters are Scheduler invocations, two failure-queue request lines and alarm-months. Standard SQS message retention has no separate GB-month charge; record applicable transfer or a chosen KMS key if the exact plan uses them. A priced example cannot stand in for current credits or an attended cleanup window. [AWS SQS billing FAQ](https://aws.amazon.com/sqs/faqs/).

## Practice interpreting delayed evidence

Use the [reconciliation challenge](RECONCILIATION-REVIEW.md) before completing a real record. It separates usage time from observation time, overlapping snapshots, retained resources and account-level credits. Its invented numbers are not a substitute for the account's current balance or resource inventory.
