# Container migration design exercise

Use this design worksheet with [Unit 15](../../reader/BOOK-LOCATORS.md#book-0d0c5baa7fa4744a). It adds no AWS resource, does not build an image and does not move application data. Use fictional or sanitized requirements only.

## Starting situation

A small repair company runs an API on one long-lived virtual machine. The application writes uploaded photos to a local directory, keeps recent user sessions in process memory, calls a PostgreSQL database, and runs a nightly report in the same process. Operators update the code by copying files and restarting the service. The company wants a repeatable release and the ability to replace a failed worker.

## Work through the checkpoints

1. List runtime, OS, libraries, ports, startup/shutdown, scheduled work, local files, session state, secrets, outbound connections and database dependencies. Mark what is observed versus assumed.
2. Decide which state must outlive a task. Propose where uploads and sessions should live, how a failed copy is detected, and how duplicate or partial work is handled.
3. Define a minimal image and its configuration boundary. Name how its identity, dependency inputs and vulnerability evidence will be recorded. Never include secrets or durable customer records in the image.
4. Compare a single container on the current host, ECS on Fargate, ECS on EC2 and EKS only where a requirement makes each a candidate. Identify who owns host, scheduler, application, data, network and upgrade work.
5. Plan a rehearsal: representative request, upload, session lookup, scheduled report, health check, permission denial, process stop, database unavailability and log review. Identify observations and rollback triggers.
6. Plan a staged release with old/new overlap, schema compatibility, copied files, traffic movement, recovery and retirement. Include both environments and data movement in the cost estimate.

## Changed cases

- The application requires a kernel module available only on the old host.
- Session data must remain valid when requests reach any replica.
- The database schema change is not readable by the old version.
- A low-traffic internal demo now becomes a customer-facing service with a five-minute recovery target.
- Uploads complete, but a later scanner or image processor has not yet approved them.

For each change, revise the plan and name what evidence would reverse the decision. Read the [assessor notes](ASSESSOR.md) only after recording your reasoning.

Ask Codex to find hidden machine-local state, unsafe overlap and unpriced dependencies. Require it to distinguish local tests from managed-service behavior. The exercise does not perform a cloud migration.
