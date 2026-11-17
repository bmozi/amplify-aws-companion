# Give the publisher a badge for one website branch

Maya keeps her repair guide in GitHub. A new commit is a changed recipe; it does not mean the visitor has seen a new page. To publish a static build, a GitHub job needs a temporary AWS identity that may deliver files to **one** Amplify Hosting branch. It should not gain permission to create an app, change the notebook backend or administer the account merely because the guide changed.

**Your task.** Trace a proposed release through four separate questions: Did a job start? Could that job obtain the AWS role? Which AWS actions and resources would the role permit? What did a visitor actually receive? You can answer the source and local-model questions without an AWS account. A current cloud answer requires an authorized, cost-reviewed observation.

## Four checks that do different jobs

| Check | Where it lives in this example | What it can establish |
| --- | --- | --- |
| Release choice | The manual [publication workflow](../examples/github-workflows/amplify-publish.yml), its `confirm_publish` and `cost_scenario` inputs, and the repository's `AMPLIFY_PUBLISH_ENABLED` variable | Whether this **workflow's** jobs are eligible to start under the checked source and current inputs |
| Badge issuer and wearer | The OIDC provider and proposed `aud`/`sub`/`workflow`/`job_workflow_ref` conditions in the [parameterized Terraform role source](../infra/github-publisher/main.tf) | Which matching GitHub token the **source candidate** would admit; installed trust needs separate readback and this is distinct from the release variable |
| Badge's permitted work | The role's policy in that same Terraform source | In source, `CreateDeployment` and `StartDeployment` target one Amplify branch, `GetJob` targets jobs under it, and two reads support the Free-plan and named-budget gates |
| Result | The Amplify job, exact served static marker and an authorized customer-path check | Whether files were deployed and whether the application fulfilled a separate customer promise |

Think of a delivery switch, a building badge, the rooms printed on the badge and a customer's receipt. Turning off the delivery switch does not revoke the badge. Having the badge does not prove a parcel was delivered. A successful parcel delivery does not prove a private note was saved or another user was denied.

The [caller](../examples/github-workflows/amplify-publish.yml) is manually triggered and defaults to `confirm_publish=no` and `cost_scenario=review_needed`. Its typecheck and the [reusable workflow's](../examples/github-workflows/reusable-amplify-publish.yml) build job have no AWS role. That reusable workflow creates its own ZIP; its separate publish job must pass the reviewed cost record before requesting an OIDC session. This is a description of the checked-in source, **not** evidence that the job has run or that any current account state still matches an older observation. The [dated probe case](GITHUB-PUBLISHER-EVIDENCE-CASE.md) distinguishes one observed role assumption and two account reads from the still-unobserved GitHub publication and customer result. The dated probe called read APIs while assuming the publication-capable role. The checked-in replacement targets a separate read-only role and stays disabled until that role is installed and verified.

## Inspect the parts without copying the owner's destination

Start at `infra/github-publisher/main.tf`. The `account_id`, `amplify_app_id`, `amplify_branch`, budget name and GitHub owner/repository identities are **inputs**. The source derives one Amplify branch ARN and one GitHub token subject from them, then proposes separate publisher and probe trusts. In a reader's design, write fictional values on paper and label them fictional; do not reuse the author's account, app, repository IDs or private `terraform.tfvars`. Check whether an OIDC provider already has an owner before assigning Terraform lifecycle responsibility. The source's `prevent_destroy` guard on a newly created account-level provider is a stop for an ordinary destructive plan, not proof that no other stack uses it.

Read the trust and permission blocks separately. The trust matches the GitHub token audience and the configured repository/branch subject. The permission policy names the limited Amplify actions, one branch and its jobs; it also includes only the selected account-plan and budget reads for its preflight. This policy is an **allow list inside one role**, not a ceiling on permissions another policy might add. Review the actual role's complete grants and applicable controls before making an effective-access claim. AWS documents that OIDC roles have a trust policy and a separate permissions policy; GitHub documents the provider URL and `sts.amazonaws.com` audience for its AWS integration. [AWS OIDC role guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html), [GitHub OIDC in AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).

The example publishes a **static** frontend through Amplify's manual deployment API. AWS documents manual Hosting deployment without a connected Git repository and says that route does not support server-rendered applications. A team whose first HTML response must be generated per visitor needs another reviewed hosting design. [AWS Amplify manual deployment](https://docs.aws.amazon.com/amplify/latest/userguide/manual-deploys.html), [Amplify IAM action reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amplify.html).

## Predict, then test the local model

Write an answer before running the lab:

1. Someone pushes a documentation commit to `main`. The manual workflow has not been started. Which source changed, and what visitor evidence is still missing?
2. The publication variable is false. A **different** workflow on the same trusted branch asks for an OIDC token. Does the variable itself change the AWS role's trust condition?
3. A job has the right token but tries to deploy another Amplify branch. Which boundary should refuse it, assuming no other permissions are attached?
4. The intended branch reports a completed deployment, but the customer cannot save a private note. Which receipt was obtained, and which application path still needs investigation?
5. A whole-run estimate exceeds the chosen lab limit, or the current Free-plan/credit/budget read is unavailable. Where must publication stop? What remains hosted from an earlier release?

Run the [fictional OIDC trust lab](../examples/oidc-trust-boundary/README.md) and its separate [assessor](../examples/oidc-trust-boundary/ASSESSOR.md). It reads the Terraform trust source and compares invented token claims; it does not request a GitHub token or contact AWS. The [publisher exercise](../curriculum/EXERCISES.md#e28) adds changed workflow and cost cases. Keep your unaided answer, local observation and any Codex critique in separate columns. Ask Codex to find a path that bypasses the publication variable, then check its claim against the actual trust block and workflow. Do not give it a real token, credential or private account receipt.

**Reasoning check.** A push only changes source in case 1. In case 2, the variable governs jobs that read it; the AWS trust rule must be evaluated separately, and the earlier probe shows one second-workflow assumption at its recorded date. Its read calls do not narrow the role it assumed. In case 3, the branch-scoped permission is the intended AWS action boundary, subject to the actual role's other grants and controls. In case 4, a Hosting result does not prove Cognito, AppSync, Data or customer authorization. In case 5, hold before requesting publication authority or calling Amplify; a failed new release does not delete already hosted files or backend resources.

Before a live experiment, name the account, Region, scoped non-root role, selected app and branch, complete AWS **and GitHub** usage estimates, current credit terms, a spending limit and credit reserve chosen for that account, stop rule, cleanup owner and later billing check. Neither an estimate nor a budget alert is a hard spending cap. The account-level provider and role need their own lifecycle review. Organization-dependent examples remain design-only until the required account and authority exist.
