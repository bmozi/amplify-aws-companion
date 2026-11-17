# SAA-C03 task 4.1 — storage skills

Internal editorial review, October 19, 2026. The checked official domain source is retained at `artifacts/curriculum-research/saa-storage-cost-review-source.md` and its source hash is recorded in [the storage knowledge review](../knowledge-reviews/SAA-4-1.md). The task names ten skills. This document individually reviews skills 01 through 10; every task 4.1 skill now has an individual partial evidence review, not a completed-task judgment. Knowledge-bullet reviews are tracked separately.

## Skill 01 — Design an appropriate storage strategy

The original example contrasts batch uploads to S3 with individual uploads. Unit 20 now asks what one S3 object should represent. It distinguishes separate objects, record aggregation for grouped reads, multipart upload of one large object, and S3 Batch Operations over existing objects. The [upload-strategy case](../../examples/s3-upload-strategy/README.md) changes item-level retrieval, freshness and replacement requirements. Its assessor checks object/request arithmetic, downstream processing costs, integrity evidence and retry/cleanup behavior.

This is partial design evidence. The case does not implement or benchmark an uploader, prove record-once delivery, establish current pricing, or identify a selected production stream configuration. Task completion is not inferred; independent learner evidence remains pending. No independent learner response has been collected.

## Skill 02 — Determine storage size for a workload

Unit 20 uses an explicit six-month forecast and a 20% free-space assumption: 650 GiB currently used, plus 40 GiB/month, gives 890 GiB of projected data and 1,112.5 GiB of provisional capacity. The [storage-size case](../../examples/storage-sizing/README.md) asks the learner to show units and revise growth rate, temporary index space, and planning horizon. Assessor notes separate provisioned capacity from snapshots, performance and quota checks.

This is partial planning evidence. The values are fictional; no production telemetry, approved forecast, current service limit, regional price, alert or expansion was checked. Independent learner evidence remains pending.

## Skill 03 — Select a cost-effective transfer method

Unit 12 now compares a supported direct client with DataSync for a one-time office-to-S3 copy and asks the reader to total the source network, service or agent, destination request/storage, verification, retry, overlap and cleanup terms. Its 6 TiB case calculates an ideal 200 Mbit/s lower bound and distinguishes that arithmetic from a measured end-to-end transfer. It excludes a continuing Storage Gateway unless a persistent file-access requirement exists. Official DataSync transfer, pricing, verification and task-report guidance grounds the service boundaries.

The case intentionally contains no AWS price table or source-provider contract. It teaches which inputs to obtain and how to compare eligible designs; it cannot choose an actual lowest-cost route without current regional rates and measurements. No transfer or integrity run occurred and learner review remains pending.

## Skill 04 — Determine when storage auto scaling is needed

Unit 20 distinguishes capacity growth from performance scaling and asks whether safe free-space runway is shorter than the human response window. The [storage-growth case](../../examples/storage-auto-scaling/README.md) compares EBS volume changes plus guest filesystem work with EFS managed storage elasticity and S3 non-provisioned capacity/request scaling. It requires maximum sizes, alerts, quota and bill checks before proposing automation.

This is partial design evidence only. Its growth rates are fictional; no telemetry, quota, price, alert or automated resize was tested. Learner review remains pending.

## Skill 05 — Manage S3 object lifecycles

The [Terraform example](../../examples/s3-lifecycle-terraform/README.md) creates one lifecycle configuration on a new private, versioned bucket and scopes it to `temporary/`. Current-version expiry, noncurrent-version deletion and incomplete multipart cleanup are expressed as separate actions. The module is formatted, initialized without a backend and passes `terraform validate` with the locked HashiCorp AWS provider v6.69.1.

Validation establishes only that Terraform accepts the configuration shape. No plan or apply ran. The configuration has not been checked against a real bucket inventory, permissions, current bill or data owner's retention approval; lifecycle expiry may permanently remove matching data. This mapping is partial, and independent learner/technical review remains pending.


## Skill 06 — Select a backup and/or archival solution

The [new case](../../examples/backup-lifecycle/README.md#case-3-separate-recovery-copies-from-long-term-archives) separates a 15-minute recovery-point and two-hour operational restore promise from seven-year retention with an eight-hour retrieval allowance. It asks the learner to compare version history, AWS Backup for S3 and archive classes, then changes the archive retrieval window to five minutes. The assessor requires cost inputs, recovery authority, current prerequisite checks and business-data reconciliation.

This is partial design evidence. The case does not choose an account boundary, enforce immutable retention, test AWS restore behavior or establish current prices. The fictional timing values are decision constraints, not observed service performance or a business/legal approval. Skill 10 remains task-level only; independent learner and technical review remain pending.


## Skill 07 — Select the appropriate data migration service

Unit 12 now compares three different operating patterns: a one-time move from a NAS, recurring supplier delivery over SFTP, and an application that continues using SMB while its data is stored in S3. The [portfolio case](../../examples/migration-service-selection/README.md) assesses DataSync, Transfer Family and S3 File Gateway by source/target support, protocol, identity, cache/outage behavior, verification, cutover and lifetime cost. Changed constraints require re-selection.

This is partial design evidence. No service was created and no source/target compatibility, region, price, throughput or cutover was tested. Real source contracts, permissions, data inventory and business acceptance remain necessary; independent review remains pending. Skill 10 remains task-level only.


## Skill 08 — Select the appropriate storage tier

Unit 20 now begins tier selection with the customer's access promise, followed by a class-candidate table that distinguishes frequent, changing, infrequent-immediate and asynchronous archive access. The [tier exercise](../../examples/storage-tier-selection/README.md) asks learners to choose for five fictional datasets, change the retrieval pattern and include size, request, minimum-duration, recovery and cost terms. The [versioned read-path exercise](../../examples/storage-cost/versioned-read-path/README.md) adds a dated Ohio S3 Standard four-meter comparison for a changed, read-heavy object: retained version byte-days, PUT, GET and internet outbound transfer are shown separately. Its saved public offer hashes and rate selector are reproducible; the subtotal is expressly pre-allowance and incomplete. Current AWS class and pricing guidance grounds the boundaries; the assessor gives alternatives where workload inputs matter.

This is partial design evidence. The dated example does not establish the account's effective price, available shared allowance, actual object distribution, retrieval behavior, retention requirement or complete bill. Independent learner evidence and a selected measured workload remain pending.


## Skill 09 — Select the correct data lifecycle for storage

Unit 10 now links lifecycle selection to a five-year report-retention case in the [backup/lifecycle exercise](../../examples/backup-lifecycle/README.md#case-4-choose-the-lifecycle-from-retention-and-retrieval). It requires separate timelines for current and noncurrent versions, exact object scope, treatment of pre-existing matches, retrieval deadlines and transition/deletion cost. A changed case tightens retrieval time and increases small-object share.

This is partial design evidence. No real object inventory, retention approval, lifecycle filter, regional cost or restore process has been tested. The case does not establish compliance or actual S3 behavior. Independent learner and technical review remain open.


## Skill 10 — Select the most cost-effective storage service

Unit 20 and the [three-workload case](../../examples/storage-service-selection/README.md) now require selection among S3 object, EFS shared NFS and EBS machine-attached block patterns before comparing whole costs. The assessor asks for workload size and operation evidence, data protection, performance, network and recovery costs. Changed cases test concurrent file edits, Windows/SMB requirements, shared readers and colder shared-file data.

This is partial evidence for a bounded S3/EFS/EBS comparison, not a survey of every suitable AWS file/object/block service. No real workload is priced or benchmarked, and a chosen interface has not been tested against application semantics. All ten task 4.1 skills now have individual partial mappings; independent technical and learner review and live evidence remain pending.
