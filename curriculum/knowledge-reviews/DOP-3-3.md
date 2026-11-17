# Individual knowledge review for DOP-C02 task 3.3

Internal editorial review, October 18, 2026. The [current official Domain 3 task page](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain3.html) lists three knowledge areas for implementing automated recovery to meet RTO and RPO requirements. The mappings below are partial and based on source inspection and local checks; they are not independent technical or learner review.

## 01 — Disaster-recovery concepts, including RTO and RPO

Unit 07 begins with Maya's booking promise and distinguishes time-to-useful-service from acceptable data loss. It uses a timeline, separates a running endpoint from correct business records, and requires a declared measurement start and acceptance end. The regional tabletop adds an asynchronous copy, a missing confirmed record, unavailable key access, an unfenced writer and a later journal. It explicitly refuses to convert the latest known copy time into a measured RPO or recovery guarantee.

The [recovery automation gate lab](../../examples/recovery-automation/README.md) makes the pre-cutover evidence requirements inspectable: confirmed trigger, fresh observer, selected recovery point, dependencies and keys, reconciled records, fenced previous writer and proved capacity.

**Still required:** select an actual workload and business-approved objectives; verify service-specific recovery semantics; run a measured, authorized end-to-end recovery; and have learners demonstrate transfer without relying on supplied assessor reasoning.

## 02 — AWS Backup and recovery strategies, including pilot light and warm standby

The new Unit 07 section compares backup-and-restore, pilot light, warm standby and multi-site active/active in terms of which components are running, what action remains, data authority and recurring cost. It explains that a cross-Region backup copy is not a live application and links current AWS primary documentation for cross-Region copy constraints, feature availability and restore testing. It also links Systems Manager Automation authoring and the permission boundary of the runbook role.

The fictional unit and lab describe an AWS design translation but create no backup plan, recovery vault, role, runbook, Region or standby workload.

**Still required:** validate the chosen resource/Region and encryption behavior, estimate current end-to-end costs, test restore and business validation, and verify scoped service-role permissions. Before live use, choose an appropriate whole-run ceiling and credit reserve for the selected account; organization-dependent variants remain design-only in this exercise.

## 03 — Recovery procedures

The existing recovery runbook section defines trigger, operator, candidate recovery points, dependencies, validation, reconciliation, cutover and cleanup evidence. The added automation section distinguishes repeatable execution from the authority to cut over, and explains stop, wait-for-approval and proceed conditions. The local seven-test model returns a reason for each blocked or approval-gated case.

**Still required:** demonstrate the procedure with an approved AWS service and actual failure/recovery path, including permissions, stale telemetry, duplicate effects, rollback/failback and costs. Local tests prove only this small decision model.

## Limits

These three individual knowledge mappings do not close task 3.3 or the DOP-C02 curriculum. Current AWS pages were inspected for the task objective and linked service behavior; feature availability, exact configurations, price and Region support must be rechecked before any later implementation. There is no live AWS verification, learner assessment, independent technical review or release-readiness claim in this evidence.
