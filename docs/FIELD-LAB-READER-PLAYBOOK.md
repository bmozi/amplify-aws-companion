# Follow the Amplify field lab without borrowing its account

Maya has a small private notebook application. A visitor opens its page, signs in, saves a note, attaches a file and sees another window update. Those visible actions cross several boundaries: Hosting serves the page; Cognito identifies the visitor; AppSync and DynamoDB handle notes; S3 holds files; a Lambda answers a small text-inspection request. The [application lesson](../reader/BOOK-LOCATORS.md#book-e8d9fb108293da29) draws that path and explains who owns each part.

This playbook helps you repeat the **reasoning** in your own account. It does not grant permission to run this project's cloud commands in a different account. Use disposable data, identify every resource owner and decide how you will stop and remove the experiment before you create anything.

## Choose the evidence you need

| Question | First useful check | What remains unproved |
| --- | --- | --- |
| Does the source describe the intended resources? | Read [Terraform Hosting](../infra/hosting/) and [Amplify backend definitions](../app/amplify/) | That either is installed or behaves as drawn |
| Will the build make a usable page? | Install reviewed locked dependencies and run a local build | That the hosted page uses the intended backend |
| Can the publisher receive a temporary AWS role? | A deliberately scoped GitHub OIDC identity probe | That it can publish, or that other actions are denied |
| Can visitors use the application? | Observe a hosted sign-in, note, file and function journey | That a second user is kept out |
| Is private data really private? | Make direct API and file requests as two separate app users | That all users, data sizes and future changes are covered |
| Did it fit the budget? | Compare the estimate, service observations and later bill | That a budget alert capped spending |

A green source check is evidence about source. A real role assumption is evidence about that session. A working page is evidence about the tested visitor path. Keep those receipts separate.

## The GitHub badge and the publish switch

The project uses a manually gated publication candidate. The checked-in [publisher caller](../examples/github-workflows/amplify-publish.yml) and its `AMPLIFY_PUBLISH_ENABLED` variable decide whether *that workflow* may start a release. Its [reusable build-and-publish workflow](../examples/github-workflows/reusable-amplify-publish.yml) repeats the release gates and builds its own ZIP before the separate credential-bearing job. The [identity probe workflow](../examples/github-workflows/probe-amplify-publisher-identity.yml) is a different workflow: it asks GitHub for a temporary AWS badge and makes read-only account checks. A release switch set to `false` does not revoke the badge or disable other workflows.

In the project's **October 23, 2026** private run record, GitHub Actions run `40017365983` assumed the intended publisher role and completed the Free-plan and named-budget reads. It did not call Amplify to publish, test a real unrelated-target denial, or exercise a customer path. The publication workflow had no run at that check. This dated observation is a teaching example, not a claim about your account or current cloud state. The private operational receipt remains in `docs/PUBLISHER-OIDC-PROBE-RESULT-2026-10-23.md` in the owner checkout.

To stop **new releases by the selected workflow**, disable its trigger or keep its gate off and inspect jobs already running. To stop **all GitHub use of that AWS role**, review and change the AWS role's trust or remove the role after checking other dependents. To stop **the site and its charges**, inspect and remove the owned Hosting and backend resources separately. These are three different operations. The [publisher-role field lab](../reader/PUBLISHER-ROLE-FIELD-LAB.md) lets you test the source-side controls without publishing.

## Check the publishing address before using the badge

A delivery worker needs the right storefront address as well as a valid badge. Before a release, confirm the expected AWS account and Region, exact Amplify app and branch, GitHub identity provider, publisher role and named budget. The [read-only account preflight](../scripts/publisher-account-preflight.py) gathers those facts for this project when an authorized operator supplies their own account and app identifiers. It keeps detailed credit and IAM documents in a private local receipt. If an IAM or billing read is denied, the result is **unknown**; it does not mean the policy, credit or role is absent.

Then compare the current role trust and permissions with the intended workflow, the reviewed artifact and the selected target. The role may have attached policies or a permissions boundary, and other controls may affect the session. A matching inventory is an address check, not proof of a successful publish or a forbidden-action denial. Verify service prices, whole-run estimate, credit terms, reserve, cleanup plan and later billing separately. Ask Codex to list each item it can establish from a source file and each one that still needs an account or served-site observation. Keep account receipts and credentials out of a public companion package.

## Before any cloud run

1. Confirm the account, Region, selected AWS plan and credit terms using a scoped, non-root identity. A saved screenshot or a prior run's balance is historical evidence.
2. Estimate the **whole run**, including build, Hosting, requests, data, files, logs and cleanup. Include existing resource usage and a margin. A budget alert warns; it does not stop charges. If you share an account, coordinate other active experiments.
3. Name the exact deployment roles and the roles they can hand work to. A narrow caller can still invoke a powerful downstream deployment role.
4. Set a time and cost stop rule, a cleanup owner and an inventory of resources. Record an estimate within your own chosen limit and preserve your chosen reserve. This project's conservative planning figures are account-specific, not reader defaults.
5. Inspect the proposed plan or change, then deploy only with authority you have reviewed. Never treat a denial as a reason to switch to root.

The commands live beside the files that own each operation: [Hosting Terraform](../infra/hosting/), [backend helper](../scripts/deploy-backend.py), [frontend helper](../scripts/deploy-frontend.py), and [reader cost-and-credit lesson](../reader/COST-AND-CREDIT-FIELD-LESSON.md). Their flags and prerequisites can change; read the current source and its help text. A local build, a backend deployment and a frontend publication are distinct steps.

## Test the neighbor at every door

For a bounded privacy test, create two separate **app** users, Maya and Leo. These are not AWS console identities. Maya creates one disposable note and one uniquely named small file. Check that she can read them after a fresh sign-in. Then, as Leo, attempt direct note read, list visibility across all relevant pages, update and delete; attempt file list, download, overwrite and delete. Record API responses, not merely what the page hides. Remove only the test objects as Maya and confirm cleanup even if a denial test failed.

The optional [two-user checker](../app/check-live.mjs) performs this sequence against a deliberately authorized live lab. Its [fake tests](../app/live-journey.test.mjs) exercise checker logic without AWS. Fake-test success does not prove Cognito, AppSync or S3 enforced the rule. The live checker needs two disposable app users in a Git-ignored local file, a reviewed deployment, a current cost gate and a cleanup plan. Its page traversal is bounded; an incomplete traversal must be reported as **unverified**.

After any experiment, compare the actual resources with the inventory and inspect later billing. Removing Hosting alone may leave the backend; deleting a local configuration file removes no AWS resource. Keep the estimate, observed service responses, cleanup inventory and delayed bill as separate evidence.
