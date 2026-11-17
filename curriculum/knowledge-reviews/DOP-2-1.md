# Individual knowledge review for DOP-C02 task 2.1

Internal editorial review, October 19, 2026. The official objective asks learners to define cloud infrastructure and reusable components over their lifecycle. The three knowledge bullets cover IaC tools, change management, and configuration-management services. The source ordinals are editorial identifiers, not AWS-issued learning results. [Official Domain 2 source](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain2.html).

The current AWS objective page was checked against all three stored source-bullet digests. Each mapping is partial: evidence here means the prose and exercises were inspected, not that a learner passed, a full toolchain was implemented, or the certification objective is complete.

## IaC approaches and reusable components — knowledge 01

[Unit 09](../../reader/BOOK-LOCATORS.md#book-485621100165252b) explains desired configuration, proposed changes, ownership, state and acceptance through a concrete equipment-record story, then uses Terraform lifecycle/recovery examples and S3 remote-state collaboration design. [Unit 16](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e) compares CloudFormation modules, CDK constructs and Service Catalog products as different ways to package or distribute reusable infrastructure. Cases 19–20 ask who authors, deploys and constrains a reusable baseline and why syntax validation does not establish safe defaults.

This is an ELI5 overview and design comparison. It does not teach complete CloudFormation, SAM, CDK or Terraform application authoring/deployment across representative workloads. There is no live AWS execution or independent learner review. The four associated skill mappings remain partial for the same reason.

## Change management for IaC — knowledge 02

| Decision | Teaching and evidence | Limit |
| --- | --- | --- |
| Determine the proposed consequence | Unit 09 explains reviewing the planned action and distinguishing create/update/replacement; local lifecycle controls reject stale or wrong-history state. | Local model and Terraform built-in only; no AWS provider replacement behavior tested. |
| Preserve an object through source refactoring | The local address-migration control preserves the test object's ID and revision; a negative control proposes delete/create. | It does not prove every Terraform migration or CloudFormation/CDK refactor is safe. |
| Recover the management record | Local serial/lineage rejection and snapshot restoration distinguish the intended history from a plausible but wrong snapshot. | No recovery of external state or customer resources. |
| Coordinate writers | Unit 09 explains S3 backend collaboration with `use_lockfile = true`, backend IAM, versioning, lock behavior and migration considerations; the [remote-state design exercise](../../examples/remote-state-design/README.md) adds six changed cases. | No backend, lock contention, AWS plan/apply, partial apply or remote recovery was performed. |
| Handle drift and partial operations | The lesson distinguishes intended state from observed differences and asks for staged review, stop ownership and customer acceptance. | No fresh drift scan or AWS partial-failure rehearsal. |

The [infrastructure review](../../examples/infrastructure-review/README.md) adds seven cases involving replacement, environment state, unknown operation status, stale snapshots and acceptance evidence; its separate assessor rejects a green command as sufficient acceptance. This supports partial knowledge coverage. A broader claim requires scoped AWS implementation, remote lock and recovery evidence, drift/partial-failure rehearsal, an approved promotion path and customer-level acceptance checks. Independent learner assessment remains open.

## Configuration-management services and strategies — knowledge 03

[Unit 16](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e) compares AppConfig for gradual application settings, Systems Manager State Manager for desired state on managed nodes, AWS Config for configuration history/rule evaluation, and OpsWorks as a historical exam term that is no longer a currently deployable choice. Cases 18 and 20 require selection from the thing that changes, explain service boundaries and reject syntax-only safety claims. Current AWS sources are linked in the lesson.

This is service-selection teaching, not a configured comparison. No node association, AppConfig deployment, Config recorder/rule, alert, permissions, rollback or cost was tested. AWS's service lifecycle may change; refresh the official status and feature details before an implementation decision. Independent learner review remains open.

## Related skill review and scope boundary

The [individual skill review](../skill-reviews/DOP-2-1.md) maps each of task 2.1's four skills to specific Unit 09/16 content and cases 15–20. All four are partial: composing/deploying IaC templates lacks an end-to-end tool implementation; StackSets remain design-only; service selection is not live-configured; and reusable templates lack deployed policy checks. The personal Free-plan lab remains outside Organizations-dependent exercises.
