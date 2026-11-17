# A recovery clock follows the customer

Maya cannot read a confirmed booking when the source endpoint fails. A candidate endpoint responds, but it is missing that booking. The operator must reconcile the candidate, close the old writer and move the selected route before a correct customer read can end this local clock.

This lab uses loopback HTTP and temporary SQLite files on one machine. It changes no AWS resource and has no cloud charge. The event durations are actual local elapsed milliseconds for this run; they are **not** an AWS recovery-time objective (RTO), recovery-point objective (RPO), DNS propagation measurement or production service-level result. The key check and writer fence are cooperative fixture flags, not KMS or distributed controls.

## Predict before running

Follow the [five-job architecture figure](../../book/figures/recovery-controller-jobs.svg) in the chapter. Write an answer to each question before reading the event record:

1. Booking `111` was confirmed for 2,300 cents in the source and journal but is absent from the candidate copy. If `/candidate/health` returns 200, may a customer safely resume there?
2. Which event ends the measured interval for the promise “a customer can read the confirmed booking again”: the candidate health response, reconciliation, route switch, or the first correct customer read?
3. Suppose the candidate is reconciled, but the old source writer is still open. May the operator switch? What could two writable copies do to the last seat?
4. After the candidate accepts booking `112`, an old-address client reaches the returned source and gets 404 for `112`. What can the operator claim about *all* customers?

## Run and inspect the local record

From the repository root:

```bash
python3 examples/regional-recovery/failover_timeline.py
python3 -m unittest discover -s examples/regional-recovery -p 'test_failover_timeline.py' -v
```

The command emits a `reviewed` run and an `old_writer_open` changed case. Follow `events` in order. The first run records a baseline 200, a failed customer read, a healthy but incomplete candidate, a local reconciliation, a route switch, the first correct read, a new confirmed booking, and a 404 on one pinned old path. `failure_to_correct_read_ms` uses the first failed request and the first correct read. The second run reconciles the candidate but returns `HOLD` when the cooperative old-writer flag remains open; it has **no** recovery duration or correct-read event. Values vary with the host and scheduler. Do not compare them with a real business target.

Change one fact on paper: the candidate has booking `111`, but its amount differs from the trusted journal. Which event should disappear from a valid run, and what evidence would resolve the discrepancy? Do not silently overwrite either value. Then change another fact: the selected route works, but a material share of clients retains the old address. Specify the clients, old-path requests and time window you would need before claiming recovery for that population.

For a future authorized AWS experiment, choose a narrowly scoped target, a steady-state customer metric, an independent observation path, a tested stop and recovery operator, data reconciliation, old-writer denial, old-client behavior, capacity, a full-run estimate and cleanup inventory. [AWS FIS stop conditions](https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html) use CloudWatch alarms and stop an experiment when a defined threshold is reached; [stopping an experiment](https://docs.aws.amazon.com/fis/latest/userguide/stop-experiment.html) does not itself prove that bookings are correct again. Route 53 can use health checks for [DNS failover](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html), but this local route variable is not DNS. A separately authorized cloud run needs account-appropriate spending and reserve limits, explicit scope and post-run reconciliation. Organization-dependent variants remain design-only unless separately authorized in a suitable environment.

Ask Codex to make a two-column event table: what the record proves, and what a real customer or AWS claim would still need. Challenge it with the old-address 404 and the held writer case. Compare your first answer with the separate [assessor](TIMELINE-ASSESSOR.md) only afterward. The two local tests verify the intended event order and hold behavior; they do not measure independent learner understanding.
