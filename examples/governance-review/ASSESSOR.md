# Governance review: reasoning guide

These practice cases are not a validated exam. Read only after preparing the exercise answers. The decision facts are constrained; these notes do not replace AWS policy evaluation for a real request.

| Case | Expected judgment | Reasoning to look for |
| --- | --- | --- |
| 1 | Allowed under the stated assumptions | Identity grant, boundary and SCP path permit the same operation; no other restriction is in scope |
| 2 | Denied | Boundary and SCPs do not supply the missing identity grant in this isolated path |
| 3 | Denied | Applicable explicit deny defeats both identity-policy allows |
| 4 | Denied | The action lacks an allow at the root level; lower-level allows cannot repair that omission |
| 5 | The claim is false | Policies at the same level combine; the retained broad allow still covers the write, absent a deny |
| 6 | Insufficient information | The member's SCP does not itself limit that external principal; inspect the actual bucket grant, partner authorization, conditions, relevant resource controls and other applicable restrictions |
| 7 | Denied | Neither a role name nor an administrator grant overrides an applicable SCP deny |
| 8 | Revise scope and rollout | SCPs do not constrain management-account principals, and an untested broad attachment can disrupt legitimate operations |

For cases 1–5, require a trace of the hierarchy, not just the right label. For case 6, do not award a confident “allowed” merely because one policy names a principal: the exercise does not supply enough context. For case 7, an exemption would need an actual policy design and authorized access path, not a label. For case 8, staged testing and separate management-account protection are different remedies.

Policy-semantic references: [IAM boundaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html), [SCP scope](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html), [SCP hierarchy evaluation](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps_evaluation.html), [RCP scope](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html). Recheck these sources when the exercise is revised.

## Review the proposal as a whole

A satisfactory draft connects the business restriction to actual request paths, stages the change, preserves a tested recovery path, assigns ownership and accounts for evidence/cost. Missing rollback authority or unexplained broad exceptions are material weaknesses even if all original policy-case labels are right.

Ask the learner to explain one case aloud without the table and adapt it to the acquired company's resource-policy path. Record the answer, errors, revision and remaining uncertainty with consent. No fixed pass score or certification-readiness claim is established by this editorial exercise. Actual learner outcomes remain pending.

For this exercise, a successful submission ends with a reviewed design. It must not create an Organization or deploy these controls merely to satisfy an assessment. Live organizational testing requires a separately authorized suitable environment.


## Lifecycle and delegation reasoning

9. Inviting an existing account does not automatically create the administrative role named in the case. Verify actual trust, caller authority and intended scoped permissions. Organization membership alone is insufficient, and copying a broad role is not the only possible access design.
10. OU placement changes inherited parent policy scope. It does not review existing partner grants, establish application continuity or move data. Compare policy paths and relevant conditions, test access/recovery in a suitable authorized environment and preserve a rollback path.
11. Delegation for one service does not establish Organizations policy-management authority. Review the separate resource-based Organizations delegation and the calling identity's required permissions, including action and target scope.
12. Editing and attaching are different actions. Missing attachment authority is not supplied by an edit grant. However, editing a policy that is already attached can affect existing targets; denying new attachments does not make policy updates harmless. Inspect existing attachments as part of impact review.
13. Follow the selected service's integration-removal procedure and inspect remaining resources, configuration, data and other IAM-authorized access. Trusted-access removal is not universal resource deletion or revocation of all human/workload use. Reconcile costs after observing actual lifecycle changes.
14. Identify the consumer, readable archive copy, encryption/decryption authority, retention owner and continuity requirements. A closure ticket cannot prove the other workload will still read its data. Resolve the dependency and verify the replacement/handoff before an authorized retirement action. This exercise performs no account closure.

## Reusable baselines and configuration choices

15. A StackSet is a reasonable candidate for repeated CloudFormation stacks across accounts and Regions. A strong answer states why an organization-integrated permission model may fit centrally governed accounts, but does not assume organization membership alone supplies all access. Limit the first wave; set operation preferences; name stop authority; check resource-level state and business readiness. This is a paper design only; a real organization rollout requires separate authorization.
16. Leaving an OU can trigger configured deletion or retention of StackSet instances; entering another OU may trigger a new deployment. Read the actual StackSet automatic-deployment settings and target membership before moving the account. Identify stack-managed resources, retained data, external dependencies, owner approval, evidence and cost before any transition. Do not imply that a retained stack instance or resource is automatically adopted by a different StackSet.
17. Inspect the StackSet operation and per-account/Region status, the configured concurrency and failure tolerance, and the affected stack events. Check whether the failure left partial resources or drift and whether retrying can collide with them. Confirm an application-level check and define a stop threshold before retry. A successful operation record alone does not prove the service works.
18. AppConfig fits gradual application settings/feature delivery; State Manager fits desired state on managed nodes; AWS Config records resource configuration and evaluates rules rather than directly applying a fix. AWS documents OpsWorks and OpsWorks Stacks as shut down on May 1, 2024. A learner should still recognize the name if it appears in the objective, while not proposing a new OpsWorks deployment. Verify today's service lifecycle before a real plan.
19. A CloudFormation module packages reusable resource configuration for use within templates. A CDK construct is a reusable code component that can represent one or more CloudFormation resources. Service Catalog publishes products/versions through portfolios and can constrain launch parameters and the launch role. A strong answer chooses the consumer/deployment experience first and records owner, supported inputs, version, least-privilege role, retention/deletion behavior, tests, cost drivers, upgrade and retirement path. These mechanisms overlap but are not interchangeable.
20. Do not publish. The artifact has observable security and lifecycle defects, and syntax validation cannot assess the business/security requirements omitted by the template. Require a reviewed public-access posture, explicit data-retention semantics, scoped actions/resources, policy/static checks, a rendered change review, and positive/negative tests in an authorized isolated environment. Include an estimate, ownership, rollback and cleanup plan. No template deployment or live policy test is part of this exercise.

These are authored criteria, not live invitation, policy, service-integration or retirement results. A complete paper answer identifies both the needed observation and its owner. The real service and account transitions remain unexecuted; independent learner review remains pending.

Cases 15–20 do not measure StackSet behavior or establish an AWS configuration result. Recheck the linked AWS service documentation before converting the design into an implementation plan.

## Account provisioning and control at scale

21. Require the business owner/purpose, cost owner/envelope, data class, Regions, OU, access group, baseline, recovery/operations owner and review date. A form can require values and reject malformed Regions or duplicate request IDs; it cannot invent an accountable business decision. “Production” in the account name does not supply those facts.
22. A newly created Organizations member account receives the default `OrganizationAccountAccessRole` path, subject to actual trust and applicable policy. An invited existing account must accept; Organizations does not automatically create that role for it. For the invite path, inspect the existing access and resource policies and establish a specific approved access path. In either path, verify the identity that will act and the target permissions before baseline automation.
23. Basic Organizations account creation is the smallest direct account-creation path but does not by itself establish the Control Tower landing-zone baseline. Control Tower Account Factory is appropriate when a landing zone and registered OU already exist and the managed account baseline/controls are wanted. AFT introduces Terraform-backed request files and a pipeline for provisioning/customization; it has Control Tower prerequisites and additional repositories/pipeline operations. With one occasional request, that extra machinery may cost more to operate than it saves. Recheck supported backends, regions, versions and account customization in current docs. No choice authorizes a real installation.
24. A failed customization may leave the account present without customization/enrollment. Inspect the known account ID, provisioning request, pipeline stage, stack/control resources, OU placement and any partial resources. Reconcile actual state with desired state and identify an owner for retained resources and cost. Do not create a replacement until identity, account, data and billing implications are resolved. Retry is a decision after inspection, not a reflex.
25. Assign groups to accounts with named permission sets that grant job-specific access. Check the generated role in the target account, intended allow, unrelated deny, current group membership, session duration and recovery operator. IAM identity permissions grant capabilities; applicable SCPs can further restrict them; resource and service policies may add other requirements. Do not place application workloads or routine developer work in the management account.
26. A green control status does not prove application reachability. Identify whether the control prevents an action, detects a noncompliant resource or checks a CloudFormation proposal before creation. Confirm the control applies to the service, Region, resource and OU; inspect its evidence and the app's own role, network route, destination policy and logs. Use a harmless application smoke test and a recovery check before an owner accepts readiness.

The [account-onboarding review lab](../account-onboarding/README.md) is a local guard exercise, not a simulator of these AWS services. A passing result only says the fictional request packet satisfies its stated checks.
