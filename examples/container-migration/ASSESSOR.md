# Assessor notes: container migration

A strong answer treats migration as an application and operating change rather than a packaging command.

- Inventory the current runtime and files before choosing a platform. A container image does not move the current machine's disk or memory with it.
- Move uploads and durable records behind an explicit storage contract. Design recovery, authorization and conflict behavior for a worker replacement.
- Treat in-memory sessions as process-local unless the application proves otherwise. A shared session store adds its own permissions, availability and lifecycle requirements.
- Keep credentials out of the image. Identify a secret delivery and rotation process and a separate runtime identity with only the required access.
- A nightly task that runs inside the web process needs an explicit scheduler, idempotency, overlap and failure policy. A container that starts does not prove the report runs once or completes.
- A required kernel module may justify EC2 or a changed application dependency; it does not automatically justify EKS. Select the narrowest platform that meets verified requirements and the team's operating capability.
- A new database schema should support the versions that overlap during rollout or have a tested migration/forward-repair plan. Rollback of the image cannot reverse an incompatible data write.
- The demo becoming customer-facing changes availability, monitoring, recovery, security and cost assumptions. It needs an owner-approved target and a representative rehearsal; one green health endpoint is insufficient.
- Pending malware/file validation belongs in the business publication contract. A successful upload is not permission to show the object.

Record image, configuration, infrastructure and schema identities together. Price old/new overlap, registry/storage, logs, load balancing, network, database and backup work. The exercise provides no AWS benchmark, target cost or migration authorization. The local Docker exercise is separate evidence and does not implement ECS/EKS.
