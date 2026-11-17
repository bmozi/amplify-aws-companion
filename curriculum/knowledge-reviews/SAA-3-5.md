# Analytics and ingestion knowledge review: SAA-C03 task 3.5

Internal editorial review, October 18, 2026. All seven current knowledge bullets in the [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task5) matched their stored hashes. Numbers below are editorial inventory positions, not AWS-issued objective identifiers. Seven entries now have partial mappings; no full task or certification coverage is established.

## Knowledge 04 — Transformation service use cases

Reviewed unit 14's “Choose processing compute from the shape of the work” and its scheduler/engine distinction, service overlap, decision table and changed-workload discussion. The lesson describes Glue's integration/catalog/transformation role, compares Batch scheduling and EMR framework requirements, and retains a simple worker as a legitimate choice for bounded work. It requires input/output contracts and runtime compatibility before performance claims.

The six processing-selection cases and separate assessor notes require a candidate, rejected alternative, operating owner, cost drivers and evidence that would reverse the choice. Case 2 addresses repeated integration of cataloged customer/sales sources; cases 1, 3 and 5 prevent a blanket “all data jobs need Glue” answer. Cases 4 and 6 distinguish skew and end-to-end delay from average compute duration. These assess service-fit reasoning rather than mere recognition of a product name.

The CSV/Parquet exercises supply actual local value-preservation checks, but they do not implement Glue connectors, job configuration, distributed transformation or cloud publication. Selected runtime/dependency support, representative performance, failure/retry behavior, authorization and observed cost remain open. The appropriate status is partial design knowledge with separate bounded local evidence, not implemented service mastery.

## Knowledge 07 — Streaming service use cases

Reviewed unit 14's “Choose what each consumer must receive” and adjacent checkpoint/backlog sections. The comparison connects retained Kinesis history to independently progressing applications, a work queue to competing workers, and batch to a deadline that permits scheduled collection. It distinguishes a stream position from a business-event identity and calls for recovery margin beyond nominal replay history.

Ingestion case 1 challenges unnecessary continuous processing; case 2 challenges the claim that competing applications both receive every sale. Cases 3–5 require reasoning through early progress, duplicate replay and out-of-order completion. The changed requirement adds a week of recomputation, output versioning and protection against repeating customer-facing effects. Assessor criteria in the individual-skill review require independent histories, reconciliation and bounded retention reasoning.

The local checkpoint lab demonstrates actual child-process failure and restart around SQLite effects. That is useful evidence for the failure concept, not a Kinesis client, service guarantee or production retention test. Stream configuration, partition/key distribution, producer access, measured per-consumer lag, real replay and cost evidence remain open. No learner has independently completed these cases here.

## Knowledge 05 — Secure ingestion entry

Unit 14 now adds “Decide who may submit a business fact,” separating authentication, action/resource permission, business scope, validation and destination idempotency. The diagram identifies the acceptance boundary; adjacent discussion distinguishes stream receipt from ledger acceptance and private endpoint access from alternate-route enforcement. Four new ingestion-authority cases require trusted tenant/producer mapping, an alternate-path test, producer-scoped event identity and bounded replay permissions. The compromised-sender transfer explicitly rejects the assumption that authenticated content must be truthful.

The separate assessor notes identify enforcing components and missing observations. This supports partial design understanding. Actual identity integration, effective policy evaluation, allowed/denied submissions, bypass checks, replay side-effect prevention and independent assessment remain open. The existing event-accounting lab still trusts producer identity and was not relabeled as an authorization test.

## Knowledge 03 — Transfer service use cases

Unit 12 now compares dataset movement with maintaining an S3-backed file interface. The selection table, conceptual flow and surrounding explanation connect DataSync to supported transfer pairs and S3 File Gateway to continuing compatible NFS/SMB access. They distinguish task verification scope, independent inventory, upload persistence, metadata refresh and application-consistent cutover. The current official knowledge bullet's hash was rechecked and matched before adding this mapping.

Six migration exercise cases and separate assessor notes test retirement versus continuing access, an incomplete manifest, unuploaded writes, multi-writer/cache assumptions and active database files. The changed case turns a retirement project into recurring analytical delivery and asks the learner to revisit publication and cost. This supports partial selection knowledge. No DataSync task, gateway, metadata compatibility, access-denial, performance, outage, recovery or learner evidence is supplied by the local SQLite migration drill. Those implementation and operating conditions remain open.

## Previously mapped entries and remaining boundaries

Knowledge 02 and 06 retain their earlier partial ingestion-frequency and volume/throughput mappings. Their fictional timing calculator remains arithmetic evidence, not measured transfer speed or a freshness guarantee.

Knowledge 01 now has a partial mapping to unit 30, “Choose the reporting tool by the reader's job.” The unit distinguishes catalog, query and dashboard responsibilities; compares ad hoc analysis, recurring manager reporting, operational status and static reports; and develops freshness, denominator and reader-permission boundaries. Six original dashboard cases and assessor notes test these decisions. The current official bullet hash matched the stored inventory before adding the mapping. Selected-service setup, supported connections and editions, effective permission checks, refresh failure behavior, rendered usability, measured costs and independent learner assessment remain open. All seven mappings are partial; their existence does not establish complete task coverage.

## Evidence locations

- [Dashboard unit](../../reader/BOOK-LOCATORS.md#book-9a2045b273a89d57) and [assessment](../../examples/dashboard-review/README.md)
- [Unit 14](../../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9)
- [Processing cases](../../examples/processing-selection/README.md) and [assessor notes](../../examples/processing-selection/ASSESSOR.md)
- [Ingestion cases](../../examples/ingestion-review/README.md) and [assessor notes](../../examples/ingestion-review/ASSESSOR.md)
- [Skill-level transfer criteria](../skill-reviews/SAA-3-5.md)
- [Checkpoint recovery](../../examples/checkpoint-recovery/README.md)
- [Individual knowledge ledger](../knowledge-evidence.csv)

This is a source and teaching-evidence review. It does not add a runtime result or independent assessment outcome.
