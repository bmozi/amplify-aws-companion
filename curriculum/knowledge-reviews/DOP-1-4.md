# Individual knowledge review for DOP-C02 task 1.4

Internal editorial review, updated October 19, 2026. This records partial evidence for all four knowledge ordinals: deployment methodologies, application storage patterns, mutable versus immutable patterns, and code/image distribution tools. It does not complete this task or establish any AWS deployment skill. [Official domain source](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain1.html).

Freshly retrieved official domain Markdown and parsed task 1.4: four knowledge entries and four skill entries. The first knowledge bullet matches the accepted inventory digest `58fc948ae16b27c873d5e3252dd743db17b5ec7d88a7fbb039de96abf39398ab`. Domain SHA-256: `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. The ordinal is our inventory identifier, not an AWS-issued result.

## What the current material actually supports

| Concept | Exact teaching location | Practice and evidence limit |
| --- | --- | --- |
| Select traffic exposure and observation | Unit 03, Give a candidate a small, observable turn | Canary, linear, all-at-once and blue/green distinctions; the actual local HTTP drill uses deterministic sequential slots, not AWS weights |
| Verify business behavior and recovery | Same section | A ready wrong-price candidate is rejected; later responses identify the stable version; a repaired candidate can be promoted; small samples do not establish statistical confidence |
| Preserve a compatible recovery path | Unit 03, Keep the old version compatible while the data changes | Actual SQLite old-writer mismatch and removed-column failure; not an online distributed migration |
| Include configuration in release reasoning | Unit 03, Changing a setting is still a release | Six design-only cases cover mixed readers, missing signals and irreversible effects; no AppConfig rollout evidence |
| Distinguish readiness from shutdown completion | Unit 15, Alive, ready and correct are different claims; Stop receiving work before disappearing | Local container harness has controlled in-flight completion and forced-stop interruption checks; no AWS scheduler or load balancer |

Read [unit 03](../../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d) and [unit 15](../../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5) in context. The [canary source](../../examples/canary-release/lab.py) confirms that the teaching controller filters candidate observations, holds insufficient samples, checks subsequent response identities and allows a repaired version to succeed. The [container README](../../examples/container-release/README.md) identifies its engine prerequisites, bounded resource use and cleanup scope. This mapping inspected existing source and dated verification; it did not rerun Docker or establish fresh cloud behavior.

[E15](../EXERCISES.md#e15) now links the artifact gate, canary, schema, configuration and optional container sequence. Its transfer prompt requires the reader to identify the selected platform's controller, traffic boundary, recovery target, observations and overlap cost. The configuration cases have separate assessor notes; the other drills state expected outcomes and negative controls. No independent learner attempt has been assessed.

## Platform coverage still missing

The official knowledge entry spans EC2, ECS, EKS and Lambda. General traffic-shifting concepts and local behavior cover only part of that requirement. Unit 03 now adds “Follow the caller through a Lambda release,” explaining published versions, aliases, direct/unqualified bypasses, probabilistic exposure, controller responsibilities and recovery limits, with [five Lambda design cases](../../examples/lambda-release/README.md) and [separate assessor notes](../../examples/lambda-release/ASSESSOR.md). Unit 15 explains the ECS rolling circuit-breaker boundary and now adds “Give a rolling release room to move”: integer capacity limits, start-first versus stop-first tradeoffs, task and target health, alarm limitations, draining and recovery prerequisites. Its [six ECS design cases and transfer problem](../../examples/ecs-rolling-release/README.md) have [separate assessor notes](../../examples/ecs-rolling-release/ASSESSOR.md). These explanations do not implement either platform.

Before a broader claim, add and assess the selected platform-specific deployment paths: what unit is replaced, which controller owns the change, how traffic eligibility and draining work, which health/alarm signals can stop it, and what previous target is actually available. Verify instance/agent and image compatibility for the EC2 path; task/service/controller behavior for ECS; workload/controller and traffic integration for EKS; and published-version/alias/caller behavior for Lambda. Do not infer one platform's rollout capabilities from another's terminology.

Real cloud practice still needs scoped access, supported current configuration, a meaningful workload, cost overlap within the authorized run limit, failure and recovery observations, and cleanup. Organization-dependent variants remain design-only. This review does not claim artifact-repository IAM, agent installation, troubleshooting or deployment-method implementation skills.


## Mutable versus immutable patterns: knowledge ordinal 03

Freshly retrieved the official domain Markdown on October 18, 2026 and parsed task 1.4 again: four knowledge and four skill entries. Ordinal 03 matches inventory SHA-256 `3918bce51843f6ac84e77b753877118aa701ebb9ad2ff1f939606cc0bc5db76b`; domain SHA-256 remains `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. Retained source: `artifacts/curriculum-research/dop-mutable-review-source.md`.

Unit 03's “Repair the running worker or replace it from the recipe?” supplies the previously missing explicit comparison: an emergency edit lost on replacement, worker versus recipe authority, fixed image versus variable configuration/permissions, controlled replacement inputs, separate traffic-exposure choices, data retirement and recovery compatibility. Its table compares both approaches; the diagram traces reconciliation into a reviewed replacement. The explanation uses [AWS reliability guidance](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_tracking_change_management_immutable_infrastructure.html) without treating a recommended pattern as proof of universal atomicity or successful recovery.

The [five replacement-boundary cases](../../examples/replacement-boundaries/README.md) and [assessor notes](../../examples/replacement-boundaries/ASSESSOR.md) require changed-case reasoning; the deadline transfer explicitly permits a justified bounded alternative. Existing local container replacement and SQLite schema demonstrations provide narrower evidence described in their own records. This review does not rerun them, simulate a mutable AWS fleet, build an AMI or validate a real emergency procedure.

Coverage remains partial. Before a stronger implementation claim, inspect the selected AWS resource lifecycle, build/configuration provenance, effective change authority, drift, overlap capacity, customer-data boundary and actual mixed-version/recovery behavior. An independent learner must explain and demonstrate the chosen path. No neighboring agent-installation, code-distribution or repository-permission skill is inferred.


## Application storage patterns: knowledge ordinal 02

Rechecked the current Domain 1 task page on October 19, 2026. Ordinal 02 matches inventory SHA-256 `430a2b9fdf9b69c6e157b7138ef4eb59f7c88ff0f1cfd2d47b35c3e525423074`; retained Domain 1 Markdown digest remains `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`.

Unit 03 now makes three boundaries explicit: source/build artifact, deployment controller/platform, and application data. Its hand-authored figure traces source to a reviewed image/revision, then separates the running compute from the data path. The storage table distinguishes temporary local data, block volumes, shared files, objects and structured records. It calls out EC2 instance-store loss, EBS delete-on-termination and retained-volume cost, shared EFS access requirements, S3 object/API semantics, ephemeral container layers and Lambda `/tmp`. Current AWS references support these claims: EC2 storage/termination, ECS persistence, EKS EBS CSI constraints, and S3 objects. Exact service features still depend on platform/version and configuration.

The [deployment-storage worksheet](../../examples/deployment-storage/README.md) and [separate assessor](../../examples/deployment-storage/ASSESSOR.md) cover a replaced EC2 server, horizontally scaled ECS uploads, stateful and stateless EKS workloads, Lambda scratch data, and recovery of records. They are design-only; no AWS storage or price was queried and no resource was created. They require checking access, lifetime, sharing, backups/recovery, feature eligibility, cost and cleanup, not simply choosing the most durable-sounding label.

## Code and image distribution tools: knowledge ordinal 04

Rechecked the current Domain 1 task page on October 19, 2026. Ordinal 04 matches inventory SHA-256 `84091e79919194022bdb13fe0a3600690215e72380b1031a12885a0c4cf3e636`; retained Domain 1 Markdown digest remains `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`.

Unit 03 distinguishes EC2 Image Builder, CodeDeploy, EKS workload controllers and Amplify Hosting by their jobs and target platforms. Image Builder produces, tests and distributes machine/container images; CodeDeploy delivers application revisions only on documented EC2/On-Premises, ECS and Lambda platforms using different mechanics; the EKS workload path remains Kubernetes-specific; Amplify Hosting connects Git branches to web-app build/hosting. This corrects a consequential service-boundary weakness: similar “deploy” language does not mean interchangeable controllers. The current tool/reference sources were checked before authoring.

The deployment-storage assessor evaluates five changed-context cases and requires learners to separate image creation from application rollout and application rollout from customer-data preservation. It remains a design exercise. No CodeDeploy agent, Image Builder pipeline, AMI, container registry, cluster, Amplify connection or cross-account share was configured. The task's four implementation skills remain separate and unmapped by this review; no exam readiness is inferred.
