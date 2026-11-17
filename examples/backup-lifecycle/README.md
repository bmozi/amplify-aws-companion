# Backup and lifecycle design cases

These are paper exercises. They create no AWS resources and use no live account data. First write your answers without an AI assistant, then compare them with the [separate criteria](ASSESSOR.md). They are original study cases, not AWS exam questions.

## Case 1: Choose the recovery copy

Maya's repair shop stores customer photos in S3. Yesterday, a worker overwrote one photo with the wrong image. This morning, a cleanup script deleted a whole folder. A separate Region also receives copies of new objects. The shop needs to recover one old photo today and wants a process for larger mistakes. It has not stated a maximum recovery time, acceptable data-loss window, retention period, or monthly cost limit.

Before choosing, answer:

1. Which failure can object version history help reverse, and what does it retain?
2. Why does a second copy or replication destination not, by itself, prove an independent recovery point?
3. What extra question would you ask before selecting AWS Backup for this S3 workload?
4. What evidence would prove that the restored photo and its booking record are correct?
5. Which workload details and charges must be estimated before enabling the chosen design?

After saving your answer, consult the [separate assessor](ASSESSOR.md).


## Case 2: Read a lifecycle rule

A bucket has versioning enabled. It contains a current photo uploaded 100 days ago and an older version that became noncurrent 70 days ago. A proposed rule says: “Expire current objects after 60 days.” The shop owner expects this rule to erase every copy and stop customers reading the photo on day 60.

Explain what is wrong with that expectation. Then propose what must be decided and reviewed before a rule is enabled.

After saving your answer, consult the [separate assessor](ASSESSOR.md).


### Try a changed case

The shop must hide a photo from customers immediately but retain it for 180 days in case of a dispute. The current version is 40 days old and has two earlier versions. Draw two separate timelines: when application access ends and when storage versions may be expired. State who approves the retention decision and what evidence will show that both timelines were followed.

Ask Codex to challenge your answer: “Which action changes customer access, which action changes retained versions, and what could make these two timelines diverge?” Verify every service-behavior claim against the linked AWS documents. AI assistance is a review aid, not evidence that the rule has been deployed or that the business retention decision is valid.


## Case 3: Separate recovery copies from long-term archives

Before answering, check the current [AWS Backup guidance for S3](https://docs.aws.amazon.com/aws-backup/latest/devguide/s3-backups.html), [S3 restore steps](https://docs.aws.amazon.com/aws-backup/latest/devguide/restoring-s3.html), and [S3 Glacier storage-class comparison](https://docs.aws.amazon.com/AmazonS3/latest/userguide/glacier-storage-classes.html). Treat the case limits as business constraints, not guaranteed service times.

A small records office has two promises for finalized inspection reports. First, a mistaken overwrite or deletion must be recoverable with no more than 15 minutes of accepted updates lost, and staff need the restored current report within two hours. Second, a sealed annual set must be retained for seven years and can take up to eight hours to retrieve after an approved request. It has not chosen a monthly spending limit or established whether records must be protected from administrator deletion.

Draw two lanes: one for operational recovery and one for long-term retention. For each lane, name the protected data, the failure it addresses, the recovery point or retention period, the person who can initiate recovery, and the evidence that shows the result is correct. Compare version history, AWS Backup for S3 and an S3 archive storage class. Which one is a recovery point, which one is a storage-cost/access choice, and which promises need different mechanisms?

After saving your answer, consult the [separate assessor](ASSESSOR.md).


### Change one requirement

The operations lead changes the archive retrieval promise from eight hours to five minutes. Explain which archive choices become unsuitable, whether the archive tier is still needed, and how a distinct recovery copy handles the 15-minute data-loss promise. Ask Codex to identify assumptions and current AWS facts that need rechecking, then verify those facts against the linked primary documentation.


## Case 4: Choose the lifecycle from retention and retrieval

A team stores signed inspection reports in a versioned S3 bucket under `reports/`. Staff read a new report frequently during its first 45 days. After that, they rarely read it, but an approved audit request may need it within 12 hours. The owner has approved retaining each report version for five years. A report may be replaced during correction; the earlier signed copy still counts as a record. The bucket already contains two years of objects, including small metadata files.

Propose a lifecycle design and draw the timelines for a current version and a version later replaced. State which current versions transition, which noncurrent versions transition, what happens at the retention boundary, and which objects your filters select. Explain why choosing the lowest storage rate is insufficient. Check transition eligibility for the small files and whether the existing object population changes the first day of the plan.

After saving your answer, consult the [separate assessor](ASSESSOR.md).


### Change the retrieval promise

The audit request now needs any report in 30 minutes, and half the files are smaller than 128 KiB. Which transitions remain appropriate? What might you retain in a faster class, and what size filter or separate object group needs review? Explain the effect on the cost model without inventing dollar rates.
