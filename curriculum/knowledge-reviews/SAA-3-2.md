# Individual knowledge review for SAA-C03 task 3.2

Internal editorial review, October 18, 2026. This adds a partial mapping for knowledge ordinal 04; it does not complete the task or establish learner competence. The [official domain source](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html) was freshly fetched as Markdown and parsed before matching the inventory bullet.

Source bullet SHA-256: `324452b88e4a0197bc8641c459d40b72e346d941372bef5b70d13d7691dbaaa5`. Full fetched domain Markdown SHA-256: `c7b3109febeec88b03448a7bc4fb4ee49cceb5d297ccb690c7d883e6e986100a`. Positional IDs and objective paraphrases are editorial identifiers, not AWS-issued completion records.

Teaching: [unit 02](../../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), “Scale the bottleneck and keep a recovery margin,” with the earlier vertical/horizontal scaling and backlog recovery example. The revised section explains EC2 Auto Scaling group capacity, target tracking and a suitable per-instance signal. Official EC2 target-tracking and SQS scaling guidance were checked directly. The fictional 600-message example derives targets of 60 and 30 messages per worker under different mean processing durations, then distinguishes those ratios from actual response or dependency capacity.

Assessment: [compute selection cases 6–8](../../examples/compute-selection/README.md), with separate assessor reasoning. Cases 6–7 test continuing-arrival recovery; case 8 tests target selection, changed processing duration, zero fleet size and absent observations. The arithmetic was recalculated locally. No instance, alarm, scaling policy or metric publisher was created.

Remaining: selected service configuration and permissions; actual metrics and missing-data behavior; warmup and scaling activity; service-specific scale-from-zero and safe scale-in; representative load and duration tails; downstream constraints; measured costs and cleanup; independent learner transfer. Generic principles do not establish ECS, DynamoDB or other services' scaling controls. Do not propagate this mapping to neighboring objectives without reviewing their exact scope.

The full-unit review found overlapping backlog explanations after the recent addition. The earlier-in-reading-order worked example was retained; the later section now advances to controller signals instead of repeating a second capacity table. This is an editorial correction, not a claim that more prose proves mastery.
