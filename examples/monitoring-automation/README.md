# Match the automation to the signal

This local lab models a small set of event and control decisions. It uses only Python's standard library, synthetic records and in-memory collections. It needs no AWS credentials, network calls, dependencies, Terraform, or retained files.

From the repository root, first predict what should happen to each case:

```sh
python3 examples/monitoring-automation/lab.py
python3 -m unittest discover -s examples/monitoring-automation -p 'test_*.py' -v
```

The packet contains two deliveries for one incoming S3 object version, an output object that must not retrigger the converter, one matching and one nonmatching EventBridge event, a CloudWatch alarm that enters `ALARM` and then receives a repeated `ALARM` observation, and AWS Config findings with different freshness and resource scope. Expected decisions are printed with short reason codes.

## What the model checks

- **S3 object work:** accepts only the configured incoming prefix and file suffix; identifies repeated delivery of the same bucket, key and version; rejects the derived-output prefix to prevent a trigger loop.
- **EventBridge-style routing:** matches a small exact subset of `source`, `detail-type` and `detail.state`. This is a teaching predicate, not a full EventBridge event-pattern engine.
- **CloudWatch alarm action:** distinguishes a transition into `ALARM` from receiving another observation while already in that state. The model tests state transition reasoning, not CloudWatch timing, metrics, notification delivery or Lambda execution.
- **Config remediation gate:** permits only an explicitly allowlisted resource with a fresh noncompliant result, a known action and attempts below a local cap. Stale, out-of-scope, compliant, unknown-action and exhausted-attempt cases stop. Those are extra safety gates in this local design model; they do not claim AWS Config provides all of them automatically.

The assertions are important: edit a fixture or gate and see which test fails. Change one item at a time and write down why the result changed. The tests prove only these local rules. They do not emulate AWS delivery guarantees, IAM, retry schedules, CloudWatch alarm evaluation, service scaling, SSM Agent, CloudWatch Agent, Route 53, ALB health, AWS Config or billing.

## Design prompts

1. The same object key is uploaded twice with different version IDs. Should the second version be processed, deduplicated, or compared with the first? State the business rule before changing the key.
2. Two different events share the same event identifier but come from different trusted producers. What scope belongs in the deduplication key?
3. A processing attempt fails after writing its output but before recording completion. What durable transaction or reconciliation strategy prevents either lost output or duplicate side effects?
4. The ALB health endpoint succeeds while the oldest repair request is overdue. Which additional customer-outcome measure is missing?
5. An AWS Config finding is 42 minutes old. What read-only observation would establish the resource's present configuration before remediation?
6. A queue grows while each worker uses little CPU. Which per-worker or wait-time signal could better represent demand, and what downstream limit must be checked before scaling?

Then read the separate [assessor notes](ASSESSOR.md) and the [illustrated lesson](../../reader/BOOK-LOCATORS.md#book-2bd946eff186b96f). Do not copy the fixture's caps or event identifiers into a production design.

## Try the crash window

Before running this, predict the number of payments and whether the worker will have a completion receipt in each case. A fictional worker and provider keep separate local SQLite files. The worker crashes after its first durable step, then retries:

- `receipt_after`: the provider records a payment before the worker records completion.
- `receipt_before`: the worker records completion before the payment is sent.
- `provider_key`: the provider accepts a stable key and the worker reuses it on retry.
- `changed_key`: the retry supplies a different key for the same intended payment.
- `changed_amount`: the retry reuses the key but changes the amount; the toy provider rejects the conflict.

```sh
python3 examples/monitoring-automation/crash_window.py
python3 -m unittest discover -s examples/monitoring-automation -p 'test_crash_window.py' -v
```

Explain why a completion receipt can exist with zero or two payments. Why must the worker leave a conflicting retry unresolved? How would the worker resolve a timeout whose result is unknown? This toy provider compares a key, operation and amount; it does not implement an actual payment API, concurrent workers, provider retention or reconciliation. Real provider guarantees and expiry differ. The temporary files are deleted after each case, and no network or AWS call is made. Compare with the [assessor notes](ASSESSOR.md#crash-window).

The program also prints four **fictional lookup observations** after a timeout. Predict the action before reading the output. A matching operation and amount can support recording a receipt; an authoritative absence can support retrying with the same key while its protection remains active. An unavailable lookup or a different amount leaves the outcome unresolved. Then change the key protection from active to expired or unknown: even with authoritative absence, this conservative model holds the retry for investigation. A confirmed matching result can still support a receipt after key expiry because no new payment is sent.

The model assumes the lookup can establish authoritative absence and that active key protection is known; a real provider may have delayed visibility, a limited key lifetime or no such lookup. Consult its contract and reconcile with an owner before acting; a missing search result alone need not mean no payment exists. These cases model decisions, not a real lookup or payment.
