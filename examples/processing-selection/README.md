# Choose the scheduler and the engine separately

These six original design cases extend [unit 14](../../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9). They create no cloud resources. Record your answer before reading [assessor notes](ASSESSOR.md).

For each case name the input/output contract, deadline, candidate, rejected alternative, operating owner, cost drivers and evidence needed to change the choice.

1. A company already has a supported container image that transforms independent files. It needs a queue for thousands of submissions. A colleague proposes rewriting it in Spark solely because the files arrive nightly. Compare scheduling the existing program with rewriting its engine.
2. A team repeatedly joins cataloged customer and sales sources, cleans records and publishes a dataset. Compare managed data integration with a custom worker. Identify why an inferred schema cannot decide whether `amount` means dollars or cents.
3. An existing Spark job requires specific libraries and runtime behavior. Both a Glue-based and an EMR-based path are proposed. Explain why “both use Spark” does not establish interchangeability. State the compatibility and operating checks you would run.
4. Four fictional partitions take 10, 10, 10 and 70 seconds, starting together on four workers. Someone predicts 25-second completion by averaging the durations, then proposes eight workers without changing partitions. Explain both errors and what evidence would justify repartitioning.
5. A daily 10 MB file has a simple bounded transformation that fits one worker. The proposal creates a large distributed processing environment “for scale.” Identify an initial simpler candidate and explicit thresholds that would reopen the decision. Do not assume file size alone proves memory or runtime fit.
6. The worker computation finishes in 20 minutes, but the job spends 25 minutes waiting and 10 minutes publishing. The deadline is 45 minutes. Explain why a 20-minute runtime chart is insufficient, and which stage you would investigate before buying more compute.

Transfer: the job must now replay a month of history without replacing the current report until validation passes. Add output versioning, reconciliation, publication/recovery boundaries and a cost estimate. Ask Codex whether its design silently assumes unlimited source throughput or safe repeated external effects.
