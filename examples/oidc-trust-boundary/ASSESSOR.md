# Assessor: two badges still depend on their claims and grants

Read this after predicting the [cases](cases.json). A local `true` means only that fictional claims match one proposed Terraform trust shape; it is not a live-role result. The publisher source checks four conditions including the called path; the probe checks three. The separate source policy limits the proposed probe role to three read actions, but effective AWS permissions remain unverified.

| Case | Publisher / probe trust | Reason |
| --- | --- | --- |
| `publisher_manual_yes` | Match / no match | Correct `aud`, immutable repository/`main` `sub`, publisher name and called reusable path. The manual input is outside role trust. |
| `separate_probe_flag_off` | No match / match | The proposed probe role recognizes its own name; the publication flag is outside both trusts. GitHub's separate probe flag would still skip the checked-in job when unset. |
| `new_workflow_flag_off` | No match / no match | Its different workflow name fails both proposed conditions. Actual token issuance is separate. |
| `copied_workflow_name_other_file` | No match / no match | A direct job can copy `workflow` but lacks the required `job_workflow_ref`. It would match the earlier name-only source candidate. |
| `copied_probe_name_other_file` | No match / match | Copying the probe name can match probe trust, but the proposed probe policy still omits publishing actions. |
| `different_caller_same_reusable` | Match / no match | The called path matches even though the invoking file differs. Its false flag should stop the called job; IAM trust does not inspect that flag. |
| `same_workflow_other_branch` | No match / no match | The subject names `feature`, not `main`. |
| `same_subject_wrong_audience` | No match / no match | Both trusts expect `sts.amazonaws.com`. |
| `reused_names_different_ids` | No match / no match | Immutable owner and repository IDs differ even though the names look familiar. |
| `environment_subject` | No match / no match | The subject uses an environment context instead of the exact branch context. |

Narrower AWS grants reduce what a successfully assumed session can do. The proposed separate probe role keeps publication actions out of its source policy. The proposed publisher requires the reviewed reusable job path as well as the caller name, audience and subject. These are source candidates until AWS and GitHub readback prove installation. The called path rejects a direct copied-name job, but does not block another trusted-branch caller from invoking the same file. The reusable job must repeat artifact, source, budget and publication checks. Writer-controlled code is still mutable. None of these choices alone validates whole-run cost, an Amplify API result or a customer-visible deployment.

Mark an answer incomplete if it treats the flag as an IAM condition, equates a workflow name with a file path, presents the candidate condition as already installed, or says the local model is an AWS simulator. A strong answer states what to read back before changing IAM/GitHub settings and names a safe negative test after any live trust update.

## Reader-packet transfer

GitHub discovers Actions workflow files under `.github/workflows/` in the repository being run. The reduced packet keeps the three YAML files under `examples/github-workflows/` for reading, so their presence there does not create runnable Actions. The text shows a gate that could be used by a deliberately installed publisher workflow; it is not evidence that this reader repository has an enabled publisher, or that the private owner's variable is false today. The private checkout's active workflow is a separate source fact. The installed role's trust and effective permissions need dated account readback, followed by safe allowed and denied requests for the selected role and resource.

Copying the file into another repository can make a workflow runnable there, but the proposed trust also expects the exact audience, immutable owner/repository IDs, branch subject, workflow name and called reusable path for the publisher role. A job still needs token permission and a matching installed role; publishing further needs effective `CreateDeployment`/`StartDeployment` permission on the intended app branch, a reviewed artifact and an allowed run gate. The copy alone proves none of those things. The publication flag is a gate on one workflow's new jobs; it does not revoke another workflow's access or an existing AWS session.
