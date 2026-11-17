# What to learn first, and how to show it

Generated from `prerequisites.json`, `chapter-evidence.csv` and the [current book chapter map](../reader/BOOK-LOCATORS.md#book-b15b8fcb83e64495). The numbered learning steps below are an earlier dependency plan, **not** the book's chapter numbers. Each step links to its actual book chapters. These are proposed learning dependencies and original assessment prompts, not verified learner outcomes.

## Use the map like a driving lesson

Before driving on a busy road, a learner should be able to steer, stop and explain the signs. Reading the steering chapter alone does not demonstrate that ability. Here, a prerequisite names a capability to check before adding complexity. A reader with prior experience can demonstrate it rather than reread every page.

Start with the file/Git/JSON checks in [learning routes](LEARNING-ROUTES.md). Choose a route below. For each learning step, inspect its linked current book chapters and evidence scope, attempt the exit challenge, then record what you actually demonstrated. If the needed lesson or implementation is missing, mark that requirement pending; an outline is not a substitute.

Local or design-only evidence supports only that level of practice. A successful local permission fixture does not waive the scoped-role prerequisite for AWS deployment. Organization-dependent exercises stay design-only until the required account and authority exist. Before a live run, identify the account, Region, identity, service eligibility, complete estimate, spending limit and credit reserve chosen for that account, stop conditions and cleanup owner.

## Route order

These sequences include the transitive prerequisites of their targets. They are editorial recommendations, not official AWS certification prerequisites. Repeated topics can be demonstrated once and revisited when the changed scenario exposes a weakness.

| Route | Learning steps in dependency order | Exit steps |
| --- | --- | --- |
| Beginner | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 | 4, 13, 14, 15 |
| Operator | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 22, 23, 27, 30, 31 | 31 |
| Architect | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 32, 34 | 32, 34 |
| Certification Review | 1, 2, 3, 5, 7, 8, 12, 15, 33 | 33 |

Read the step numbers in this table against the step headings below, where each one names its current book chapters. The certification-review sequence is only a starting diagnostic. Add the practical route matching the selected exam and the official task/skill ledger; completing learning step 33 does not establish advanced exam coverage. The architect route includes operating foundations because a design must account for deployment, failure and recovery.

## Record a bounded learning result

Use the [learning-record worksheet](LEARNING-RECORD.md) for a copyable form and a worked example. For every attempt, record learning step and current book chapter, challenge variant, source revision, environment, assistance used, observations, explanation and unresolved limitations. Use these four decisions instead of a single optimistic completion percentage:

| Dimension | Sufficient for this practice attempt | Needs another attempt |
| --- | --- | --- |
| Explain | Predict the outcome and explain the relevant boundary in your own words | Repeat service names or an AI answer without explaining the mechanism |
| Demonstrate | Supply the named evidence at the declared local/design/live scope | Supply a screenshot or green check that does not test the claim |
| Transfer | Update the decision when the challenge changes a constraint | Copy the original solution despite a changed invariant |
| Bound the claim | Name untested behavior, data/access limits, costs and cleanup | Claim cloud enforcement, recovery or learning from an unrelated local test |

Do not average away a material failure. Unauthorized disclosure, an unbounded live experiment, or invented evidence requires correction before that attempt can count as sufficient. These are provisional assessment criteria, not statistically validated scoring thresholds. A self-assessment and an independent assessor judgment are separate records.

Use Codex for the guided pass: ask it to explain one concept, then ask you to predict a result before revealing the answer. For the exit attempt, withhold the worked solution, disclose assistance, and separate your unaided explanation from generated code. An assessor should ask a follow-up that changes one requirement.

## Learning-step checks

Each linked starting point exists today. It may cover only part of the challenge. The [planning-step artifact map](chapter-evidence.csv) lists supporting files and remaining work; each step's current status is reproduced below to avoid presenting this map as delivered instruction.

### Learning step 1: A business request becomes an application

Current book chapters: [Chapter 1: Customer request](../reader/BOOK-LOCATORS.md#book-16b52b3769a877e6).

Prerequisite steps: Entry file/Git/JSON checks. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Trace one business request through identity, processing, storage and response.

**Changed-case challenge:** A booking succeeds but its confirmation is lost. Draw what is known and what remains uncertain; propose the next observation.

**Evidence to supply:** Annotated request path and observation-versus-assumption list.

Current starting material: [01-request-to-system.md](../reader/BOOK-LOCATORS.md#book-16b52b3769a877e6).

### Learning step 2: Accounts, identity and cost

Current book chapters: [Chapter 3: Identity and authority](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [Chapter 2: Cost and context](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

Prerequisite steps: 1. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Separate account, application and deployment identities; bound an experiment before launch.

**Changed-case challenge:** A teammate proposes using root because a deploy fails. Identify the missing evidence and prepare an account/region/role/cost/cleanup record.

**Evidence to supply:** Identity responsibility table and priced-run checklist; live role and alert proof remain separate.

Current starting material: [06-identities-and-authority.md](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [04-cost-and-context.md](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

### Learning step 3: Network and data basics

Current book chapters: [Chapter 4: Network paths](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [Chapter 5: Compute and data](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239).

Prerequisite steps: 1, 2. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Explain network stages and preserve meaning across data representations.

**Changed-case challenge:** An amount arrives as a decimal string and a request returns 403. Identify the data-unit and network/application questions separately.

**Evidence to supply:** Canonical data example and failure-boundary explanation; local network observations where available.

Current starting material: [05-network-paths.md](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [02-compute-and-data.md](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239).

### Learning step 4: First Amplify application

Current book chapters: [Chapter 6: First Amplify app](../reader/BOOK-LOCATORS.md#book-e8d9fb108293da29).

Prerequisite steps: 2, 3. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Choose the Amplify pillars a requirement actually needs, then connect the first application to its resource owners and identities.

**Changed-case challenge:** A public-menu site gains private orders and photo uploads. Explain which Amplify parts are needed at each stage. Then a second customer tries to read the first customer's note: demonstrate the expected denial and trace which component enforces it.

**Evidence to supply:** A bounded capability/owner map plus application request and denial evidence; personal live reproduction awaits scoped identity. The written capability choice does not substitute for the live denial.

Current starting material: [lesson.html](../app/public/lesson.html), [26-first-amplify-application.md](../reader/BOOK-LOCATORS.md#book-e8d9fb108293da29).

### Learning step 5: Permissions and ownership

Current book chapters: [Chapter 3: Identity and authority](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [Chapter 9: Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [Chapter 4: Network paths](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [Chapter 22: Tenant isolation](../reader/BOOK-LOCATORS.md#book-422c5f26d4302648), [Chapter 28: Accounts and governance](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e).

Prerequisite steps: 2, 3. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Trace direct and delegated authority for a specific action.

**Changed-case challenge:** A publisher can pass a broad execution role. Explain why its narrow-looking entry policy is insufficient.

**Evidence to supply:** Actor/action/resource table, delegation path and representative allow/deny tests or explicit pending status.

Current starting material: [06-identities-and-authority.md](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [19-data-protection.md](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [05-network-paths.md](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [11-tenant-isolation.md](../reader/BOOK-LOCATORS.md#book-422c5f26d4302648), [identity-at-scale.svg](../book/figures/identity-at-scale.svg), [protective-controls-at-scale.svg](../book/figures/protective-controls-at-scale.svg), [16-accounts-and-governance.md](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e), [SOA-4-1-4-2.md](../curriculum/skill-reviews/SOA-4-1-4-2.md).

### Learning step 6: Terraform, CDK and CloudFormation boundaries

Current book chapters: [Chapter 7: Infrastructure ownership](../reader/BOOK-LOCATORS.md#book-485621100165252b).

Prerequisite steps: 4, 5. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Assign one infrastructure owner and explain a proposed change before applying it.

**Changed-case challenge:** A plan unexpectedly replaces a resource after a teammate changes state. Stop, reconcile source/state/remote observations and propose recovery.

**Evidence to supply:** Saved plan explanation and local lifecycle evidence; remote state and drift checks labeled separately.

Current starting material: [09-infrastructure-ownership.md](../reader/BOOK-LOCATORS.md#book-485621100165252b), [FIELD-LAB-READER-PLAYBOOK.md](../docs/FIELD-LAB-READER-PLAYBOOK.md).

### Learning step 7: Compute choices

Current book chapters: [Chapter 5: Compute and data](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [Chapter 26: Containers](../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5), [Chapter 30: Quotas and Regions](../reader/BOOK-LOCATORS.md#book-98530e7b95042c56).

Prerequisite steps: 3, 5. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Select compute from duration, arrival pattern, dependencies and operating responsibility.

**Changed-case challenge:** A short request becomes a long-running task requiring an OS dependency. Compare two feasible compute paths and reversal conditions.

**Evidence to supply:** Decision record with constraints, capacity assumptions and a measurement plan.

Current starting material: [02-compute-and-data.md](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [15-containers-and-service-replacement.md](../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5), [22-quotas-and-regional-readiness.md](../reader/BOOK-LOCATORS.md#book-98530e7b95042c56), [DOP-3-2.md](../curriculum/knowledge-reviews/DOP-3-2.md), [DOP-3-2.md](../curriculum/skill-reviews/DOP-3-2.md), [SOA-2-1.md](../curriculum/skill-reviews/SOA-2-1.md).

### Learning step 8: Storage and database choices

Current book chapters: [Chapter 5: Compute and data](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [Chapter 9: Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [Chapter 11: Storage access patterns](../reader/BOOK-LOCATORS.md#book-316ad1ab1452bb2f), [Chapter 13: Database read paths](../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828), [Chapter 12: Database selection](../reader/BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa).

Prerequisite steps: 3, 5. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Select storage by access patterns, consistency, lifecycle and recovery needs.

**Changed-case challenge:** Two buyers compete for one seat while the business adds invoice joins and photo uploads. Separate transactional, query and object requirements. Then move an appointment display into an in-memory primary and explain what must change before a confirmation receipt is safe.

**Evidence to supply:** Access-pattern table and competing-write evidence; state the tested database boundary. The [local acknowledgment lab](../examples/in-memory-authority/README.md) can supply a narrow restart observation, not an AWS durability result.

Current starting material: [02-compute-and-data.md](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [19-data-protection.md](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [20-storage-by-access-pattern.md](../reader/BOOK-LOCATORS.md#book-316ad1ab1452bb2f), [21-database-read-paths.md](../reader/BOOK-LOCATORS.md#book-8d7fd952f0661828), [25-database-selection.md](../reader/BOOK-LOCATORS.md#book-0fb36d2b3a5c21aa).

### Learning step 9: Networks and private access

Current book chapters: [Chapter 4: Network paths](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [Chapter 29: Hybrid connectivity](../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230), [Chapter 9: Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [Chapter 2: Cost and context](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d).

Prerequisite steps: 3, 5. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Investigate forward and return paths without broadening access blindly.

**Changed-case challenge:** One subnet times out while another succeeds. Trace DNS, routes, traffic rules and application authorization using discriminating observations.

**Evidence to supply:** Topology and ordered investigation record; modeled routes are labeled as models.

Current starting material: [05-network-paths.md](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [18-hybrid-network-paths.md](../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230), [19-data-protection.md](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [04-cost-and-context.md](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [protective-controls-at-scale.svg](../book/figures/protective-controls-at-scale.svg).

### Learning step 10: Separate environments

Current book chapters: [Chapter 8: Environment separation](../reader/BOOK-LOCATORS.md#book-0c50e8451acb85fa), [Chapter 16: Delivery and recovery](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d).

Prerequisite steps: 4, 5, 6. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Separate environment ownership, configuration and lifecycle.

**Changed-case challenge:** A preview needs realistic data but must not read production records. Define identities, data fixtures, naming and cleanup.

**Evidence to supply:** Environment matrix and creation/removal evidence for an authorized environment; otherwise design-only.

Current starting material: [environments.html](../app/public/advanced/environments.html), [23-environment-separation.md](../reader/BOOK-LOCATORS.md#book-0c50e8451acb85fa), [03-delivery-and-recovery.md](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [README.md](../examples/environment-boundary/README.md).

### Learning step 11: Delivery pipelines

Current book chapters: [Chapter 16: Delivery and recovery](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [Chapter 26: Containers](../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5).

Prerequisite steps: 10. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Connect a tested artifact to one release controller and verified running behavior.

**Changed-case challenge:** A healthy build contains the wrong business behavior. Show what prevents promotion and how the previous artifact remains available.

**Evidence to supply:** Artifact identity, gate result and recovery decision; local gate differs from deployed CI.

Current starting material: [03-delivery-and-recovery.md](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [GITHUB-TO-AMPLIFY-FIELD-LESSON.md](../reader/GITHUB-TO-AMPLIFY-FIELD-LESSON.md), [15-containers-and-service-replacement.md](../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5), [DOP-1-3.md](../curriculum/skill-reviews/DOP-1-3.md), [SOA-3-1.md](../curriculum/skill-reviews/SOA-3-1.md), [DOP-1-1-1-2.md](../curriculum/skill-reviews/DOP-1-1-1-2.md).

### Learning step 12: Logs, metrics and traces

Current book chapters: [Chapter 14: Customer outcomes](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d).

Prerequisite steps: 1, 5, 7. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Connect telemetry to a customer outcome while limiting sensitive data and cardinality.

**Changed-case challenge:** CPU is normal but accepted jobs stop completing. Define a useful signal, missing-data interpretation and trace/log correlation.

**Evidence to supply:** Signal calculation and correlated evidence; real alert delivery must be recorded separately.

Current starting material: [08-observe-customer-outcomes.md](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [monitoring-automation-paths.svg](../book/figures/monitoring-automation-paths.svg), [README.md](../examples/monitoring-automation/README.md), [ASSESSOR.md](../examples/monitoring-automation/ASSESSOR.md), [lab.py](../examples/monitoring-automation/lab.py), [test_monitoring_automation.py](../examples/monitoring-automation/test_monitoring_automation.py), [DOP-4-3.md](../curriculum/knowledge-reviews/DOP-4-3.md), [DOP-4-3.md](../curriculum/skill-reviews/DOP-4-3.md), [configuration-change-ownership.svg](../book/figures/configuration-change-ownership.svg), [DOP-5-2.md](../curriculum/knowledge-reviews/DOP-5-2.md), [DOP-5-2.md](../curriculum/skill-reviews/DOP-5-2.md), [incident-evidence-path.svg](../book/figures/incident-evidence-path.svg), [DOP-5-3.md](../curriculum/knowledge-reviews/DOP-5-3.md), [DOP-5-3.md](../curriculum/skill-reviews/DOP-5-3.md), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [security-audit-evidence-path.svg](../book/figures/security-audit-evidence-path.svg), [DOP-6-3-knowledge.md](../curriculum/knowledge-reviews/DOP-6-3-knowledge.md), [DOP-6-3.md](../curriculum/skill-reviews/DOP-6-3.md).

### Learning step 13: Troubleshooting and incident response

Current book chapters: [Chapter 16: Delivery and recovery](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [Chapter 4: Network paths](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [Chapter 15: Incident investigation](../reader/BOOK-LOCATORS.md#book-48004aaa3a73ab7d), [Chapter 14: Customer outcomes](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d).

Prerequisite steps: 9, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Use observations to distinguish incident hypotheses and verify mitigation.

**Changed-case challenge:** An unfamiliar failure resembles a prior incident but affects only one operation. Propose and execute the smallest distinguishing check.

**Evidence to supply:** Timeline, hypotheses, observations, mitigation and repeated customer check.

Current starting material: [03-delivery-and-recovery.md](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [05-network-paths.md](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [28-incident-investigation.md](../reader/BOOK-LOCATORS.md#book-48004aaa3a73ab7d), [08-observe-customer-outcomes.md](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [configuration-change-ownership.svg](../book/figures/configuration-change-ownership.svg), [DOP-5-2.md](../curriculum/knowledge-reviews/DOP-5-2.md), [DOP-5-2.md](../curriculum/skill-reviews/DOP-5-2.md), [incident-evidence-path.svg](../book/figures/incident-evidence-path.svg), [DOP-5-3.md](../curriculum/knowledge-reviews/DOP-5-3.md), [DOP-5-3.md](../curriculum/skill-reviews/DOP-5-3.md), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [security-audit-evidence-path.svg](../book/figures/security-audit-evidence-path.svg), [DOP-6-3-knowledge.md](../curriculum/knowledge-reviews/DOP-6-3-knowledge.md), [DOP-6-3.md](../curriculum/skill-reviews/DOP-6-3.md), [alarm-to-runbook-boundaries.svg](../book/figures/alarm-to-runbook-boundaries.svg), [SOA-1-2.md](../curriculum/skill-reviews/SOA-1-2.md), [operations-two-finish-lines.svg](../book/figures/operations-two-finish-lines.svg).

### Learning step 14: Backup and recovery

Current book chapters: [Chapter 17: Recovery promise](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [Chapter 9: Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d).

Prerequisite steps: 8, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Restore useful business data and measure the full recovery interval.

**Changed-case challenge:** The newest backup is structurally valid but omits a confirmed order. Select evidence before declaring recovery successful.

**Evidence to supply:** Restore integrity and business reconciliation, with measured interval and explicit untested steps.

Current starting material: [07-recovery-as-a-business-promise.md](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [19-data-protection.md](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [SOA-2-2.md](../curriculum/skill-reviews/SOA-2-2.md), [SOA-2-3.md](../curriculum/skill-reviews/SOA-2-3.md).

### Learning step 15: Performance and cost

Current book chapters: [Chapter 14: Customer outcomes](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [Chapter 17: Recovery promise](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [Chapter 5: Compute and data](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [Chapter 2: Cost and context](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

Prerequisite steps: 7, 8, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Compare measured performance against a complete cost model and workload constraints.

**Changed-case challenge:** Traffic doubles while the budget falls. Recalculate units, identify the bottleneck and compare two bounded changes.

**Evidence to supply:** Workload measurements, estimate assumptions and residual costs; distinguish estimates from billing.

Current starting material: [08-observe-customer-outcomes.md](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [07-recovery-as-a-business-promise.md](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [DOP-3-1.md](../curriculum/knowledge-reviews/DOP-3-1.md), [DOP-3-1.md](../curriculum/skill-reviews/DOP-3-1.md), [02-compute-and-data.md](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [DOP-3-2.md](../curriculum/knowledge-reviews/DOP-3-2.md), [DOP-3-2.md](../curriculum/skill-reviews/DOP-3-2.md), [incident-evidence-path.svg](../book/figures/incident-evidence-path.svg), [DOP-5-3.md](../curriculum/knowledge-reviews/DOP-5-3.md), [DOP-5-3.md](../curriculum/skill-reviews/DOP-5-3.md), [04-cost-and-context.md](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d), [SAP-2-6.md](../curriculum/knowledge-reviews/SAP-2-6.md), [SAP-2-6.md](../curriculum/skill-reviews/SAP-2-6.md), [whole-path-performance-boundaries.svg](../book/figures/whole-path-performance-boundaries.svg), [SOA-1-3.md](../curriculum/skill-reviews/SOA-1-3.md), [SOA-2-1.md](../curriculum/skill-reviews/SOA-2-1.md).

### Learning step 16: Request processing

Current book chapters: [Chapter 19: Durable requests](../reader/BOOK-LOCATORS.md#book-0b7eb9d1bab09ff9), [Chapter 24: Events and reports](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9).

Prerequisite steps: 5, 7, 8, 11, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Separate accepted work from completed work and handle retries deliberately.

**Changed-case challenge:** A worker completes an effect but loses its acknowledgment. Trace the retry and explain how duplicate consequences are prevented or reconciled.

**Evidence to supply:** State transitions, stable job identity, failure observations and known atomicity limits.

Current starting material: [REQUEST-PROCESSING-PATTERN.md](../docs/REQUEST-PROCESSING-PATTERN.md), [27-durable-request-processing.md](../reader/BOOK-LOCATORS.md#book-0b7eb9d1bab09ff9), [14-events-and-trustworthy-reports.md](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9).

### Learning step 17: Reservations and transactions

Current book chapters: [Chapter 5: Compute and data](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [Chapter 20: Reservations](../reader/BOOK-LOCATORS.md#book-ffe5a37f32aa3433).

Prerequisite steps: 8, 16. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Enforce a business invariant under competing requests.

**Changed-case challenge:** The last seat is held, then payment arrives after expiry. Define which transition may consume or return capacity before writing code.

**Evidence to supply:** Transition table and concurrency/expiry tests for implemented behavior; existing immediate reservations do not prove holds.

Current starting material: [02-compute-and-data.md](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [reservations.html](../app/public/advanced/reservations.html), [29-reservation-lifecycle.md](../reader/BOOK-LOCATORS.md#book-ffe5a37f32aa3433).

### Learning step 18: Files and media

Current book chapters: [Chapter 21: File intake](../reader/BOOK-LOCATORS.md#book-98f19229e5a86e66), [Chapter 9: Data protection](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [Chapter 4: Network paths](../reader/BOOK-LOCATORS.md#book-6948135871204c55).

Prerequisite steps: 5, 8, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Control a file from intake through inspection, use and deletion.

**Changed-case challenge:** A user replaces bytes after inspection and another user requests the file. Bind inspection to exact content and test access separately.

**Evidence to supply:** Immutable identity/digest, lifecycle transitions and denial evidence; actual scanning remains distinct.

Current starting material: [10-file-intake-and-lifecycle.md](../reader/BOOK-LOCATORS.md#book-98f19229e5a86e66), [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [19-data-protection.md](../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153), [05-network-paths.md](../reader/BOOK-LOCATORS.md#book-6948135871204c55).

### Learning step 19: SaaS tenants

Current book chapters: [Chapter 22: Tenant isolation](../reader/BOOK-LOCATORS.md#book-422c5f26d4302648).

Prerequisite steps: 5, 8, 10. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Preserve tenant context through queries, caches and background jobs.

**Changed-case challenge:** Two tenants reuse the same record ID and one membership is revoked while a job waits. State the required authorization moment.

**Evidence to supply:** Isolation cases across each implemented path and explicit authentication/concurrency limits.

Current starting material: [11-tenant-isolation.md](../reader/BOOK-LOCATORS.md#book-422c5f26d4302648), [tenant-offboarding-boundaries.svg](../book/figures/tenant-offboarding-boundaries.svg), [tenant-job-authority-after-revocation.svg](../book/figures/tenant-job-authority-after-revocation.svg), [tenant-outbox-lost-reply.svg](../book/figures/tenant-outbox-lost-reply.svg), [tenant-fairness-boundary.svg](../book/figures/tenant-fairness-boundary.svg), [tenant-sqs-fairness-choice.svg](../book/figures/tenant-sqs-fairness-choice.svg), [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [architecture.svg](../examples/tenant-entitlement/architecture.svg).

### Learning step 20: Search and analytics

Current book chapters: [Chapter 24: Events and reports](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9), [Chapter 25: Dashboards](../reader/BOOK-LOCATORS.md#book-9a2045b273a89d57).

Prerequisite steps: 8, 18. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Keep search and analytical optimizations consistent with the business question.

**Changed-case challenge:** A late sale is stored under arrival date. Show why a cheaper query can omit it and prove the corrected membership.

**Evidence to supply:** Query text, source layout, exact result IDs and engine work metrics; no inferred cloud-cost percentage.

Current starting material: [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [14-events-and-trustworthy-reports.md](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9), [README.md](../examples/search-index/README.md), [30-dashboards-and-decisions.md](../reader/BOOK-LOCATORS.md#book-9a2045b273a89d57).

### Learning step 21: Events and telemetry

Current book chapters: [Chapter 24: Events and reports](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9).

Prerequisite steps: 8, 12, 16. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Account for duplicate, late, conflicting and missing events.

**Changed-case challenge:** Two registers reuse event IDs and a source disconnects. Update identity scope and explain what a matching manifest cannot prove.

**Evidence to supply:** Event contract, window semantics, reconciliation and checkpoint failure plan.

Current starting material: [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [14-events-and-trustworthy-reports.md](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9).

### Learning step 22: Accounts and governance

Current book chapters: [Chapter 28: Accounts and governance](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e), [Chapter 3: Identity and authority](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [Chapter 2: Cost and context](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

Prerequisite steps: 2, 5, 6, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Match account governance to responsibility and preserve a recovery path.

**Changed-case challenge:** An OU deny blocks a legitimate recovery role. Trace grant versus ceiling and propose staged correction with attachment rollback.

**Evidence to supply:** Design-only account/policy map and reviewed cases; no Organization creation in the personal trial.

Current starting material: [16-accounts-and-governance.md](../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e), [governance-automation-path.svg](../book/figures/governance-automation-path.svg), [account-onboarding-gates.svg](../book/figures/account-onboarding-gates.svg), [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [DOP-2-1.md](../curriculum/knowledge-reviews/DOP-2-1.md), [DOP-2-1.md](../curriculum/skill-reviews/DOP-2-1.md), [DOP-2-2.md](../curriculum/knowledge-reviews/DOP-2-2.md), [DOP-2-2.md](../curriculum/skill-reviews/DOP-2-2.md), [06-identities-and-authority.md](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [identity-at-scale.svg](../book/figures/identity-at-scale.svg), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [protective-controls-at-scale.svg](../book/figures/protective-controls-at-scale.svg), [security-audit-evidence-path.svg](../book/figures/security-audit-evidence-path.svg), [DOP-6-3-knowledge.md](../curriculum/knowledge-reviews/DOP-6-3-knowledge.md), [DOP-6-3.md](../curriculum/skill-reviews/DOP-6-3.md), [04-cost-and-context.md](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

### Learning step 23: Hybrid connectivity

Current book chapters: [Chapter 29: Hybrid connectivity](../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230).

Prerequisite steps: 9, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Design hybrid connectivity around routes, DNS, dependencies and failures.

**Changed-case challenge:** A private application works by IP but fails by name after a link outage. Compare DNS and routing evidence and redundant-path behavior.

**Evidence to supply:** Design-only topology, dependency inventory and failover test plan; no claim of a deployed VPN or circuit.

Current starting material: [18-hybrid-network-paths.md](../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230), [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md).

### Learning step 24: Container platforms

Current book chapters: [Chapter 26: Containers](../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5), [Chapter 16: Delivery and recovery](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [Chapter 5: Compute and data](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239).

Prerequisite steps: 7, 9, 11, 12. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Operate containers through readiness, replacement and bounded shutdown.

**Changed-case challenge:** An old task holds a write while a replacement receives new requests. Show completion or explicit uncertainty before termination.

**Evidence to supply:** Artifact/config identity, client outcome and process logs; local Docker is not ECS or Kubernetes evidence.

Current starting material: [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [15-containers-and-service-replacement.md](../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5), [03-delivery-and-recovery.md](../reader/BOOK-LOCATORS.md#book-02b8b1e13a935d6d), [02-compute-and-data.md](../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), [DOP-3-2.md](../curriculum/knowledge-reviews/DOP-3-2.md), [DOP-3-2.md](../curriculum/skill-reviews/DOP-3-2.md).

### Learning step 25: Migration and modernization

Current book chapters: [Chapter 27: Migration](../reader/BOOK-LOCATORS.md#book-9fb6047993bd4d40).

Prerequisite steps: 8, 9, 11, 14. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Preserve business meaning and authority during migration.

**Changed-case challenge:** The target accepts a new order after cutover and someone proposes returning to the old source. Identify the missing reconciliation.

**Evidence to supply:** Data mapping, write boundary, reconciliation, cutover and rollback limitations.

Current starting material: [12-migration-and-cutover.md](../reader/BOOK-LOCATORS.md#book-9fb6047993bd4d40), [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md).

### Learning step 26: Multi-region recovery

Current book chapters: [Chapter 17: Recovery promise](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [Chapter 4: Network paths](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [Chapter 30: Quotas and Regions](../reader/BOOK-LOCATORS.md#book-98530e7b95042c56).

Prerequisite steps: 9, 14, 25. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Choose regional recovery from data consistency and business objectives.

**Changed-case challenge:** Both regions accept changes during a network partition. Define ownership, conflict handling and failback before promising availability.

**Evidence to supply:** Design comparison, RTO/RPO assumptions, data-loss analysis and a bounded future test plan.

Current starting material: [07-recovery-as-a-business-promise.md](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [05-network-paths.md](../reader/BOOK-LOCATORS.md#book-6948135871204c55), [ARCHITECTURE-STUDIES.md](../curriculum/ARCHITECTURE-STUDIES.md), [22-quotas-and-regional-readiness.md](../reader/BOOK-LOCATORS.md#book-98530e7b95042c56), [SOA-2-2.md](../curriculum/skill-reviews/SOA-2-2.md).

### Learning step 27: Policy and delivery automation

Current book chapters: [Chapter 3: Identity and authority](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [Chapter 17: Recovery promise](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [Chapter 14: Customer outcomes](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [Chapter 10: Security findings](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d).

Prerequisite steps: 5, 6, 11, 22. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Automate reviewed changes without widening the automation identity.

**Changed-case challenge:** A generated policy fixes one denial by granting every role. Trace escalation and design a scoped allowed/forbidden test pair.

**Evidence to supply:** Reviewed policy/plan and release authority chain; local guards are not IAM enforcement.

Current starting material: [06-identities-and-authority.md](../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [PUBLISHER-ROLE-FIELD-LAB.md](../reader/PUBLISHER-ROLE-FIELD-LAB.md), [07-recovery-as-a-business-promise.md](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), [DOP-3-1.md](../curriculum/knowledge-reviews/DOP-3-1.md), [DOP-3-1.md](../curriculum/skill-reviews/DOP-3-1.md), [08-observe-customer-outcomes.md](../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115), [monitoring-automation-paths.svg](../book/figures/monitoring-automation-paths.svg), [README.md](../examples/monitoring-automation/README.md), [ASSESSOR.md](../examples/monitoring-automation/ASSESSOR.md), [lab.py](../examples/monitoring-automation/lab.py), [test_monitoring_automation.py](../examples/monitoring-automation/test_monitoring_automation.py), [DOP-4-3.md](../curriculum/knowledge-reviews/DOP-4-3.md), [DOP-4-3.md](../curriculum/skill-reviews/DOP-4-3.md), [configuration-change-ownership.svg](../book/figures/configuration-change-ownership.svg), [DOP-5-2.md](../curriculum/knowledge-reviews/DOP-5-2.md), [DOP-5-2.md](../curriculum/skill-reviews/DOP-5-2.md), [incident-evidence-path.svg](../book/figures/incident-evidence-path.svg), [DOP-5-3.md](../curriculum/knowledge-reviews/DOP-5-3.md), [DOP-5-3.md](../curriculum/skill-reviews/DOP-5-3.md), [31-security-findings-and-evidence.md](../reader/BOOK-LOCATORS.md#book-367ab937e61db26d), [protective-controls-at-scale.svg](../book/figures/protective-controls-at-scale.svg), [security-audit-evidence-path.svg](../book/figures/security-audit-evidence-path.svg), [DOP-6-3-knowledge.md](../curriculum/knowledge-reviews/DOP-6-3-knowledge.md), [DOP-6-3.md](../curriculum/skill-reviews/DOP-6-3.md).

### Learning step 28: AI assistance and retrieval

Current book chapters: [Chapter 31: Authorized retrieval](../reader/BOOK-LOCATORS.md#book-c7716c08655f741e).

Prerequisite steps: 5, 8, 12, 19. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Keep retrieval permission, source provenance and generated-answer support separate.

**Changed-case challenge:** Access is revoked after retrieval, and the source includes an instruction to reveal another tenant's data. State which gates act independently of a model.

**Evidence to supply:** Retrieval/release denial cases and citation checks; model grounding and injection evaluation require separate tests.

Current starting material: [ai.html](../app/public/advanced/ai.html), [17-authorized-retrieval.md](../reader/BOOK-LOCATORS.md#book-c7716c08655f741e).

### Learning step 29: Human decisions in automated workflows

Current book chapters: [Chapter 23: Human approvals](../reader/BOOK-LOCATORS.md#book-842e431cbcce6c95), [Chapter 24: Events and reports](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9).

Prerequisite steps: 5, 11, 16. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Bind approval to the exact action and handle stale or repeated decisions.

**Changed-case challenge:** A second approver authorizes a changed target after the first approval. Define invalidation and what may execute.

**Evidence to supply:** Action/version/reviewer/expiry records and duplicate-effect checks; real authentication and external effects labeled.

Current starting material: [13-human-approval-workflows.md](../reader/BOOK-LOCATORS.md#book-842e431cbcce6c95), [14-events-and-trustworthy-reports.md](../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9).

### Learning step 30: Reliability experiments

Current book chapters: [Chapter 18: Reliability experiments](../reader/BOOK-LOCATORS.md#book-56c900b7f81568d4), [Chapter 17: Recovery promise](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d).

Prerequisite steps: 13, 14, 15. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Run a reliability experiment with a hypothesis, stop condition and recovery evidence.

**Changed-case challenge:** The experiment produces a different failure than predicted. Stop within its boundary and explain what the result does and does not establish.

**Evidence to supply:** Hypothesis, baseline, bounded fault, observations, stop decision and recovery receipt.

Current starting material: [reliability.html](../app/public/advanced/reliability.html), [24-reliability-experiments.md](../reader/BOOK-LOCATORS.md#book-56c900b7f81568d4), [07-recovery-as-a-business-promise.md](../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d).

### Learning step 31: Operations capstone

Current book chapters: [Chapter 33: Operating decision](../reader/BOOK-LOCATORS.md#book-f37b7b76fb542d53).

Prerequisite steps: 13, 14, 16, 30. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Resolve an unfamiliar operating incident and communicate evidence honestly.

**Changed-case challenge:** Use the operations capstone without its assessor notes; name the unfinished and missed-promise customers, then defend the recovery choice against another plausible cause.

**Evidence to supply:** Incident report, reconciled business results and follow-up checks; fixed fixture analysis is not live operation.

Current starting material: [33-operating-decision-worked-example.md](../reader/BOOK-LOCATORS.md#book-f37b7b76fb542d53), [OPERATIONS.md](../examples/capstones/OPERATIONS.md), [capstone.html](../app/public/advanced/capstone.html).

### Learning step 32: Architect review board

Current book chapters: [Chapter 32: Architecture defense](../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e).

Prerequisite steps: 15, 19, 22, 25, 26. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Defend a design against constraints, alternatives and failure behavior.

**Changed-case challenge:** Use the architecture capstone, then shorten recovery time and add a tenant-isolation requirement. Revise the tradeoff, not just the diagram.

**Evidence to supply:** Requirements, alternatives, cost/recovery/isolation evidence and changed design; independent assessor review still required.

Current starting material: [32-defend-an-architecture.md](../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e), [ARCHITECTURE.md](../examples/capstones/ARCHITECTURE.md).

### Learning step 33: Certification scenario practice

Current book chapters: [Chapter 34: Scenario reasoning](../reader/BOOK-LOCATORS.md#book-f4cbabaed002683d).

Prerequisite steps: 15. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Use certification objectives to locate and remediate demonstrated skill gaps.

**Changed-case challenge:** Explain an original scenario and reject a plausible alternative. For SAP-C03, locate the published Task 4.2 and Skills 4.2.1 and 4.2.4, then carry one booking promise across the five domains and transfer the reasoning to a school-document portal. Explain which part of each skill the fictional case practices and what implementation evidence remains missing.

**Evidence to supply:** An unaided rationale, changed-case response, help level, dated official task/skill link and the missing practical evidence. Advanced scope also requires the corresponding practical route; a mapped case is not a completed skill.

Current starting material: [34-scenario-reasoning.md](../reader/BOOK-LOCATORS.md#book-f4cbabaed002683d), [CERTIFICATION-TO-APPLICATION.md](../curriculum/CERTIFICATION-TO-APPLICATION.md), [EXERCISES.md](../curriculum/EXERCISES.md).

### Learning step 34: Adapt the system to a new business

Current book chapters: [Chapter 32: Architecture defense](../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e), [Chapter 2: Cost and context](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

Prerequisite steps: 25, 32. Current teaching status: **partial**; independent learner review: **pending**.

**Outcome:** Transfer foundations to a new business with different constraints.

**Changed-case challenge:** Adapt the repair workflow to a reservation business with external payments. Identify what carries over and what must change.

**Evidence to supply:** Changed requirements, invariants, architecture decisions and measured acceptance evidence for implemented parts.

Current starting material: [32-defend-an-architecture.md](../reader/BOOK-LOCATORS.md#book-aadca742bfb00b8e), [04-cost-and-context.md](../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d).

## Maintain the dependency decisions

Edit the JSON source or evidence map, then run `python3 scripts/build-prerequisite-guide.py`. The companion checker verifies the graph has no cycles or missing steps, checks the current chapter links and confirms that this guide matches its source. It cannot validate pedagogical ordering, test a learner or infer completion. Revisit a prerequisite when reader observations show it is unnecessary or missing; record the reason in continuity rather than silently promising an easier route.
