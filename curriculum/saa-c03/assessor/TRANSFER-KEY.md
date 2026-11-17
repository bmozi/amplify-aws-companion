# Transfer assessor — review after submission

Internal rubric only; no independent reviewer or learner calibration yet. For each case record four separate judgments: (1) initial requirement and mechanism, (2) justified alternative rejection, (3) response to the changed fact, (4) evidence limits. Use supported / incomplete / contradicted with a passage-specific reason, not a made-up exam score. An explanation that violates a stated security or recovery constraint needs remediation regardless of other correct details. Accept alternative designs when they satisfy every supplied constraint and their assumptions are explicit.

## SAA-T01 — task 1.1

Require scoped temporary access, independently reasoned caller trust and resource permissions, explicit prefix/read scope and a negative test outside that scope. A shared employee key fails attribution and boundary separation. The changed case needs confused-deputy analysis and an appropriate customer-binding mechanism such as a correctly enforced external ID for the third-party role path; do not treat that ID as a password or as a replacement for principal trust.

## SAA-T02 — task 1.2

Identify missing object/tenant authorization, not a missing private route. Bind the authenticated principal to each accessed record and test forbidden identifiers through all relevant paths. WAF may filter configured attack patterns, but input handling, parameterized queries and record authorization remain application responsibilities. No network-only repair can prove tenant isolation.

## SAA-T03 — task 1.3

Require recoverable data, surviving decrypt authority, usable key lifecycle and a tested restoration path. Demonstrate restoration and business reconciliation using the intended recovery identity. Longer retention changes legal/owner policy, key and identity continuity, service lifecycle, archival retrieval, format readability, cost and recovery timing; encryption does not by itself supply retention or restore.

## SAA-T04 — task 2.1

Explain the commit/ack gap and possible duplicate effect. A timeout can reduce overlap but cannot eliminate crash redelivery. Persist stable business/operation identity and status; use the provider’s documented key scope and retention, record provider references, query uncertain outcomes and define reconciliation. Do not promise exactly-once effects solely from queue choice.

## SAA-T05 — task 2.2

Do not accept RTO from DNS and replication alone. Require recovery identity/key/network/capacity dependencies and measured customer acceptance within the clock, with RPO reconciliation. Ten requests show bounded behavior only, not production peak or degraded-region capacity. A repeatable representative test and declared limits are needed.

## SAA-T06 — task 3.1

Evaluate an appropriate FSx for Windows File Server configuration for SMB/directory needs and S3 for the object workload; do not claim EFS NFS is a drop-in SMB replacement. Verify exact feature, directory/network integration, throughput, concurrency, availability and restore using representative operations. A shared service is not mandatory merely because both workloads store bytes.

## SAA-T07 — task 3.2

More workers can increase throttling and retry load without raising completions. Measure arrival/completion rate, age, concurrency, downstream limit, latency and retries; bound requests and use appropriate backoff. After the bottleneck changes, compute sizing or worker scaling may help, but verify achieved throughput and downstream headroom rather than repeat the old diagnosis.

## SAA-T08 — task 3.3

Separate the confirmation freshness promise from the report tolerance. Route the required authoritative read or implement an explicitly validated consistency mechanism; do not assert asynchronous replication has zero lag. During failure, report load redistribution can overwhelm the writer; define priority, limits, delayed reporting and tested capacity. A replica fixes neither all write bottlenecks nor all failover load.

## SAA-T09 — task 3.4

Evaluate Global Accelerator for the network entry/routing requirement and CloudFront for HTTP content caching, checking supported endpoints and actual behavior. Neither is a universal replacement for the other. A dedicated connection is not itself proof of the required encryption; specify the supported encryption design, endpoints and acceptance evidence for the hybrid path.

## SAA-T10 — task 3.5

Distinguish AppFlow for a supported SaaS connector, MSK for Kafka, appropriate transformation plus Glue catalog, Athena query and Quick Sight presentation. Alternatives are acceptable with a justified requirement fit. Reconcile source identities/counts and event-time windows, reject or version incompatible schemas, handle duplicate/late data and govern access. A dashboard refresh is not evidence that the dataset is complete.

## SAA-T11 — task 4.1

A totals 125; B initially totals 155, so A is lower. With B retrieval 10, B totals 85 and becomes lower. These are fictional units, not prices. Verify exact class/Region, bytes, requests, minimum size/duration, monitoring, retention, transfer, recovery and access behavior. Do not compare only storage.

## SAA-T12 — task 4.2

On-demand totals 1000 versus commitment 840 for ten months; with six months on-demand is 600 versus commitment 840. Fixed obligation creates utilization risk. These are invented totals, not AWS quotes. Check eligibility, actual term/payment, price basis, changes in workload or architecture, other charges and capacity separately; discount does not promise capacity.

## SAA-T13 — task 4.3

Compare representative query/write mix, peak and skew, index write/storage work, replicas, backup, connection/transfer charges, migration and operating effort while preserving correctness. The changed access pattern undermines a decision based on fixed keyed queries; reconsider engine/model rather than merely buy more capacity. A declared average is not measured cost or performance.

## SAA-T14 — task 4.4

The supported S3 route can avoid the NAT path after route and access configuration, but the endpoint does not provide general external API egress. Retain or replace the latter deliberately. Demonstrate surviving AZ routes, capacity, permissions, dependency access and costs. Do not infer internet reachability or resilience from successful S3 reads alone.
