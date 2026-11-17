# Individual knowledge review for DOP-C02 task 3.1

Internal editorial review, October 19, 2026. The current [official Domain 3 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain3.html) lists four knowledge areas for implementing highly available solutions. The retained source-bullet hashes in `knowledge-inventory.csv` were created from the accepted official Markdown inventory. The current HTML page still states the same four concepts. All four mappings below are **partial**: they connect actual teaching and assessment, not completed AWS configuration, certification coverage or learner mastery.

## 01 — Multi-AZ and Multi-Region deployments

Unit 07's [high-availability decision lesson](../../reader/BOOK-LOCATORS.md#book-382878fd78726415) defines the difference between an AZ failure boundary and a Region boundary, then asks the reader to choose the smallest scope that meets the business promise. It follows a second-Region design through regional resources, data, keys, quotas, routing, identity and operator access. The [availability decision-path figure](../../book/figures/availability-decision-path.svg) and five changed-condition [DOP-C02 design cases](../../examples/resilience-path-review/README.md#dop-c02-task-31-resilience-design-route) support assessment.

**Still required:** verify the selected service/feature/Region matrix, deploy only within an authorized and cost-reviewed scope, exercise failure/recovery and measure customer behavior. No multi-AZ or multi-Region environment is created by this lesson.

## 02 — Service-level agreements

The lesson distinguishes a provider SLA from the fictional application's customer-facing SLO. It calculates the illustrative time represented by 99.9% over a 30-day month and cautions that uptime minutes do not prove correct booking outcomes. The lab asks the reader to translate a business requirement into an SLO, acceptable interruption/data loss and reopening evidence.

**Still required:** inspect the current terms for each selected AWS service and evaluate their scope, measurement, exclusions and remedies. The example percentage is fictional, and this material is not legal interpretation of any provider commitment.

## 03 — Replication and failover methods for stateful services

The lesson distinguishes sending copies from changing write authority. It teaches lag, one-writer control, fencing, interrupted writes and record reconciliation, then compares regional replication with backups and traffic routing. Case 5 combines delayed replication, a write in flight, stale DNS and reduced standby quota.

**Still required:** verify selected service semantics, consistency and engine/feature support; test promotion, fencing, failback and duplicate-safe customer operations; record measured lag and recovery time. No replication or failover behavior was tested in AWS.

## 04 — Techniques to achieve high availability

The lesson compares Multi-AZ application capacity, managed database failover, cross-Region replication, regional routing and backup/restore by the question each answers and the responsibilities left behind. It links health, surviving capacity and end-to-end business acceptance rather than treating duplicate boxes as availability proof.

**Still required:** confirm architecture-specific failure isolation, supported configurations, current service limits/cost, and the selected workload's end-to-end recovery behavior. A design decision and a local tabletop are not measured high availability.

## Limits

The route is a fictional design worksheet with separate assessor notes. Its answers have not been collected from learners or calibrated by an independent technical reviewer. It provisions no AWS resources, checks no current account state or credits and consumes no AWS credits. Keep the evidence scope as partial.
