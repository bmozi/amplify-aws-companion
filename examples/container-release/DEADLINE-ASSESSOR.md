# Stop deadline assessor notes

Keep this page separate from the learner's first attempt. The exercise is a local process model, not an ECS or customer-system measurement.

## Expected distinctions

- **0.4-second work, three-second stop window:** the process has enough time in this observed run; the client receives the fixture's 200 response and the process exits zero. The evidence is the response and log order, not the timeout settings alone.
- **Four-second work, one-second stop window:** the harness forces a kill after the window; the client connection breaks and the process exits by signal. A disconnected client has no evidence of a durable business result from this fixture.
- **Changed 2.5-second work, two-second window:** predict likely interruption under the same timing, but do not call it guaranteed without a run. Request admission time, shutdown scheduling, signal handling and system load can shift the observed result. If the operation had a durable or external effect, inspect its authoritative record and request identity before retrying.
- **No false completion:** a zero exit, an HTTP 200, and a persisted business effect are different observations. This service has no persisted effect, so no answer may claim one. A process kill also cannot prove a real operation was rolled back.
- **AWS transfer:** an ECS stop plan needs selected task, target-deregistration and application behavior plus client/business measurements. This local script establishes none of those AWS facts.

A strong learner answer names the evidence it would collect for a real workload: duration distribution under representative load, in-flight count at stop, client status, retained work identity, authoritative outcome lookup, retry/duplicate behavior, and the actual platform stop sequence. It compares the extra overlap/retention cost with the customer promise before choosing a window. Merely lengthening the timeout is not a complete remedy.

## Local evidence boundary

The October 22 author run of `python3 examples/container-release/deadline_lab.py` observed one 200 response and graceful exit in the short case, and a disconnected client with process exit -9 in the long case. This is an internal fixture result. No independent learner attempt, Docker replacement run for this specific timed endpoint, ECS deployment, AWS cost, or real customer result is recorded here.
