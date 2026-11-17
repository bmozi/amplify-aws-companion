# Message boundary assessor

Keep this separate from the learner cases in [README](README.md#carry-a-trusted-tenant-label-across-a-message-boundary). The local result is a bounded demonstration, not a real security review or learner score.

1. The producer derives Shop A from its trusted membership lookup. It rejects Alice's conflicting `shop-b` request before writing accepted work. SQS has no knowledge of Alice's membership; the group is metadata supplied by the producer.
2. The accepted request row persists in SQLite, and a reopened fixture lists it through `pending_envelopes()`. A real publisher needs a retryable send record and delivery protocol. An uncertain send can have succeeded, and a standard queue can also redeliver; consumers must handle duplicate work.
3. The acceptance and effect keys are `(tenant, request_id)`, so Shop A and Shop B can both use `same-id`. A global request-ID-only key would collide. The database lookup and every downstream effect must retain tenant scope.
4. No. The fixture's SQLite transaction covers only its local effect table. Email is outside that transaction. An explicit delivery record or external provider idempotency/reconciliation path is needed, with honest handling of ambiguous acknowledgements. Do not claim exactly-once email from an exactly-once local row.
5. Either policy can be coherent if documented and enforced. A user-delegated action may need a fresh membership check and cancellation policy; a tenant-owned accepted workflow may continue after the individual leaves. The chosen policy belongs at acceptance and execution, with auditable state transitions. This fixture models neither revocation nor a live worker identity.

For review, mutate the local fixture deliberately: copy `claimed_tenant` into `MessageGroupId`, remove the tenant from the primary key, or insert a second effect after duplicate delivery. Each should violate a named case or test. Passing the current tests only covers the listed local boundaries; it does not prove authenticated SQS producers, worker IAM, SQS fairness, external-effect safety, or representative latency.
