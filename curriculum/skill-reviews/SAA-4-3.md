# Individual-skill review: SAA-C03 task 4.3

Internal editorial review, October 18, 2026. The official [Domain 4 objective](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain4.html#solutions-architect-associate-03-domain4-task3) includes five skills: backup/retention policy, appropriate engine, cost-effective service, cost-effective database type, and schema/data migration. All five skills now have separate partial mappings. This is not task completion: current workload evidence, owner decisions, technical review and learner assessment remain open.

## Skill 01 — Design appropriate backup and retention policies

Unit 07, “Set the backup policy from the failure you need to recover from,” derives the schedule, recovery lookback, retention and restore checks from owner-approved RPO/RTO, corruption-detection time, records requirements and failure boundaries. The [four-case paper worksheet](../../examples/database-backup-policy/README.md) compares quickly detected deletion, corruption found after 42 days, seven-year records retention, and compromised backup credentials. It asks for separate operational and archive promises, application-level restore acceptance, and whole-path costs.

Current AWS primary documentation was checked October 18, 2026 for RDS automated-backup retention and point-in-time recovery, DynamoDB PITR/on-demand recovery, AWS Backup plans and restore-test validation. Service recovery windows and restore destinations differ. A policy must verify the precise resource, Region, encryption/key access, copy boundary and current price; no generic retention period meets every scenario.

This is partial design evidence. The cases are synthetic. No owner has approved the proposed retention, no calculator estimate or resource configuration was created, and no restore was tested. Independent technical and learner reviews remain open.

## Skill 02 — Determine an appropriate database engine

Unit 25, “Compare engines against the application's actual behavior,” expands the PostgreSQL/PostGIS migration example into an engine-dependency inventory and parity-test method. The [engine-selection worksheet](../../examples/database-engine-selection/README.md) asks the learner to separate engine choice from managed-service choice, check exact RDS/Aurora version and Region capabilities, state a conversion benefit, and define expected outcomes before comparing behavior.

Current official sources checked October 18, 2026 include the exam objective, RDS PostgreSQL extension availability, RDS MySQL feature support, and DMS Schema Conversion boundaries. This is partial evidence: no selected target version/Region, complete application inventory, representative AWS load test, conversion or measured price has been checked. DMS schema conversion assessment does not itself migrate application data or prove semantic equivalence. Independent technical and learner reviews remain open.

## Skill 03 — Determine cost-effective AWS database services

Unit 25, “Compare database services by eligible access path and full cost,” contrasts an ID-keyed, bursty device-status workload with a relational appointment/invoice workload. The [cost worksheet](../../examples/database-service-economics/README.md) compares DynamoDB on-demand and provisioned capacity, RDS and Aurora candidates, while requiring the same correctness, retention, recovery and traffic assumptions. It counts the database, indexes/storage, backup, transfer, application compute, operations and development effort rather than comparing only one service price line.

Checked current AWS Well-Architected access-pattern guidance, DynamoDB capacity modes and usage-cost documentation, and RDS billing components on October 18, 2026. This is partial design evidence; no current regional calculator model, account usage, service configuration, latency or cost was measured. Independent technical and learner reviews remain open.

## Skill 05 — Migrate database schemas and data

Unit 25, “Treat schema conversion, data movement and cutover as separate work,” distinguishes conversion assessment from moving data and changing the application's write destination. The [rehearsal worksheet](../../examples/database-migration-rehearsal/README.md) includes a cross-Region and possible cross-engine plan, full load/CDC considerations, target validation, business-level parity, controlled cutover, reverse-write risk and migration-month cost.

Current AWS primary documentation was checked October 18, 2026 for DMS Schema Conversion scope, task phases, data validation requirements/limitations and homogeneous migration workflow. This remains partial planning evidence. No source/target combination was selected, no migration task or endpoint was created, and no data was moved or validated. Owner approval, measured rehearsal/rollback, regional cost and independent/learner review remain open.

## Skill 04 — Determine cost-effective AWS database types

Unit 25, “Time-series questions and columnar files solve different parts of the problem,” teaches the distinction between a time-ordered measurement workload and a physical columnar format. It uses the documented Timestream for InfluxDB 3 Parquet architecture to show that the concepts can coexist. The [no-cloud economics worksheet](../../examples/database-type-economics/README.md) checks the 3,456,000-observations/day scenario arithmetic, recent operational query versus historical fleet analysis, lifecycle eligibility, current calculator-input research, retention assumptions and changed-case reasoning. Assessor notes distinguish a time-series candidate, S3/Parquet/Athena and when warehouse behavior merits a separate comparison.

Checked the current AWS exam objective, Timestream LiveAnalytics availability notice, InfluxDB 3 architecture and Athena columnar-format guidance on October 18, 2026. AWS closed LiveAnalytics to new customers on June 20, 2025. New-account recommendations must therefore not use it as a default. InfluxDB 3's Core and Enterprise features differ materially; service and edition remain candidates to evaluate rather than an automatic choice.

This is partial instructional evidence. Arithmetic and design cases are synthetic. No Regional availability, current calculator estimate, service deployment, AWS performance, measured bill, independent technical assessment or learner result is established. All five individual skill mappings remain partial; task completion and broader exam readiness are not established.
