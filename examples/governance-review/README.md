# Review a guardrail without applying it

Original design exercise for A07 and proposed chapter 22. No commands, IAM changes, Organizations setup or AWS spending are required. Read [the lesson](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e), write your answers, then consult [assessor notes](ASSESSOR.md). The cases use named actions as policy facts, not deployable JSON.

## A fictional company and its boundaries

Harbor Repairs has an organization root, a Workload OU with one production member account, and a Sandbox OU with one experiment member account. The management account is used for organization administration. An application role named `BookingWriter` belongs to the production account. The action under review is `dynamodb:PutItem` on its booking table.

For cases 1–4 only, assume: the role session is valid; its trust path has already succeeded; the table is in the same account; there are no resource-based grants, session policies, RCP restrictions, endpoint-policy restrictions or other explicit denies; any conditions on the stated allows are satisfied. These assumptions intentionally isolate the identity/boundary/SCP question. They do not describe all real requests.

For each case record **allowed, denied, or insufficient information**, name the controlling fact, and state what evidence would be needed before making the same judgment in a live account.

1. The role's identity policy allows the write. Its boundary allows it. SCPs allow it at the organization root, Workload OU and account. No stated policy denies it.
2. Keep case 1, but remove every identity-policy allow for the write. The boundary and SCP allows remain.
3. Keep case 1, but add an explicit deny for the write to an SCP attached to the Workload OU. Attach a second identity policy that allows the write.
4. The role and boundary allow the write, but the root's only SCP allows `s3:GetObject`. The OU and account each allow all actions. There is no root-level allow for `dynamodb:PutItem`.
5. A colleague adds a narrow S3-only allow SCP to the Workload OU while retaining a broad allow SCP at that same OU. They say this change now blocks DynamoDB. All other facts are those of case 1. Assess the claim.
6. A reviewer says a member-account SCP prevents an outside partner's role from reading a bucket in that member account. The only supplied facts are that the partner role is outside the organization and a bucket policy names it. Can the reviewer conclude the read is denied? List the missing facts.
7. The team calls a new member-account role `BreakGlass`. It has an administrator identity policy. A relevant applicable SCP explicitly denies the recovery action it needs. Can the role perform that action because of its name or administrator policy?
8. The security administrator proposes applying one restrictive SCP everywhere and using it to protect actions performed from the management account too. Identify two reasons to revise this plan before any rollout.

## Lifecycle and delegation cases

These cases concern missing evidence and operating design; they do not inherit cases 1–4's simplified policy assumptions.

9. Harbor invites the acquired company's existing account. An operator assumes `OrganizationAccountAccessRole` must now exist and that all access is ready. Identify the assumption and the access evidence needed before baseline automation can run.
10. A manager moves an account to a “Production” OU and marks partner access reviewed without inspecting any resource policies or old/new parent controls. Explain what the move changes and what it cannot establish.
11. The security account is registered as delegated administrator for one supported service. A developer concludes it can now edit and attach any SCP. Identify the separate mechanism and caller permissions that must be reviewed.
12. A delegation allows specified policy create/read/update actions but does not include attachment actions. The operator says the ability to edit means the policy can be attached anywhere. Explain both the permission distinction and why changing an already-attached policy still deserves impact review.
13. The team disables a service's trusted access and assumes all service use, historical data and charges ended. What must be checked through the service-specific procedure and resource/billing evidence?
14. A project is retired while another workload still reads its encrypted archive. The owner proposes closing the account immediately. Trace the data, key, caller, operational ownership and retention dependencies that must be resolved before any authorized closure plan.

## Reusable baselines and configuration choices

15. Harbor adds 40 member accounts and wants a baseline log destination and deployment role. Compare a manually repeated stack, an Organizations-integrated StackSet, and a staged deployment pipeline. Choose a starting target, rollout wave, operation-failure threshold, stop owner and evidence that shows both stack success and application readiness. State why this remains a design proposal here.
16. An account moves from the Sandbox OU into Production. Its StackSet used automatic deployment and the configured behavior deletes stack instances when accounts leave scope. Identify what may be removed, what may be recreated by the destination OU, and which retained data, dependencies and owner approvals must be checked first.
17. A deployment is reported successful in 15 Regions but failed in one. The operator wants to rerun all Regions immediately. Specify which operation status/details, concurrency or failure-tolerance settings, resource drift and customer-level checks you need before deciding to retry, repair or stop.
18. A team wants a feature to reach 5% of users, a security baseline to stay on enrolled EC2 nodes, and evidence of whether S3 buckets meet encryption rules. Select among AppConfig, Systems Manager State Manager and AWS Config. Name what each choice does not do. A colleague suggests new AWS OpsWorks Stacks; explain the current support boundary while preserving the exam-term distinction.
19. Three departments ask for “the standard private S3 archive.” Compare a CloudFormation module, a CDK construct and a Service Catalog product. Choose based on who authors, reuses, deploys and constrains it. Name the versioning, consumer inputs, role, data-retention, test, cost and removal questions the reusable artifact must expose.
20. A shared template passes syntax validation, but sets no lifecycle rule, permits public access, and creates a writer role broader than the product needs. Decide whether to publish it. Propose checks that catch unsafe defaults and a harmless positive/negative test plan. Explain why a green syntax check is not evidence that the design is safe or affordable.

## Account provisioning and control at scale

21. A product team submits a request for a new “production” account, but has not supplied a business owner, cost owner, classification, allowed Regions, target OU, required access group, recovery owner or monthly estimate. Identify the missing decisions. Which ones can a form validate, and which require an accountable person to decide?
22. Compare creating a new member account with inviting an existing account from the acquired repair company. For each path, draw the first access route and list the evidence that permits onboarding to continue. Do not assume that an accepted invitation created the same role as account creation.
23. The platform team has one new account request per quarter and proposes installing Account Factory for Terraform because it uses Terraform elsewhere. Compare direct Organizations creation, Control Tower Account Factory and AFT by prerequisites, governance outcome, customization path, operating burden and failure recovery. Recommend the least complex viable path and state what must be checked in the current product docs.
24. A member account exists, but its account-customization step failed and it is not enrolled. A retry proposes creating a replacement account under a new email address. Explain how you would inspect and reconcile the existing account and partial resources before deciding to resume, repair or stop.
25. A developer group needs read-only access in sandbox and a scoped deployment role in production. Propose the identity source, group assignments, permission sets and tests. Explain how the Identity Center-generated role, SCP ceiling and resource-level permissions combine, and why ordinary application work stays out of the management account.
26. A control dashboard is green for the OU, but the app cannot reach its logging destination in a newly enabled Region. Separate preventive, detective and proactive controls. Identify which control evidence, regional support, role, network and business smoke checks are needed before declaring the new account ready.

The [local account-onboarding review](../account-onboarding/README.md) adds executable positive and negative request-packet checks. It validates fictional inputs only; it does not call AWS or prove a Control Tower workflow.

Add one lifecycle transition and one specific delegation to the operating design below. Record the successful observation required to advance, a stop condition, responsible operator and recovery path. No account creation, invitation, move, delegation or closure is part of the exercise.

## Produce the operating design

Prepare a one-page change proposal containing:

- The undesirable action and the business reason for restricting it.
- The affected principal/action/resource paths and any necessary exceptions.
- The exact hierarchy/attachment scope and a small first rollout target.
- One intended allow test, one intended deny test and one recovery-path test, all using harmless synthetic resources in a separately authorized organizational environment.
- The prior policy/attachment record, authorized rollback operator and stop condition.
- Audit destination, retention, access ownership, cost assumptions and expiration/review date for temporary exceptions.

No destructive “deny test” should be attempted against valuable data: an incorrect policy might allow it. A written test plan is a design artifact, not an executed test.

## Change the requirement

Harbor acquires a company whose partner integration already uses resource policies. Explain why moving its account under a familiar OU does not automatically establish safe partner access. Draw the identity path and the resource-policy path. Decide which evidence you need before migration, and preserve a safe way to stop the rollout.

Ask Codex to challenge your completed proposal, not to answer first. Require it to distinguish documented policy semantics, exercise assumptions and missing evidence. Do not paste credentials, MFA material, private customer data or live policy attachments into a public learning submission.
