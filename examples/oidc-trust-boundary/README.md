# Give the publisher and the reader different badges

**Next advanced lesson:** [which workflow path issued the publisher badge?](WORKFLOW-PATH-UPGRADE.md) explains the new reusable-workflow source candidate, seven changed cases and a separate assessor. It is cloud-free design practice; the installed AWS trust has not been changed by that lesson.

Maya tells the shop, “Only the delivery team may publish the new website.” The old probe borrowed the delivery badge just to read the notice board. Its choice to look only at the board did not remove the badge's ability to open the delivery door. The source candidate gives the probe a separate reader badge: both badges check the company, repository and branch, while each checks its own workflow name and opens different AWS actions.

The installed GitHub publisher role was last read back with `aud=sts.amazonaws.com` and one immutable repository-and-`main` `sub`. That live readback predates these Terraform changes. The source candidate checks the publisher `workflow` **name** and called `job_workflow_ref` path, while a separate probe role checks its own name. The probe source policy contains `amplify:GetJob`, `freetier:GetAccountPlanState` and `budgets:ViewBudget`; it has no Amplify publication action. A missing or false `AMPLIFY_PROBE_ENABLED` variable skips the checked-in probe job before OIDC. The [historical probe](../../reader/GITHUB-PUBLISHER-EVIDENCE-CASE.md) assumed the older publisher role and made two read-only account calls; it did not publish. No new role or trust change has been applied or observed in AWS.

## Predict, then run

Open [fictional cases](cases.json). Before running the script, predict which **proposed role trust**, if any, each already issued fictional token matches. Then ask which policy would permit publication. Pay special attention to the separate probe, a direct copied publisher name, a different caller of the same reusable file and the wrong-branch case. A case's `publish_flag` is outside both role trusts.

```sh
python3 examples/oidc-trust-boundary/lab.py
python3 -m unittest discover -s examples/oidc-trust-boundary -p 'test_*.py' -v
```

The script checks the two Terraform trust documents, the probe's three read actions, both workflow names and the publisher's called path. In the private source it checks the three active workflows; in the reduced reader packet it checks three inert copies under `examples/github-workflows/`, where GitHub will not register them as Actions. A partial or mismatched set stops the exercise. It uses invented owner/repository IDs `101` and `202`. It makes **no** GitHub or AWS request, signs no token and has no credentials. `publisher_trust_match` and `probe_trust_match` are fictional claim comparisons, not AWS decisions. Even a probe match does not prove the new role exists, that STS would issue credentials, that no extra policy was attached, or that a visitor would see a deployed page.

| Question | Enforcing place | What this exercise shows |
| --- | --- | --- |
| May this job request an OIDC token? | GitHub job permissions and controls | The fictional case presumes a token; this is not tested. |
| Does AWS trust this token's audience, subject, name and called path? | Each role's trust policy | The local proposed-condition comparisons. The real probe observed assumption only under the earlier live trust. |
| What may the temporary role do? | Effective AWS permissions, including every attached policy and higher-level controls | The source check finds three read actions on the proposed probe role; actual role readback and safe allowed/denied tests remain necessary. |
| Did the correct site serve the change? | Amplify job and customer-facing observation | Still untested for GitHub publication. |

### A copy of a workflow is not a running workflow

Maya gives a new teammate this reduced reader packet. It contains caller, reusable publisher and probe YAML examples under `examples/github-workflows/`, but no files in `.github/workflows/`. The teammate reads the publisher example and says, “The `AMPLIFY_PUBLISH_ENABLED` check is false, so this GitHub repository has a safe off switch.” What would you correct?

First identify which files GitHub would register as workflows **in the repository that actually hosts them**. Then distinguish these three claims: the example describes a proposed gate; a private source checkout contains an active workflow file; the account has an installed IAM role with a particular trust and permission set. Which evidence would establish each claim? If someone copied either example into `.github/workflows/` of a different repository, what would still be needed before it could assume the intended AWS role or publish this Amplify app? Write your answer before reading the [assessor](ASSESSOR.md).

The local script checks the example files as *teaching inputs*. Running it cannot register a GitHub Action, enable a repository variable, install a role or disable an existing role session. The safe reader-packet boundary depends on the file path as well as the YAML text. [GitHub's workflow-file rule](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) explains why the directory matters.

## Change the rule on paper

Consider three candidate responses. Write down the improvement and what remains possible for each before reading the [assessor](ASSESSOR.md).

1. Keep the previously installed branch-level subject and make the role's AWS grants narrower. What could another workflow on `main` still do? What source-writing authority would you protect?
2. Use the proposed separate publishing and probe identities. Why does the probe's role policy still matter after the name checks? What must be verified before enabling the new GitHub probe gate?
3. Compare the proposed publisher's name **and called-path** conditions with the earlier name-only design. Which one distinguishes a copied name in a direct job? Why can another same-branch caller still invoke the reviewed reusable file? Name the gates inside that file and the token/IAM evidence required before an installed-role change. Do not copy a fictional subject into the live role.

GitHub documents the `workflow` name and `job_workflow_ref` called path as different claims in its [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc). AWS lists both as supported [GitHub trust condition keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_iam-condition-keys.html#condition-keys-wif). A copied name in a direct job fails the proposed publisher path check; another caller on the trusted branch can still use the reusable job. Exact token, IAM and caller review remain open.

**Cost and cleanup:** This lab uses only local Python. A future live migration needs an exact plan, intended-role and cross-role denied-assumption probes, read/write permission checks, and a GitHub Actions usage check. Keep `AMPLIFY_PROBE_ENABLED` unset and `AMPLIFY_PUBLISH_ENABLED=false` until the corresponding independent gates pass. A separate account-specific whole-run cost limit and verified credit reserve are needed before any Amplify publication. No organization account is required for this local exercise.

**Use Codex:** Give it the invented cases, Terraform trust block and the four-question table. Ask it to identify the first enforcing boundary for each result and a counterexample to “flag off means AWS access revoked.” Verify its answer against the source and official references. Never paste a real OIDC token or cloud credential into the prompt.
