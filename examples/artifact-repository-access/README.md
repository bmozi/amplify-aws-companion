# Give every release job the right repository key

This design-only exercise supports the first implementation skill in current DOP-C02 task 1.4: configuring security permissions so a pipeline can access an artifact repository. It does not create or edit AWS permissions. Read the [identity lesson](../../reader/BOOK-LOCATORS.md#book-47726780fac09ca7) first, answer each case, then use the [assessor notes](ASSESSOR.md).

For every proposed request, write:

1. **Caller:** the human, build role, publisher role, deployment role or service runtime role.
2. **Action:** the actual read, publish, retrieve or policy-change operation.
3. **Resource:** the exact domain/repository/package, ECR repository, S3 bucket/object or destination.
4. **Policy locations:** identity permission, resource policy and any boundary, session, organization, endpoint or key policy that applies.
5. **Evidence:** the smallest safe allowed request and a meaningful out-of-scope request, with the actual assumed principal and denial reason recorded.

Assume the project is a web service that consumes open-source packages, publishes one reviewed internal package and deploys a container. The repository and role names below are fictional. Each case changes the authorization path; do not assume that all three repositories use the same IAM actions.

## Cases

1. **The build only needs its ingredients.** A pull-request build reads dependencies from a CodeArtifact repository. It does not publish packages or deploy an application. Define its intended boundary. Which additional package-manager/token permissions and service conditions must you look up before making a least-privilege policy? Which denied action would reveal an accidental write grant?
2. **A trusted release publishes one package.** A protected release job publishes `@workshop/ui` to one CodeArtifact repository. Separate the build's read permission from the release publisher's write permission. Identify the repository and package resource types, the destination boundary and the administration actions the publisher should not receive. State how your review changes if the client publishes package metadata in addition to a version.
3. **The consumer lives in another account.** A deployment account needs to read a package from a producer account. Draw both sides of the grant. Identify the consumer identity-policy decision, producer domain/repository resource-policy decision and token-service permission. Explain why “the producer account trusted our account” does not by itself prove that a particular deployment role can read the package.
4. **The pipeline is compromised.** A contributor can change the build definition. The build role can publish trusted packages and the deployment role can update production. Trace how the modified build could use each role. Propose a boundary between untrusted pull-request checks, trusted publication and production deployment, including who approves a change to the role/pipeline definitions.
5. **The same word, a different service.** The architecture switches from CodeArtifact packages to an ECR container image, then to a ZIP held in S3. For each, identify the owning repository/resource, the read or write permission boundary and the current primary reference you would inspect. Explain why copying an action name or ARN pattern from CodeArtifact is unsafe.
6. **A denial is not yet a diagnosis.** A pipeline reports AccessDenied. You have only a screenshot of the error. List the missing facts you need before editing a policy. Include identity, action, target ARN, repository owner/account, Region, package-manager operation and relevant policy layers. State what evidence is safe to collect first.

Keep the exercise design-only. If a later cloud test is proposed, separately check the current repository configuration, identity, service actions, token behavior, cost and cleanup. Choose whole-run spending and reserve limits from the account's current terms. Stop if the estimate or authorization path is unclear. No organization-based distribution is implemented here.

For AI-assisted critique, give Codex your role table and fictional resource map. Ask it to find missing principals, overbroad actions/resources, forbidden actions that lack a test, and unverified authorization layers. Require current AWS primary sources. Do not ask it to apply policy changes. Record what it could not prove, and independently verify action/resource support in the AWS Service Authorization Reference before implementation.

These decision exercises are not calibrated certification questions and do not test AWS authorization.
