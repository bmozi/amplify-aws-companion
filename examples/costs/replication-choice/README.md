# Which copy earns its ongoing cost?

Maya's shop has repair photos and a booking ledger. A photo is an object that may be opened later. A booking is a changing business fact that may be updated during a live customer conversation. A colleague proposes “replicate everything to a second Region” and calls the design complete. Your task is to decide **which customer operation must survive a Region failure**, what copy it needs, how fresh that copy must be, and what the entire copy will cost and preserve.

This paper lab addresses [SAP-C03 skill 3.2.3](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain3.html). It makes no AWS call. Use the [recovery lesson](../../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [storage lesson](../../../reader/BOOK-LOCATORS.md#book-316ad1ab1452bb2f) and [database selection lesson](../../../reader/BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa). Write a response before reading the [assessor](ASSESSOR.md).

## Draw two distinct copy paths

```text
photo upload -> source S3 bucket/version -> replication rule -> destination S3 version
booking write -> source DynamoDB item -> global-table replication -> destination item
```

A second copy is not the same as a working second application. In either path, identify the reader, the authority for new writes, the permission and encryption keys, the route to the second Region, and the observation that a recent change arrived. Avoid copying data that a data-location rule forbids.

## Five decisions

For each decision, state the **customer promise, candidate mechanism, freshness/failure limit, cost meters, one allowed observation, one negative observation, and cleanup/retention owner**.

1. **Photo archive.** New photos must reach an approved backup Region. Existing photos predate the rule. Distinguish live S3 Cross-Region Replication from an existing-object backfill. Include source/destination versioning, replication permissions, destination storage and lifecycle, replication PUTs, inter-Region transfer, KMS operations where used, and any Replication Time Control/metrics you choose. Which cost continues after the test ends?
2. **One booking writer.** Maya wants the second Region to serve customer reads after a failure, with a stated acceptable staleness. Compare a global table with a backup/restore plan. State replicated-write, replica-storage, read, backup and monitoring meters; do not add an S3-style inter-Region transfer line to DynamoDB global-table replication without checking AWS's billing rules.
3. **Two booking writers.** Both Regions accept edits to the same booking during a network split. The proposed answer says, “the global table keeps both updates.” Choose a consistency mode and write authority that meets the business rule, or change the promise. Give a conflict test and a failback rule. A lower bill does not cure lost business meaning.
4. **Quiet month, long retention.** New photo uploads fall sharply but old versions and destination copies keep growing. Decide whether the team needs every noncurrent version and the current storage class. Explain how expiry, restore time, deletion rules and audit needs change the cost and recovery promise.
5. **Different data rule.** A new contract forbids booking data from leaving the original Region, while photos may be copied to the approved backup Region. Redraw the recovery promise. What can be restored elsewhere from permissible data, and what customer operation must wait or use a separately approved design?

## Evidence and AI review

Use a worksheet with separate rows for **source storage, destination storage, request/replicated-write units, transfer where applicable, KMS, monitoring, backup/retention and restore**. Put a quantity, unit, Region, lifetime and dated price source in each row before calculating a real estimate. There is no numerical price in this exercise. A real pilot also needs an observed replication lag, an intentionally failed or delayed copy, a restored read, a prevented adjacent-data read, and a billing reconciliation. A passing configuration screen supplies none of those results by itself.

Ask Codex to play the skeptical data owner: have it find a missing copy, an unpriced retained version and a conflict that changes a booking. Require source links for any AWS behavior it asserts, then check the actual [S3 replication requirements](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-requirements.html), [S3 setup and existing-object behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-how-setup.html), [S3 pricing](https://aws.amazon.com/s3/pricing/), [DynamoDB global-table billing](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/global-tables-billing.html) and [global-table design](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-global-table-design.html). No real customer record, key or account detail belongs in the prompt.
