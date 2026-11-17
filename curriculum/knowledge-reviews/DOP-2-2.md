# Individual knowledge review for DOP-C02 task 2.2

Internal editorial review, October 19, 2026. The official task asks learners to automate creating, onboarding and securing accounts in a multi-account or multi-Region environment. Its one knowledge item concerns AWS account structures, best practices and related services. The source ordinal is editorial, not an AWS-issued learning result. [Official Domain 2 source](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain2.html).

## Explanation and practice

[Unit 16](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e) now follows an account from owner/request decisions through creation or invitation, baseline, access, operational acceptance, recovery and cost review. It distinguishes basic Organizations account creation from Control Tower Account Factory, Terraform-based AFT customization and onboarding an existing account. It explains Identity Center groups/permission sets and why a dashboard or successful pipeline is only one part of the evidence. Six new [design cases 21–26](../../examples/governance-review/README.md) cover intake, create-vs-invite, provisioning-tool choice, partial customization failure, multi-account access and Region/control gaps; separate assessor notes provide answer criteria.

The [account-onboarding local companion](../../examples/account-onboarding/README.md) accepts two fictional request packets for human review and rejects eight changed cases involving missing ownership, unaccepted invitation, duplicate request or email, overly broad access, out-of-scope Region, prohibited personal-trial organization work and excessive lab spending/insufficient reserve. It has no AWS credentials or API path. It does not simulate Organizations, Control Tower or IAM behavior.

## Evidence boundary

The inventory retains source digest `4c5e15...`; this turn rechecked the current public objective text but did not recompute the fetched-Markdown digest. Refresh the source copy and digest before release because AWS certification pages can change. This mapping is partial. No organization, account, Control Tower landing zone, AFT pipeline, permission set, security control, billing alert or cross-account role was created or queried. Organization setup remains prohibited in the personal Free-plan trial because it can change plan/credit status. Independent technical and learner review are open. The four associated skill mappings are separately described in the [task 2.2 skill review](../skill-reviews/DOP-2-2.md).
