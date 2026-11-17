# Five AWS boundaries, one small design review

This is a design-only learning exercise for the five knowledge points in [SAA-C03 task 1.1](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain1.html#solutions-architect-associate-03-domain1-task1). Read the linked lesson sections first, answer without opening the assessor, then change one fact in each case. No AWS account, identity, policy, resource or bill is touched. These short cases practice decisions; they do not predict an exam score.

## The shop in the story

Harbor Repairs has a small Amplify-hosted customer website, one development account, one production account, a few employees who already use a company sign-in system, and customers who sign in to the application. Its records must be available during ordinary equipment failures, and the team has a limited learning budget.

An AWS account is like a separately managed workroom. A Region is a broad geographic area; Availability Zones are separate locations within a Region. The building analogy helps start a design, but AWS placement, service scope and failure behavior must be checked for the actual service. AWS operates some parts of a service; the customer still owns the choices and configuration that AWS leaves to them. “Managed” does not mean “no responsibilities.”

## Your five decisions

For each case, write: **decision; reason; who owns the next action; what fact would change your answer; and evidence you would need before a real change.** Use the lesson links and current AWS documentation; do not paste credentials or real customer data into an AI assistant.

1. **Separate rooms.** A trainee is testing Terraform in the same account as the production site. The trainee asks for administrator access “just for the weekend.” Choose a boundary or explain why you would keep one account for now. Trace how a cross-account deployment would be allowed, and name one important thing the account boundary alone does not prevent. Then change the case: a shared identity role can administer both accounts.
2. **Company sign-in.** An employee changes teams and then leaves the company while holding a temporary AWS role session. Compare individual IAM users with federated workforce access. Explain separately how the person proves who they are, which AWS role they receive, how future access stops, and what must be checked about an already-issued session. Then change the case: this is a customer signing into the website, not an employee signing into AWS.
3. **Two kinds of location.** A booking application runs in two Availability Zones in one Region. The owner says it is now protected from every geographic outage. Explain which failure scope the design addresses and what a second Region would add. Identify at least three dependencies beyond compute that need review, and name the latency, data-location and cost questions. Then change the case: the requirement covers a single machine failure only.
4. **Smallest useful permission.** A publisher needs to update one development app from reviewed GitHub commits. A colleague proposes `AdministratorAccess` because the first deployment is failing. Describe the smallest job you can specify: actor, action, resource, conditions and duration. Trace any downstream deployment or service role the first publisher can cause AWS to use. Then change the case: the publisher must also edit its own trust policy.
5. **Who maintains what?** AWS manages the underlying hosting service, while Harbor chooses build settings, application code, customer data and access. Sort the actual work into AWS-owned, Harbor-owned and shared/configuration-dependent responsibilities. Do not assume every AWS service has the same boundary. Then change the case: a self-managed virtual machine replaces the managed hosting service.

## Use Codex as a tutor, not the answer key

First answer the five cases yourself. Then ask Codex to find a missing actor, boundary or cost assumption and request a source for any AWS behavior it asserts. Record your original answer, the critique, your revision and what you verified. A fluent explanation is not proof that a role works or that a control denies access.

## Response record

| Case | My decision and reason | Changed fact and revised decision | Source or evidence still needed |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

Continue with the deeper [identity and authority lesson](../../reader/BOOK-LOCATORS.md#book-47726780fac09ca7), [accounts and governance lesson](../../reader/BOOK-LOCATORS.md#book-71a7c1be66a5700e), [recovery lesson](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d), and [permission review](../permission-review/README.md). The larger exercises add policy and recovery details that this foundation exercise intentionally leaves out.
