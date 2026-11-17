# Individual skill review for DOP-C02 task 2.2

Internal editorial review, October 19, 2026. The [official objective](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain2.html) lists four account-governance skills. These mappings are partial, design-only for Organizations operations, and not evidence of certification readiness or independent learner performance.

## Standardize and automate account provisioning — skill 01

[Unit 16](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e) now teaches a request-to-acceptance chain with separate create-new and invite-existing paths, cost/recovery ownership, baselines, access, smoke tests and handoff evidence. The [account-onboarding local lab](../../examples/account-onboarding/README.md) checks fictional requests for ownership, uniqueness, branch-specific proof, baseline, least-privilege test evidence, budget and recovery. It tests 2 positive packets and 8 blocked changes, without making service calls.

Partial: this local gate is not a provisioning engine or idempotent AWS workflow. No Control Tower/AFT request, account, baseline, role, security service, notification or bill was created. A full practical assessment needs an authorized organization, selected supported workflow, scoped operator, state reconciliation after failure, measured cost and cleanup.

## Create, consolidate and centrally manage accounts — skill 02

Unit 16 distinguishes direct Organizations creation, invitation and acceptance of an existing account, Control Tower Account Factory, and AFT's Terraform-request/pipeline path. Cases 22–24 require the learner to account for owner consent, discovery, prereqs, baseline deployment, partial customization failure and recovery before retry. The account-onboarding companion stops an invited-account packet without acceptance or a separate access proof.

Partial and design-only. No account was created, moved, consolidated, enrolled or closed; no OU controls, identity integration, baseline or AFT pipeline were observed. A real assessment requires a separately authorized organization and proof of account lifecycle, operating ownership, cost and recovery.

## Apply IAM solutions across multiple accounts — skill 03

Unit 16 explains Identity Center groups and permission sets as reusable job recipes that create managed roles in assigned accounts, then separates those grants from SCP ceilings and resource-specific policies. It keeps routine workloads out of the management account. Cases 22 and 25 ask for an approved identity path, intended allow, unrelated deny and recovery owner. The local packet check rejects a broad-access example as incomplete evidence.

Partial. No identity store, group, permission set, assignment, role trust or policy was configured or tested against AWS. Actual session identity, permissions, cross-account path, MFA, allowed/denied action and recovery remain unverified.

## Implement governance and security controls at scale — skill 04

Unit 16 distinguishes preventive, detective and proactive Control Tower controls, describes their implementation families and asks readers to check OU, service, resource and Region applicability. Cases 24 and 26 require an evidence-based response to a partially enrolled account and a green dashboard with a broken application path. Existing lesson sections cover SCPs, trusted access, delegation and account lifecycle.

Partial. No Control Tower control, AWS Config rule, CloudFormation hook, Security Hub or GuardDuty integration, cross-Region rollout or remediation was enabled/tested. A practical assessment must validate current supported Regions and resource coverage, actual enforcement/detection, least privilege, response and recovery, cost and cleanup in an approved suitable organization.

## Current sources and safety boundary

AWS documents that new Organizations member accounts receive the default `OrganizationAccountAccessRole`, whereas invitations do not automatically create it. Control Tower Account Factory requires an existing landing zone and registered OU; AWS documents that a customization failure can leave an account existing but not enrolled/customized. AFT adds a Terraform-based account request pipeline, and IAM Identity Center permission sets create managed account roles. Control types have distinct preventive/detective/proactive mechanisms. See links in Unit 16 and the individual knowledge review.

Do not run Organization or Control Tower exercises in this personal trial. AWS warns organization/Identity Center setup can affect Free plan and credit state. This review does not authorize or perform AWS sign-in or deployment.
