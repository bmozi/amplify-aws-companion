# Refuse excess work without losing the available worker

Run from the repository root:

```sh
python3 examples/admission-control/lab.py
```

Python's standard library starts one temporary loopback HTTP server. A semaphore permits one business operation at a time. An event holds the first request inside that operation while a second real HTTP request arrives. This creates controlled overlap without relying on a sleep to guess whether the first request has started.

Predict the result: the process-health endpoint returns 200, but the second business request receives 503 with an explicit statement that work was not accepted. The first request is still active. Releasing it allows another operation to return 200. An injected worker failure then returns 500; a subsequent operation returns 200 because `finally` returned the capacity slot. The server and client threads are closed before exit. Run without `-O`.

This fixture has no side effects, authentication, durable queue or retry scheduler. In this particular implementation, the overload rejection occurs before business work. A network timeout or an arbitrary production 503 does not establish that nothing happened. An application with side effects needs its own request identity, reconciliation and safe-retry contract.

The bound applies to the business-operation slot, not HTTP connections or server threads. Python's teaching server still creates request threads. This is not a production protection against connection floods, a global concurrency limit across replicas, an AWS throttling test or a load benchmark. Production designs must bound each relevant layer and measure queueing, fairness and rejected traffic.

For a negative control, make a temporary copy and remove the final slot release. The post-release success assertion should fail. Do not change the checked-in fixture to turn a failure into a pass. Then explain why a controller that restarts the process whenever one request gets 503 might harm the still-running request.

Ask Codex to trace exactly where work is admitted and where the slot is released. Have it identify the difference between overload rejection, admitted-work failure and an unknown outcome after a client disconnect. Verify its explanation against the code and output. Independent learner responses remain uncollected.
