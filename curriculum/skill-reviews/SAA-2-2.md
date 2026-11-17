# Individual-skill review: SAA-C03 task 2.2

Internal editorial review, October 18, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task2) lists eight skills. These are our positional IDs and paraphrased labels. All eight remain partial; the prompts are original and have not been administered to independent learners.

**October 25 assessment separation:** The [reader packet](../../examples/saa-resilience-task/README.md) now places eight changed-fact cards before a [separate assessor](../../examples/saa-resilience-task/ASSESSOR.md). The prompts and scoring cues below remain this internal editorial review; they are no longer the learner's first-attempt assessment target in the individual skill ledger. This improves assessment independence from the answer key, not independent learner validation or observed AWS behavior.

## Eight changed-case prompts

### Skill 01 — Automate integrity with controlled changes

A recovery environment differs from its infrastructure definition after an emergency repair. An automated job proposes applying the old definition immediately. Explain what must be compared, who owns the resource and what would justify either updating the source or restoring the previous configuration.

Look for: drift diagnosis, source/state/runtime distinctions, reviewed plan, concurrency protection and recovery from partial failure. Unit 9 and its real local Terraform drill establish bounded mechanics. Remote state collaboration, cloud drift and autonomous remediation safety are not demonstrated.

### Skill 02 — Design availability across failure locations

The business needs 600 requests/s. Compare unit 7's two-location and three-location capacity examples after one location fails. Then add a shared database outage. Identify which claim each topology does and does not support.

Look for: surviving capacity rather than normal aggregate capacity, margin, dependency map and current service-specific placement/failover behavior. The arithmetic is a design screen. No deployed multi-zone or regional service design has been tested under load.

### Skill 03 — Measure the business availability promise

Every host reports healthy, but accepted bookings stop completing. Select a customer-facing measure, a backlog/deadline measure and an investigation signal. Explain the meaning of a time window with no requests.

Look for: a defined denominator, business completion, age of unfinished work and no-data handling. Unit 8 has synthetic calculations and actual local request/alert receipts. These do not prove production telemetry delivery, a useful SLO or human response.

### Skill 04 — Remove relevant single points of failure

Two application fleets survive, but the only recovery login and instructions depend on the failed office server. Draw serving and recovery-control paths. Propose isolation without assuming that merely adding an account or server solves the problem.

Look for: dependencies shared across copies, tested authorized recovery access and capacity isolation for competing work. Unit 7 now teaches the map; there is no implemented bulkhead or failure-injection result for this scenario.

### Skill 05 — Preserve and recover business data

A new backup has the expected row count but an incorrect booking amount. An older backup is correct but lacks one confirmed order. Explain what the local reconciliation drill proves and what evidence a real encrypted cloud restore would additionally need.

Look for: record-level reconciliation, independent trustworthy evidence, encryption/access dependencies and tested application cutover. Actual local restore evidence exists. AWS backup, replication, concurrency and durability under service failure remain unverified.

### Skill 06 — Choose recovery by the required outcome

Compare restore-on-demand and a prepared standby for an application with a short recovery window. Then change the failure from a lost machine to corrupted records replicated everywhere. State which previous assumption no longer holds.

Look for: cost/readiness tradeoff, whole recovery interval, confirmed-data evidence, old-writer control and failback. Unit 7 and the regional tabletop support design reasoning. They do not establish a measured cloud RTO/RPO.

### Skill 07 — Improve legacy resilience within real constraints

An application cannot be changed and keeps sessions and uploads locally. A proposal adds a second instance and a load balancer. Explain what becomes more available and what still fails when the original instance disappears. Consider the all-targets-unhealthy case.

Look for: supported clustering/state behavior, vendor constraints, health semantics and an honest limit on the promise. Unit 7 now has a separate [loopback HTTP failover lab](../../examples/legacy-session-failover/README.md). Its tiny proxy switches from A to healthy B and observes an old session denial and absent uploaded file; copying the file repairs only the file path. Four focused tests validate that local model. This is not a vendor-supported legacy deployment, ALB implementation, multi-AZ storage or measured AWS failover.

### Skill 08 — Choose managed capabilities for a reliability need

A team proposes custom traffic routing and custom backup scheduling. Compare those responsibilities with suitable managed-service candidates, then identify the application correctness and recovery work that would remain even if the infrastructure services work as documented.

Look for: a concrete requirement, supported service behavior, dependency/cost tradeoffs and acceptance evidence. Existing lessons give selection principles, not complete implementation comparisons across the task's purpose-built service examples. This skill is particularly broad and remains introductory.

## Knowledge-list review and disposition

The task includes twelve knowledge areas. Failure-location planning, recovery strategies, networking and visibility have teaching and bounded examples. Distributed failover, immutable replacement, load balancing, connection proxies, quotas and storage durability require deeper service-specific implementation evidence. The task's example managed services also need use-case depth; a list of names does not supply it. This paragraph is not a completed knowledge-bullet ledger.

The review exposed missing surviving-capacity arithmetic, recovery-control dependency mapping and legacy state/health caveats. Added three substantive sections to unit 7, grounded in official ALB and reliability guidance. The eight evidence rows remain partial; no organizational change, live failure injection or independent assessment occurred.

Provide prompts before rationales. Ask the learner to defend a choice and then change its failure assumption. Record actual answers, assistance and unresolved evidence separately from the authored scoring guidance.


Knowledge ordinal 4 now has an individual **partial** evidence mapping. The current official Markdown bullet matches stored digest `fea3908d38b2e4a83442b32a68bbf9c4a353eb5f046d3a6d6b6f5e5adaad2648`. Unit 7 compares preparation states for four recovery categories, separates timing from data-loss objectives, and adds fictional 27-minute versus 17-minute sequences. Four regional-review cases assess those distinctions. This supports teaching and bounded assessment design; it does not establish service-specific regional failover, measured AWS RTO/RPO or independent learner performance. Knowledge ordinal 06 also has a separate [partial failover review](../knowledge-reviews/SAA-2-2.md). As of October 25, the separate knowledge ledger has individual **partial** mappings for all twelve knowledge items in this task; this older note about first-mapped ordinals is retained only as a dated teaching history.


## Resilience rehearsal evidence update

Rechecked the official domain page on October 18, 2026: task 2.2 still lists eight skills, with business-requirement metrics at ordinal 03 and implementation of single-point mitigation at ordinal 04. The new material strengthens existing partial evidence; it does not add a skill mapping or establish either skill's complete coverage. [Current official source](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task2).

Unit 07's “Rehearse a failure with an exit plan” and “Three moments that must not be confused” now connect the serving, observation and recovery paths. The [resilience tabletop](../../examples/resilience-exercise/README.md) supplies explicit preconditions, a duplicate-confirmation timeline and an observer-silence case; its [separate assessor](../../examples/resilience-exercise/ASSESSOR.md) explains the decision boundaries and timing. E05 and E14 now lead readers to the exercise.

For ordinal 03, ask the learner to explain why a 90-second accepted recovery can meet a 120-second target while the no-duplicate promise still fails. Look for separate measures of service recovery and business correctness, an explicit timing origin, and rejection of stale green observations. The supplied arithmetic is not a service measurement. Unit 08's existing signal/receipt work remains the primary teaching path for the wider metric-selection skill.

For ordinal 04, ask the learner to trace a common sign-in or network dependency that could disable both the observer and the recovery operator. Then change the scenario so the stop path is available but the reconciliation source is not. Look for a revised acceptance decision and the missing evidence required to reopen. The diagram and fictional access precondition do not implement independent controls or prove failure isolation.

The authoring and scoped visual review establish that the teaching is present. The extracted companion receipt establishes that the files are included and related local drills execute on the existing host. Neither proves these tabletop decisions were made by an independent learner or validates a cloud fault platform. Remaining work includes implemented isolation, tested effective recovery access, actual metric freshness/alarm delivery, measured fault/recovery behavior, and independent changed-case assessment. Before selecting any live implementation, use a separately authorized environment and review its full cost and restrictions.

## October 24 legacy-state continuation

The [Unit 07 legacy section](../../reader/BOOK-LOCATORS.md#book-7cfd6a932c7d812e), original state-path figure, [predict/run/change exercise](../../examples/legacy-session-failover/README.md) and separate assessor strengthen ordinal 07. The checked source remains [SAA-C03 Task 2.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task2). AWS documents that sticky routing moves to a healthy target after the first fails and that an ALB can route to all registered targets when all are unhealthy; the local proxy deliberately models neither full service rule. Its actual observation is narrower: B answers `/health` while the old session returns 401 and the file is absent; copying the file does not restore that session. The source-mapping status stays **partial** until a compatible vendor mode, effective AWS authorization/health behavior, bounded failure test, complete cost and independent learner transfer are reviewed.
