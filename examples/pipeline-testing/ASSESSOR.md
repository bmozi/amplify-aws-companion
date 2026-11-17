# Test the requirement: assessor notes

This is an internal discussion guide, not an exam answer key or calibrated score. Read it after running the lab and recording the learner's first prediction.

## Expected observations

| Run | Unit | Integration | Acceptance | Why the gate stops |
| --- | --- | --- | --- | --- |
| Default | Pass | Pass | Pass | All three local requirements hold |
| `--fault consent-bypass` | Pass | Fail | Not run | The isolated rule is correct, but the service ignores it and persists a message without consent |
| `--fault wrong-message` | Pass | Pass | Fail | The service and outbox operate, but the customer-visible message violates the appointment requirement |

The consent rule's unit test calls `ReminderRules` directly. It does not call the full service, so it cannot find a defect where the service skips that rule. Integration tests combine the service and database and check that a denied action leaves no record. The acceptance test crosses the local HTTP boundary and checks both the response and the exact persisted customer result. The stage runner stops on the first failing suite, as a candidate release pipeline should stop at a failed required gate.

## What this exercise does and does not show

The harness runs real local Python code, a local SQLite database and a loopback HTTP server. The injected faults are in the actual execution path. The results show that test scope determines what behavior is observed; they do not prove that these test names alone make a pipeline safe.

The exercise does not implement a browser, SAST/DAST engine, identity provider, notification provider, load generator, resilience controller, AWS service or production pipeline. A request accepted by this local toy API is not proof of customer delivery. Local process exit codes are used by the runner to stop or continue, but they are only signals for these local test commands. Cloud build systems need explicit handling for test reports, timeouts, retries, cleanup and the meaning of a skipped or inconclusive result.

## Strong answers

- Connect each test to an explicit requirement and observable result, rather than equating a green build with correctness.
- Identify the false-confidence gap in mocked or overly narrow tests and the additional boundary exposed by the next layer.
- Retain both positive and negative cases so that an always-deny or empty implementation cannot pass.
- Place fast, deterministic checks early. Run provisioned integration and customer-journey checks in an isolated environment. Use performance, destructive resilience and security tests with scoped data, permissions, duration, cost and stop conditions appropriate to their risk.
- Treat static security findings as leads to triage, not proof of exploitation or proof of safety. Treat an untested path as unknown, not clean.
- Name the AWS-specific follow-up: selected service wiring, effective test identity, representative configuration/data, complete cleanup, bounded estimate and observed failure handling.
- This lesson does not authorize a load or fault-injection test; select and approve an appropriate test environment before any such run.

No independent learner has attempted this exercise. The reported local run is an implementation check, not evidence of reader learning or deployed AWS behavior.
