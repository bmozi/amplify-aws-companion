# Database backup and retention policy worksheet

This paper exercise practices SAA-C03 task 4.3 skill 01. It creates no AWS resources. Read [unit 07](../../reader/BOOK-LOCATORS.md#book-d98571daa4ab1df3), write the policy decisions first, then compare with the [assessor notes](ASSESSOR.md).

## One example workload

Maya's booking database accepts confirmed appointments every day. The owner proposes: “Take a daily backup and keep it for a month.” That sentence has no stated RPO, RTO, restore test, clean-point lookback, account/Region boundary or record-retention approval. Work through the cases below before choosing a service feature.

## Workcard

For each case, write the recovery objective, candidate mechanism, retention reasoning, restore acceptance, major costs and an assumption that could reverse the design.

1. **Mistake found quickly.** At 12:05, a staff member deletes confirmed appointments by mistake. The team notices at 12:20. The owner says losing more than five minutes of confirmed changes is unacceptable. For this exercise, the 45-minute recovery target starts when the team notices the mistake, and the booking service must be usable again by its end. What is the deadline? Which steps must fit inside that interval? How would your answer change if the owner started the clock at the deletion instead?
2. **Corruption found late.** A defective update began 42 days ago. The first confirmed business impact is found today. The owner asks to restore the database to before the defect and preserve valid transactions since then.
3. **Long retention.** Final invoices must be kept seven years under a policy approved by the business and its counsel. The application database must still recover from recent mistakes within the operational window.
4. **Lost account credentials.** A privileged account was compromised and an attacker may delete accessible backups. The owner requires a recovery copy outside the affected administration boundary.

Then compare service mechanisms without treating them as interchangeable:

- RDS automated backup and point-in-time recovery versus retained manual snapshots.
- DynamoDB point-in-time recovery versus on-demand table backups.
- An AWS Backup plan for supported resource types versus service-native backup controls.

For every proposed mechanism, check current supported resource types and Regions, maximum lookback, restore destination, required KMS/key permissions, copy boundaries and pricing. Do not infer any mechanism from a service name alone.

## Cost and restore test

Use the current AWS Pricing Calculator or service pricing page for the selected Region. Record date, resource size/change rate, frequency, retention, number of copies, storage tier, cross-Region transfer, restore frequency and temporary restored capacity. Estimate an ordinary month and a month with the planned restore test. Include who runs tests and who validates application records. Do not deploy anything for this worksheet.

Define a restore test that proves more than “the restore API returned success”: record when the recovery clock starts; restore to a separate target; check representative record identities and business values against independent expectations; verify a critical application journey; and record when the service is usable again. Include detection, decision, restore, validation and cutover according to the chosen clock boundary. Dispose of temporary resources according to the exercise instructions. This is a design specification, not evidence that a restore ran.

## Changed-case transfer

Change one fact at a time: detection comes after 90 days; the allowed data loss becomes zero; records need legal hold; the database is multi-Region; a key is unavailable; a single record restore is needed; the service's native recovery period changes; or restore tests take longer than the RTO. Explain which policy assumption fails, what alternative evidence is required, and whether the business must revise its promise.
