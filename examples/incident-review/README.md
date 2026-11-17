# Investigate the booking slowdown

This is a staged fictional incident, not AWS telemetry or an executable failure-injection lab. All times are invented UTC on one day. Do not change AWS, local networking or production resources. Read [unit 28](../../reader/BOOK-LOCATORS.md#book-48004aaa3a73ab7d), then answer each stage before opening the next evidence file. The files are available for learning, not access-controlled exam material.

## Stage 1: initial report

At 09:00, a rollout sends 20% of booking traffic to candidate v2; v1 remains active. At 09:01, customers begin reporting slow confirmation. Process-health probes succeed on both versions. At 09:02, the dashboard shows 12 late confirmations among 100 eligible completed bookings in the preceding minute. The chosen fictional target is completion within two seconds. Unfinished accepted work is not included in that completed-only view, and its size is unknown.

Write an initial impact statement, at least two competing explanations, one discriminating observation and a bounded immediate action. Explain why 12/100 is insufficient to describe all accepted work. Define what evidence would authorize expanding the rollout. Do not assume the candidate is either faulty or safe.

Open [stage 2](STAGE-2.md) only after recording your decisions. Keep your unaided reasoning before asking Codex for a challenge. Use [assessor notes](ASSESSOR.md) after both stages.
