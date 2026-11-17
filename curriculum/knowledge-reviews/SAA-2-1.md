# Individual knowledge review for SAA C03 task 2.1

Internal editorial review, October 18, 2026. Positional IDs below refer to the [official task's separate knowledge list](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task1). Current official Markdown was fetched and the exact bullet hashes matched the existing inventory before these mappings were added. Objectives are paraphrased; none is complete.

## Knowledge 01 API creation and management

Source bullet SHA-256: `f99b8af2bb19c90e59bac76cde9a37daca66adc7b6456fd4fcfe3ce128a3ccd1`.

Teaching: unit 1, “An API is a promise between two programs,” and its receipt, error and API Gateway selection subsections. The original illustration distinguishes lost response from lost work. The [API contract assessment](../../examples/api-contract/README.md) includes six design cases and a separate rationale. The local standard-library lab implements a bounded HTTP contract over loopback with SQLite persistence.

The author's retained bf27242 extracted-package receipt records execution of that lab on a Mac: rollback before durable acceptance, committed work with a deliberately lost reply, caller-scoped stable-key replay, changed-input conflict, fixture ownership denial, six concurrent requests sharing one acceptance, and HTTP success reporting business rejection. That dated receipt remains in an owner-only log; follow the linked [API contract lab](../../examples/api-contract/README.md) to collect your own result. The fixture identities are not authentication evidence, and the generated identifier/temporary database do not establish an AWS API.

Additional API lifecycle teaching now includes the [client compatibility review](../../examples/api-contract/COMPATIBILITY-REVIEW.md) and a local serialized JSON matrix. It demonstrates differing older-client behavior for added fields, a renamed required field, an unknown business state and unsafe old-consumer rollback. This supplies bounded compatibility teaching, not a deployed API version lifecycle.

Remaining: real identity and revocation, selected API Gateway configuration, deployed authorization, request validation and failure behavior, API lifecycle/version compatibility, throttling and abuse handling, polling/load measurements, retry-window expiry, distributed persistence and recovery, prices and teardown. The existing practice does not exhaust API management. The mapping is partial; learner assessment remains pending.

Transfer prompt: a mobile client reconnects after its documented retry window expired and cannot tell whether the earlier request completed. Require an authorized reconciliation path and an honest unresolved outcome rather than a fresh request justified by a timeout. The current lab does not implement expiry; grade the proposed contract as design reasoning only.

## Knowledge 14 Container orchestration

Source bullet SHA-256: `e6de2b56a9eef27625625ba41a73b5c31993191871a444aefc059067ed5ad0a5`.

Teaching: unit 15, “Choose the platform by responsibility,” “Open the Kubernetes box before choosing it,” and its release/readiness/shutdown sections. The lesson distinguishes artifact, desired workload, observed readiness, managed control plane, compute lifecycle and application correctness. The [Kubernetes responsibility review](../../examples/kubernetes-responsibility/README.md) adds six design cases with separate assessor reasoning. Existing service-communication and image-review exercises cover adjacent integration and release decisions without claiming a deployed cluster.

The local Docker exercise has separate recorded lifecycle evidence. It does not run an ECS scheduler or Kubernetes control plane. The new Kubernetes section is source-grounded design teaching; no cluster has been created, no Pod scheduled, and no cloud role or upgrade tested by it.

Remaining: selected ECS/EKS deployment with scoped authority, scheduling and placement behavior, resource requests/limits and representative load, networking/storage integration, workload identity, controlled replacement and drain, version-compatible upgrades/recovery, actual cost and cleanup, and independent learner transfer. The lesson compares responsibility boundaries; it does not claim complete Kubernetes operations training.

Transfer prompt: the initially simple API now depends on a supported vendor controller available only through Kubernetes, while the team still has two operators. Reassess EKS without assuming that the new requirement resolves integration ownership, cost or recovery. Require a tested dependency path and an explicit alternative, such as changing the vendor integration, before treating the choice as settled.

## Knowledge 16 Workflow orchestration

Source bullet SHA-256: `f5134adc309d10f8a6267df80efd8939cdfbecfd19d6892cf188bf88cb32d257`. Fresh official domain-2 Markdown matched that exact positional inventory entry on October 18, 2026; full fetched source SHA-256 was `23b2af5036a5ed0531a7dcd7d7df8f12fc8d7a084efe17e45780381e765bcfb7`.

Teaching: unit 13 separates preparation, review, admission, execution and outcome; explains expiry and cancellation; and compares explicit workflow definitions with code-based orchestration. The [two-reviewer challenge](../../examples/approval-workflow/TWO-REVIEWER-REVIEW.md) and separate assessor guide add eight policy cases and three service-integration selection questions. Official Step Functions integration-pattern and Lambda durable-functions overview pages were rechecked. The current prose preserves service choice as unresolved rather than presenting a local SQLite state machine as an AWS workflow.

The original local lab records an atomic fixture effect; the separate [two-reviewer drill](../../examples/approval-workflow/README.md) records admission only. The author's working-tree receipt in an owner-only log reports distinct eligible non-requesters, revision/digest matching, local revocation, exact expiry, controlled cancellation orders and duplicate concurrent admission. Run the linked drill to collect your own result. The owner's receipt does not establish real identity, callbacks, checkpoint/replay behavior or an external effect. Review and admission evidence must not be used as publication completion evidence.

Remaining: choose and implement the exact workflow/service integration; verify scoped execution and callback authority, input/output boundaries, supported waiting/timeout behavior, retries and duplicate effects, downstream cancellation, history/observability, quotas and recovery, measured cost and cleanup. The code-based alternative needs its own checkpoint/replay and external-effect review. Independent learner transfer remains pending. Coverage is partial.

Transfer prompt: the review must remain open while a downstream asynchronous job runs, but the current integration advances after HTTP acceptance. Require an explicit completion signal or a supported waiting pattern, its failure/timeout behavior and business validation. Then stop the parent workflow in the design: explain why downstream resource and outcome inspection is still needed.


## Knowledge 03 Caching strategies

Source bullet SHA-256: `1ff5fd0fc2cd8e85cf0ac87044452b0b4cb00b58552a23f626e00a2ed7275b9f`. Fresh official domain-2 Markdown matched this positional inventory entry on October 18, 2026.

Teaching: [A cache is a saved answer with a reuse rule](../../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828) and its adjacent explanations. Assessment: [local predictions and changed-case prompts](../../examples/cache-consistency/README.md). Evidence: Cache-aside teaching; local SQLite and in-memory cache hit expiry stale display and explicit stale-repopulation schedule; no distributed cache measurements.

Remaining: Selected managed cache strategy configuration authorization invalidation failure behavior cold-cache load cost and independent learner evidence. This is a partial mapping, not mastery or complete service coverage.


## Knowledge 05 Event-driven architecture

Source bullet SHA-256: `72fb93509a4f4a966b1bd7b5cd4dc2a877e3a50cf3da2e64784db41a753e0f2c`. Fresh official domain-2 Markdown matched this positional inventory entry on October 18, 2026.

Teaching: [The gap between two successful-looking actions](../../reader/BOOK-LOCATORS.md#book-0b7eb9d1bab09ff9) and its adjacent explanations. Assessment: [local predictions and changed-case prompts](../../examples/event-reconciliation/README.md). Evidence: Transactional outbox and consumer-boundary teaching; emulated dispatch evidence; local producer-scoped event deduplication conflicts late arrival and synthetic reconciliation.

Remaining: Selected event transport and routing contracts producer authentication ordering retention replay independent consumers deployed failure recovery cost cleanup and learner evidence. This is a partial mapping, not mastery or complete service coverage.

### Verification scope for the cache and event mappings

Reran `examples/cache-consistency/lab.py`, `examples/event-reconciliation/lab.py` and `examples/event-reconciliation/producer_lab.py` from clean source 5699bb6 before these ledger edits. Each passed. The cache example deliberately reproduces stale display and stale repopulation; it does not solve distributed invalidation. Its tenant cache keys are namespacing, not authentication. The event example reports three accepted events despite eleven delivery attempts; its second pass distinguishes the same local ID from two producers and exposes a falsely complete unscoped manifest. Supplied producer labels and expected manifests are trusted fictional inputs, not source-completeness or identity proof. Reviewed the lesson's source-grounded cache-aside and outbox boundaries; the emulated dispatch checks retain their separate historical verification receipt.

Transfer prompts: require immediate revocation of cached private content, then explain why a tenant-scoped key alone is insufficient. Separately add an independently owned subscriber to the event architecture and identify its own delivery, replay, retention and effect-reconciliation obligations. A queue or cache product name cannot establish either business promise.

## Keep neighboring objectives separate

These mappings now sit alongside individual partial reviews for managed service selection, microservice boundaries, horizontal/vertical scaling, CDN/edge delivery, container migration, load balancing, multi-tier design, serverless patterns, storage interfaces and read replicas. All sixteen knowledge entries have partial mappings, not completion. The workflow and earlier queuing/messaging mappings remain separate. Seventy-six partial skill mappings are another population; do not combine skill and knowledge counts into a mastery score. Give learners the prompts before the rationales and retain their actual responses and assistance records when a trial is conducted.


## Remaining individual knowledge mappings added October 18, 2026

The ten bullets that were still inventory-only have now been connected to exact teaching, an assessment and a remaining-evidence statement. Their retained source hashes were checked against the official task list before acceptance. All remain partial.

| ID | Teaching and assessment | What remains |
|---|---|---|
| 02 — Managed AWS services | Unit 02 explains managed-service responsibilities; the new worksheet contrasts Transfer Family file exchange, SQS task dispatch and Secrets Manager credential storage. | Current selected service features, permission design, failure behavior, complete cost and learner review. |
| 04 — Microservice principles | Unit 02 distinguishes independently operated components and externalized state; service-communication cases test discovery, identity and retry boundaries. | Evidence that separation meets a real requirement, safe state migration, cross-service failure behavior and independent review. |
| 06 — Horizontal and vertical scaling | Unit 02 shows how one constrained database limits extra workers and uses a fictional backlog model; scaling cases change workload shape. | Measured bottleneck, installed control, startup/scale-in/failure behavior and full cost. |
| 07 — CDN and edge accelerator | Unit 05 teaches reusable content, private responses, cache variation and alternatives; the CDN cases change audience, content and authorization. | Selected distribution/function behavior, measured viewer outcomes, current pricing and cache-isolation evidence. |
| 08 — Container migration | Unit 15 now teaches migration as checkpoints for runtime, local state, image, platform, traffic, schema and retirement; new cases change these constraints. | Selected cloud deployment, data migration, identity/network integration, rollback and observed cost; no AWS migration occurred. |
| 09 — Load balancing | Unit 05 distinguishes ALB request routing, NLB transport flows and GWLB inspection; the cost/design cases test protocol, targets, health and placement. | Configured listeners/targets, drain/failover, measured behavior and complete current regional cost. |
| 10 — Multi-tier design | Unit 01 now teaches tiers as responsibilities rather than required servers and includes a new boundary diagram and four changed-case designs. | Selected topology, actual route/identity/policy tests, failure/recovery and current bill. |
| 12 — Serverless patterns | Unit 02 compares function, container and host execution with runtime, duration, state, concurrency and responsibility; compute-selection cases change those needs. | Selected service mode, measured startup/performance, retries, downstream capacity, recovery and full cost. |
| 13 — Storage interfaces | Unit 20 compares object/file/block contracts, concurrency and cost; the storage review supplies changed-workload prompts. | Selected-client compatibility, conflict/recovery tests, measured access pattern and whole cost. |
| 15 — Read replicas | Unit 21 explains asynchronous read lag and consistency and separates replica use from historical recovery; the local example exposes a propagated deletion. | Engine-specific configuration, measured lag/failover, application routing and a tested recovery path. |

These additions improve the knowledge map but do not establish all task skills, a complete deployment guide for each service, cloud evidence, independent technical review or learner mastery. The figure is a working SVG; the working manuscript was structurally rebuilt, but the complete print/ebook visual gate remains pending.
