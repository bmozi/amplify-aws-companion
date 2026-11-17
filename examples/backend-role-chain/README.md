# Follow the role that actually builds

Maya has replaced a root deployment command with a temporary, non-root role. That is a real improvement, but it answers only who starts the request. The CDK deployment also uses bootstrap roles; CloudFormation's execution role can have a different permission ceiling. Work through [Unit 34's two-badge lesson](../../reader/BOOK-LOCATORS.md#book-f2671f1320a930b4) and its [diagram](../../book/figures/cdk-two-badge-deployment.svg) before looking at the assessor notes.

For each fictional case, write three sentences: **what is established**, **what is unknown or unsafe**, and **which read or denial test would change the decision**. Use “hold backend mutation,” “candidate for further review,” or “limited static publication path.” These are review labels, not AWS permission grants.

| Case | Changed evidence |
| --- | --- |
| A | The caller is an assumed role in the right account. The existing CDK execution role has AWS-managed `AdministratorAccess` attached. |
| B | The caller policy names only one Amplify app and one branch. No one inspected the execution role, deployment role, asset roles or stack access. |
| C | The execution role has a reviewed narrow policy and boundary, but a second operator can update the already-created stack. No one reviewed that operator's stack rights. |
| D | The deployment role's `iam:PassRole` permission is denied for the approved CloudFormation execution role. A suggested workaround is to allow every role in the account. |
| E | Attached-policy listing was denied. The local audit printed no `AdministratorAccess` finding. |
| F | The narrow frontend-publisher candidate can create one Hosting deployment and inspect its job. Someone proposes using it to update the Gen 2 backend. |

For **A**, draw all four boxes and identify the first place where the claimed least-privilege boundary fails. For **C**, explain why later stack access matters even if the new operator cannot pass the service role again. For **D**, propose the *scope* of evidence a repair would need without writing a blanket policy. For **E**, distinguish an absent policy from an unread policy. Then change **A**: suppose the execution role is narrowed, but the file-publishing role can upload to a shared asset bucket and the deployer may assume it. Which path must now be reviewed?

The companion's [read-only preflight](../../scripts/backend-role-preflight.py) is the operator tool for a later authenticated session. It discovers all five default CDK role resources in `CDKToolkit` and privately records their trust, attached and inline documents and boundaries. An optional verified `--stack-name` adds the stack's associated service role. Its [synthetic tests](../../scripts/tests/test_backend_role_preflight.py) cover wrong-account refusal, broad attachment detection, missing/incomplete reads and selected stack-role mistakes; run them without AWS:

```sh
python3 -m unittest scripts.tests.test_backend_role_preflight
```

The script does not tell whether an IAM request would be allowed after all policies, resource grants and session conditions are evaluated. Even with `--stack-name`, it does not enumerate everyone who may operate that stack. Before any backend mutation, use the [reader operating plan](../../docs/FIELD-LAB-READER-PLAYBOOK.md) to review the complete path, current account/credit terms and selected prices, a whole-run estimate, account-appropriate spending and reserve limits, exact cleanup and representative allowed/denied behavior. The role audit itself is read-only and uses no credits in this packet. Do not create an AWS Organization to complete these cases.

Ask Codex to challenge your first answer without showing the [assessor notes](ASSESSOR.md). Prompt: “Name one uninspected principal, role, resource or stack operation that could overturn my conclusion. Cite the AWS rule for that edge. Then change one fact and wait for my revised answer.” Keep your original response separate from the assisted revision. A fluent AI explanation is not an IAM simulator or a live account observation.

Primary references: [CDK bootstrap roles](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping-env.html), [CDK security boundary](https://docs.aws.amazon.com/cdk/v2/guide/best-practices-security.html), [CloudFormation service-role reuse](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-iam-servicerole.html), [passing a role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html).
