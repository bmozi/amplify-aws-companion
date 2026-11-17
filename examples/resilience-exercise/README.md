# Stop the fault, then prove the shop can work

Maya wants to know whether the booking service can survive a slow worker. Customers must not receive two appointments when they retry a request. The team proposes delaying one worker in a dedicated synthetic lab. Before touching that worker, they must decide what they expect to learn and what would make them stop.

This is a **tabletop exercise**, not an executable fault injector or an AWS experiment record. All times, thresholds and observations below are fictional. No account access, infrastructure or spending is required. Write your decisions before opening [the assessor notes](ASSESSOR.md).

## Draw three paths

```text
Synthetic customer -> booking API -> lab worker -> booking records
                           |
                     result observer

Experiment operator -> fault controller -> selected lab worker

Recovery operator -> stop control
                  -> service repair
                  -> booking reconciliation
```

The fault controller deliberately creates a problem. The observer checks what a customer experiences. The recovery operator stops the experiment and verifies the business result. These are different responsibilities even when one learner performs all three in a local exercise.

A stop button reached only through the worker being disrupted would be a poor escape route. Draw the actual authentication, network and service dependencies of the observer and recovery path. Separate boxes do not prove independence: they may still share credentials, a network route or a failed dependency.

## Make a bounded promise

For this fictional lab, the proposal is:

- Target exactly one named worker in a disposable environment. No customer records, real payments or production targets are permitted. Resolve the target and inspect its identity before beginning; a broad tag match is insufficient evidence of a single target.
- Inject a delay for at most 60 seconds. Send at most 30 synthetic logical booking requests, with at most one retry per request. A retry retains its original request identity. Count attempts separately from logical bookings.
- Hypothesis: accepted requests remain single bookings despite retries, and useful service is restored within 120 seconds of the first observed customer failure.
- Before starting, demonstrate a baseline of correct bookings and fresh observations, verify recovery access, and agree who can stop. No baseline, missing telemetry, unexpected target or unavailable recovery operator means **do not start**.
- Stop immediately on a duplicate confirmed booking, an observation more than 20 seconds old, an unexpected target, or an operator's stop request. Also stop at the duration limit. These are teaching rules for the proposed controller; they are not claims about AWS defaults.
- Accept recovery only after two consecutive 20-second windows of correct new synthetic bookings, reconciliation of every accepted request identity, no duplicate confirmations, and no remaining injected delay. Reconcile capacity as well as row counts. The small sample is a teaching criterion, not a production reliability estimate.

A time limit bounds deliberate injection, not every resulting consequence. A queued retry, an incorrect record or a failed worker can remain after injection ends. Name the repair and reconciliation steps separately. Do not automatically start another experiment because the previous one stopped.

## Packet 1: decide whether to begin

The selector resolves two workers: `booking-lab-1` and `booking-shared-1`. The second worker handles another team's test environment. The observer's last successful sample is 35 seconds old. The operator says, “The fault lasts only a minute.”

Write a go/no-go decision and identify each failed precondition. Specify what evidence would allow reconsideration. Explain why a short duration does not repair an uncertain target or a blind observer.

## Packet 2: follow the clocks

Assume the preconditions have now been met in a new fictional run. Read one row at a time; record your decision without using later evidence.

| Time from start | Supplied observation |
| --- | --- |
| 0 seconds | Fault begins on the single reviewed lab worker; observer is current |
| 10 seconds | First customer request times out; its retry uses the same logical request ID |
| 20 seconds | Observer detects two confirmed bookings for that ID; operator requests stop |
| 25 seconds | Fault controller reports stopped; duplicate records still exist |
| 40 seconds | Worker serves requests again; one customer still has two confirmations |
| 60 seconds | Reviewed repair reconciles all accepted IDs and capacity; injected delay is absent |
| 80 seconds | First 20-second post-repair window has correct new bookings |
| 100 seconds | Second such window passes; reconciliation still matches all accepted IDs |

Calculate detection time from first observed failure, stop-request-to-stopped time, and failure-to-accepted-recovery time. State whether the 120-second recovery target was met and whether the entire hypothesis was met. Explain why those answers can differ. This is arithmetic on supplied evidence, not a measured RTO.

## Packet 3: silence and partial recovery

In a different run, the observer stops producing samples at second 10. At second 35 the dashboard still shows its last green result. The worker's process is running. The fault controller is reachable through a separate, previously checked access path.

Decide what to do under the stated rules. Name what the dashboard cannot establish. After stopping, a health endpoint returns HTTP 200 but the reconciliation source is unavailable. Decide whether to reopen the service, continue verification, or declare success. Explain what additional business constraint would determine whether a limited read-only mode is acceptable.

## Map the design to AWS without pretending it is deployed

AWS Fault Injection Service (FIS) can use CloudWatch alarms as experiment stop conditions. Choose the service's steady-state metrics and unacceptable thresholds before creating the condition. A configured alarm is not proof that its metric arrives, its threshold is appropriate or its missing-data behavior meets our stale-observation rule. That rule needs an explicitly designed and tested implementation. [AWS FIS stop conditions](https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html).

FIS distinguishes `stopping` from `stopped`. Its stop procedure completes outstanding post actions before stopping. Read the selected action's documented behavior before assuming which effects will be undone. Independently verify workload and business recovery. [Stopping experiments](https://docs.aws.amazon.com/fis/latest/userguide/stop-experiment.html), [experiment states](https://docs.aws.amazon.com/fis/latest/userguide/view-experiment-progress.html).

A future AWS lab needs a reviewed scoped experiment role, exact supported action and target, tested alarm and manual-stop access, measured observation delays, and a cleanup inventory. Include the workload, monitoring, retries, retained logs and fault service in the estimate. Choose spending and reserve limits from the account that would host the experiment, and recheck actual costs afterward. This worksheet does not authorize or provision that future run. Organization-dependent variants remain design-only.

## Transfer and AI review

Change the case: instead of a slow booking worker, a queue consumer stops after sending a confirmation but before acknowledging its message. Identify the side effect that restarting the consumer cannot undo. Revise the hypothesis, request identity, observation and reconciliation requirements before choosing a fault tool.

Ask Codex: “Review my experiment card and fictional timeline. Identify each assumption needed to stop, each missing observation, and every business effect that stopping does not reverse. Separate supplied evidence from inference. Do not execute anything.” Check its timing calculations and challenge any claim that green infrastructure means correct bookings.

The [local canary drill](../canary-release/README.md) exercises an actual response-path rollback, and the [reconciliation drill](../recovery-reconciliation/README.md) checks local restored records. They provide related component evidence, not an integrated FIS platform or a test of this worksheet's timing. Live fault and recovery behavior requires separate testing.

The separate [A22 loopback experiment](LOCAL-LAB.md) runs a tiny synthetic booking server through an actual HTTP timeout, operator stop, same-ID retry and business-record check. Its six tests include a broken-retry negative control that remains wrong after the fault stops. The [process-replacement extension](PROCESS-LAB.md) commits to a same-host SQLite file, terminates the first worker, retries through a new worker and races two workers against one ID. Its three additional tests include a broken retry rule. These local observations do not satisfy the tabletop's fictional timing goal or prove AWS recovery.
