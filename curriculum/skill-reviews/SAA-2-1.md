# Individual-skill review: SAA-C03 task 2.1

Internal editorial review, October 18, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task1) contains seven skills. IDs are our positional labels; objectives below are paraphrased. All remain partial. This task combines many knowledge areas; mapping its skills does not finish those areas.

## Seven changed-case prompts

### Skill 01 — Design boundaries from requirements

Maya's acceptance API is fast, but photos take several minutes to process. Compare a modular synchronous application and a separate asynchronous processor. The accepted-work write succeeds while queue dispatch fails: explain what each design promises and how the pending work can be found.

Look for: timing and business-state distinction, durable dispatch, independent failure/scaling reasons and the operating cost of separation. Unit 2 and the request-processing design teach this reasoning. A02 has local emulated evidence, not real distributed dispatch or an independent design assessment.

### Skill 02 — Choose scaling by the limiting resource

Use this separate fictional steady-rate model: arrivals are 17 jobs per second; each worker can finish two jobs per second; a shared supplier caps total completions at 18 jobs per second. Assume durable queued work, constant rates, no retries or startup delay, and an initially empty backlog. Compare eight and twelve workers. Then the supplier stops all completions for five minutes while arrivals continue. Calculate the backlog and whether each fleet can clear it after supplier recovery while new jobs continue arriving. Identify which real measurements could invalidate the calculation.

Look for: eight workers cannot keep up; twelve workers remain supplier-limited to 18 jobs/s and have only one spare job/s. Starting empty, the outage adds 5,100 jobs; at that spare rate recovery takes 5,100 seconds if all simplified assumptions hold. These are calculations, not observed load behavior. Startup, retries, job distribution, oldest-work age and safe scale-in matter. No cloud autoscaling or load test is evidenced.

### Skill 03 — Choose a decoupling mechanism

One photo needs processing, while two departments each need the completion notice. Decide where a work queue, subscriber distribution or event routing fits. Explain why putting both departments on one competing-consumer queue does not establish independent delivery to each.

Look for: message purpose, per-consumer recovery, stable identity, ordering requirements and target failure handling. Unit 2 now compares the mechanisms; local event reconciliation is sequential. No SNS/EventBridge integration or independent consumer outage test has been run.

### Skill 04 — Decide whether containers fit

A worker requires an existing custom runtime, and the team wants predictable artifact packaging. Compare a container path with a function or machine, then change the requirement to an operating-system capability unavailable in the proposed managed runtime.

Look for: required behavior, compatible execution environment, state location, image identity, permissions and full operational cost. Unit 15 includes actual local Docker release/drain evidence. ECS deployment, realistic load and a complete container migration remain pending.

### Skill 05 — Decide whether serverless fits

A brief event handler bursts in demand, but its database supports a limited number of active connections. Explain why removing server administration does not remove that bottleneck and identify the invocation/concurrency behavior to inspect.

Look for: workload limits and downstream bounds, distinction between capacity reservation/capping and preinitialized capacity, and failure/retry behavior for the chosen source. Unit 2 supplies the initial decision; current Lambda work does not establish this burst/concurrency scenario. Measured startup, scaling and downstream protection remain unverified.

The later [six-request local burst](../../examples/serverless-db-burst/README.md) now makes that dependency visible with six simultaneously started local handlers, two immediate slot admissions and four busy results, then six completions through a volatile queue with two consumers. Its original figure and changed cases distinguish synchronous refusal from explicit asynchronous acceptance, function reserved concurrency from SQS event-source maximum concurrency, and prepared execution environments from database work capacity. This strengthens the **partial** mapping. It does not measure Lambda, SQS, RDS, customer latency or a selected safe production setting; independent learners have not attempted it.

### Skill 06 — Select the whole technology path

The same company needs a keyed booking update, shared legacy file access and a flexible relational report. Compare interfaces and consistency needs before choosing compute, storage, networking and database services. Explain which choice forces changes elsewhere.

Look for: requirements across the full path, supported compatibility and a credible alternative. Unit 20 now develops object/file/block operations and a five-change S3 Files versus separate-file-store versus object-redesign packet. The new cases expose two access paths, delayed export, API/file conflict, rename behavior, whole cost and a Windows/SMB requirement that changes the shortlist. This is deeper authored selection practice, not a measured workload comparison. Database alternatives, private connectivity, selected-client compatibility, real conflict/recovery behavior, current complete prices and independent learner assessment remain missing.

### Skill 07 — Prefer a supported service when its contract fits

A team proposes building a custom queue server because it can demonstrate enqueue/dequeue quickly. Compare it with a managed queue using durability, duplicate handling, maintenance, permissions, recovery and cost. Name one requirement that would force the service selection to be reconsidered.

Look for: service-managed responsibility distinct from application correctness, current supported behavior and operating capability. Unit 2 now follows accepted photo P-42 through an atomic outbox, SQS Standard, a duplicate-safe worker and supplier reconciliation. The [changed-case packet](../../examples/managed-service-selection/README.md) asks learners to choose among SQS, a database queue and an operated broker, then revisit the choice when a send reply is lost, the supplier result is uncertain, booking writes contend, a protocol is mandatory or long replay is required. A [separate assessor](../../examples/managed-service-selection/ASSESSOR.md) gives bounded reasoning and cost/reversal criteria. The existing [local queue-recovery lab](../../examples/queue-recovery/README.md) demonstrates one duplicate-effect boundary. This remains **partial**: the alternatives have not been implemented on AWS, the chosen workload and regional cost have not been measured, and no independent learner has been assessed.

## Knowledge-list review and disposition

The official task includes sixteen knowledge areas. Coverage is uneven: event/queue reasoning and container operation have deeper local examples; API management, caching, edge delivery, load balancing, multi-tier design, read replicas and storage-interface comparisons remain introductory or incomplete. Compute/state/scaling and workflow reasoning have prose and bounded examples but need service-specific implementations. Container migration and managed-service selection need complete worked comparisons. This paragraph is a coarse audit, not sixteen completed evidence records.

Added four substantive sections to unit 2: boundaries tied to business timing, a checked backlog/drain calculation, messaging selection and managed-execution limits. The prior prose mentioned queues and scaling without enough worked decision detail. No cloud provisioning was necessary to improve that teaching, but arithmetic and local tests cannot replace real service evidence. All seven learner reviews remain pending.

For assessment, give the prompts separately from their rationales. Ask the learner to state assumptions and then change a constraint. Record their actual explanation and assistance; do not infer mastery from this authored answer guide or the existence of a diagram.


## Later API and orchestration evidence update

The [individual knowledge review](../knowledge-reviews/SAA-2-1.md) supersedes the earlier coarse absence description for API and container-orchestration depth: unit 1 now includes an API contract lesson and bounded local HTTP lab, and unit 15 includes Kubernetes object/responsibility teaching with six design cases. Both knowledge mappings remain partial. Skill 04 now has that responsibility comparison as additional assessment support; complete container migration, cloud orchestration and learner evidence are still pending. The earlier coarse audit is not a claim that later storage, networking or replica work is absent; use the current individual ledger for those topics.
