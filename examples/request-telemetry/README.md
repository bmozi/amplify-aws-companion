# Follow a real local request and its alert

Run from the repository root:

```sh
python3 examples/request-telemetry/lab.py
```

Python's standard library starts three temporary HTTP listeners on loopback with OS-assigned ports: a frontend, a dependency and an alert receiver. Requests run sequentially. No AWS credentials, model calls or external recipients are involved. All listeners are stopped and joined in `finally` blocks; logs and receipts are in memory only. Run without `-O` so assertions execute.

Predict the observations before running:

1. A healthy dependency produces 200, a controlled unhealthy dependency produces 503, and restored health produces 200.
2. Each request has a fresh server-generated correlation ID, shared by its frontend and dependency events. The returned ID lets the client identify the matching pair.
3. The client sends a synthetic authorization value, query-string marker and proposed correlation ID. None appears in the recorded logs. This checks those fixtures and the allowlisted event fields, not every possible secret leak.
4. The alert receiver first rejects delivery with 503. A detected failure therefore exists without a delivery receipt.
5. Two later deliveries use the same event ID and receive 202 acknowledgments. The receiver retains one matching alert receipt.

The assertion checks that the receipt refers to the dependency's actual failed request. The program also reports measured frontend elapsed times; those measurements are tiny local samples, not production latency percentiles or a service-level objective.

A local HTTP acknowledgment is not proof that a human read a page or email. The receiver has no production authentication, durable storage, retry scheduler, concurrent deduplication contract or payload-hardening claim. The sender retries explicitly in the fixture. A crash loses its in-memory alert; this is not a reliable notification service.

The code uses a correlation field called `trace`, but it does not implement W3C trace context, spans, OpenTelemetry export, sampling or AWS X-Ray. No TLS, external DNS, CloudWatch alarm, SNS topic or real incident is exercised. The controlled dependency flag establishes the cause in this fixture; correlated events alone do not establish causation in an unfamiliar system.

For practice, make the receiver unavailable for the whole attempt and report delivery as failed rather than inventing a receipt. Then design a durable retry/outbox extension with a maximum age, bounded attempts and a separately monitored failure destination. Do not send real notifications as part of the local exercise.
