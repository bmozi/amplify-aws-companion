# A22 loopback fault stop and booking receipt

Maya submits one synthetic appointment request. The lab worker records it, then waits long enough that her local HTTP client gives up. From her screen, the outcome is unknown: the missing reply does not say whether the booking was written. An operator stops the deliberate delay, and Maya retries with the **same request ID**. The useful question is whether she now has one booking or two.

Run from the repository root:

```sh
python3 examples/resilience-exercise/local_lab.py
python3 -m unittest discover -s examples/resilience-exercise -p test_local_lab.py -v
```

The run starts a loopback HTTP server on an ephemeral `127.0.0.1` port and shuts it down afterward. It uses invented names and in-memory records; there is no AWS call, external network listener or AWS cost. The controller accepts only the named `booking-lab-1` target, a fresh observer and a ready recovery operator. The injected reply delay is at most 0.25 seconds; duration and request-attempt limits also bound the fault. The exercise uses short durations so it can be repeated locally. They are **not** the tabletop's fictional 60-second/120-second targets.

Read the JSON receipt in this order:

1. A baseline booking succeeded before injection.
2. `first_customer_outcome` is `timeout`. The worker wrote before delaying its reply, so the client cannot infer that from its timeout alone.
3. The operator stops further delay. The retry uses `fault-1` again and finds one record for that logical request.
4. Two new synthetic bookings succeed. `observed_failure_to_second_probe_seconds` is measured local wall time from the first timeout to the second new response. It is not a cloud or customer RTO: the observer, controller, server and records share one process.
5. `hypothesis_met` requires the single retried booking, correct new probes and no active injected fault. It says nothing about another process, a durable database, a real queue or AWS Fault Injection Service.

The test suite includes a deliberate **broken retry rule**. With that rule, the delay stops and new requests work, but the same logical request gets two bookings. The result must reject the hypothesis. Other tests veto a shared-worker target, a multi-target selector, a stale observer and an unavailable recovery operator; reject a changed customer on a reused request ID; and stop a fault when its attempt cap is exceeded. These are local negative controls, not permission or cloud-failure tests.

Before reading [assessor reasoning](LOCAL-LAB-ASSESSOR.md), answer these changed cases:

1. The first timed-out request did **not** reach the record store. How would the retry result change, and why must the caller still retain the same ID?
2. The record store commits a booking, but the observer's `/audit` path is stale. May an operator claim one booking from two green new probes? Name the missing evidence.
3. The delay stops after the first customer timeout. The negative-control store contains two rows for `fault-1`. What must be reconciled before customer recovery can be claimed?
4. The controller accidentally selects a shared worker. Which precondition stops the run, and why does a 0.25-second fault limit not make the selection safe?
5. Move the worker to another process and the record store to DynamoDB. Which local claims survive as design hypotheses? What authenticated, concurrent, timed and cost observations would be needed for an AWS result?

Ask Codex to review your experiment card **before** running it: identify the exact target, observer freshness, stop access, stable request identity, contradiction and recovery receipt. Then compare its predictions to the JSON and tests. Challenge any answer that equates stopping the delay with erasing a booking. The [A22 tabletop](README.md) and [Unit 24](../../reader/BOOK-LOCATORS.md#book-56c900b7f81568d4) keep the broader fault-tool, operator and AWS boundaries visible. This local exercise makes no AWS call or charge.
