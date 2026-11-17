# Multi-tier architecture design

Read [Unit 01](../../reader/BOOK-LOCATORS.md#book-20a32f2d1ab40bbb) and its figure first. Tiers describe responsibilities and access boundaries; they do not mandate one server per box. These cases are design-only and create no network, load balancer or database.

For each case draw who may call which component, where data becomes authoritative, which failure crosses a boundary and what measurable requirement justifies each additional tier. Draw **application subnets** only around resources placed in your VPC. Label SQS and S3 as managed services reached through their APIs, even when a VPC endpoint gives the application a private route to them.

## Cases

1. **One small internal tool:** A nearby five-person team uses a form that already meets its response and availability needs. Is a separate CDN, load balancer, application subnet and database subnet useful? Name a business change that could make one boundary worthwhile.
2. **Public repair API:** Customers upload a photo and check repair status. Design a public entry, application authorization, private data access and file storage path. State which component checks record ownership and which one only filters network traffic. Place the object store outside application subnets, and decide whether the selected compute needs VPC access at all.
3. **Long-running image work:** The API must acknowledge a valid upload quickly, but image processing takes several minutes. Show the queue/worker path, state transitions, retry identity and result storage. Explain why an accepted message is not a completed repair. Mark SQS as a managed service outside the application subnet; if a private VPC route is needed, name the endpoint and its cost/permission review separately.
4. **A new private report:** A report joins the database and is too slow for customer requests. Add a reporting path only if justified. Identify data freshness, privacy, network reachability, source load and report recovery requirements.

## Boundary test

Change one fact after drawing the initial design: the report includes private fields, the application moves to two Availability Zones, a worker may be interrupted, or the internal tool becomes public. Update the diagram and explain each new access path. Do not simply add another AWS service name.

For the image-work design, change one more fact: the database commits the accepted job, then the process stops before it sends the queue message. The customer has a receipt, but no worker has heard about the job. Show where a durable obligation to send work lives, how a later sender finds it, what happens if that sender retries after an uncertain reply, and how an operator notices a job that remains pending. Explain which action is atomic with the database record and which crosses the queue boundary. Do not claim that saving a database row and sending a message are automatically one transaction.

After writing your answer, use the [local outbox model](../modernization-targets/README.md) to see a related booking example. It rolls back a failed booking transaction and repeats a delivery after a lost acknowledgment. A separate test commits a pending row to a temporary SQLite file, exits the writer before its first send, and has another process deliver it. That local restart is not a machine crash, durable AWS queue or proof of a production recovery path.

Ask Codex to challenge the diagram: “Which flow is not required? Which network permission could be confused with business authorization? Which new tier adds cost or a failure point without solving a stated requirement?” Verify the reasoning yourself. The exercise is not a deployed topology.

After finishing your own four designs and one changed-condition redraw, compare them with the [reference reasoning](ASSESSOR.md). It supplies defensible examples and reversals, not a single mandatory AWS topology or a score for a real learner.
