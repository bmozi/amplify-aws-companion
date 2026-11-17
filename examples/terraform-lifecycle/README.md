# Inspect real Terraform changes without an AWS deployment

Prerequisites: Terraform 1.6–1.x and Python 3.9 or newer. Tested here with Terraform 1.16.4. From the repository root:

```sh
python3 examples/terraform-lifecycle/lab.py
```

The runner copies the accompanying `main.tf` into a temporary directory. It uses only Terraform's built-in `terraform_data` resource, no downloaded provider, AWS backend or provisioner. Inherited Terraform arguments and AWS environment variables are excluded from its subprocess environment. State, plans and the copied configuration are removed afterward, including on failure.

Before running, predict these outcomes:

| Step | Expected plan or observation |
| --- | --- |
| First plan and apply | Create one local lifecycle object |
| Repeat unchanged configuration | No-op |
| Change revision from 1 to 3 | Update; object ID stays the same |
| Apply the earlier saved revision-2 plan after revision 3 | Terraform rejects the stale plan |
| Change replacement generation | Delete and create; object ID changes |
| Rename the resource label without a mapping | Plan proposes delete old address and create new; never applied |
| Add the explicit address mapping | Plan has no lifecycle change; apply preserves ID and revision at the new address |
| Plan and apply destroy | Empty resource state |

`input` holds the revision value; `triggers_replace` intentionally makes generation changes replace this resource. These are properties of this teaching resource, not a claim that changing an AWS attribute always has the same lifecycle effect.

The runner reads structured plan/state JSON and checks behavior, rather than treating a successful exit as sufficient. Its output reports only synthetic results. It never operates in `infra/hosting` or on the account's existing Terraform state.

For a manual variation, copy `main.tf` into a new disposable folder outside the repository and run init, plan and apply there. Inspect a saved plan before applying it. Change `revision`, then `generation`, and explain why their effects differ. Destroy the local object and inspect state before deleting the folder. Do not copy cloud configuration or add provisioners to this exercise.

Ask Codex to explain the observed action list and identify what cannot be learned from it. A stale-plan check is not proof of remote locking, and a local no-op is not proof that AWS application behavior is correct. Read [the infrastructure ownership unit](../../reader/BOOK-LOCATORS.md#book-485621100165252b) and complete E16.

For a worked AI-review challenge, try [checking an overconfident no-op explanation](AI-REVIEW.md) before opening its separate answer guide. The case asks what a plan can establish, what must be checked independently, and how to discuss it without sharing private state.

## A source refactor can change infrastructure

The added pass changes `terraform_data.lesson` to `terraform_data.renamed` only in the temporary configuration. Predict the first plan before reading its action map. The runner checks both addresses and refuses to apply that destructive control. It then adds a `moved` block, inspects the previous-address field and no-op lifecycle action, applies the mapped change and checks the actual state address and unchanged ID/revision. Cleanup destroys the renamed local object.

Explain why preserving an ID is useful evidence here but not a database-data restore test. For a changed case, imagine two environments upgrading at different times: which migration record must remain available to the older environment? Ask Codex to compare the proposed plan with your intent, then verify its answer against the actual plan. The lifecycle pass does not test a remote backend or cloud ownership transfer. The separate local state-record pass below now runs as part of the same command.


## Recover the equipment list, not the equipment

Imagine a shop with an equipment list. Finding yesterday's list does not repair a broken freezer or restore the food inside it. Terraform state is a management record; restoring it is similarly different from recovering the service and its data.

The runner also executes [state_recovery.py](state_recovery.py). Run that file directly to repeat only this pass. It makes four disposable local folders and uses the same built-in resource. It never reads the lab's AWS state or configures a remote backend.

| Prediction to make before running | What the drill checks |
| --- | --- |
| Can an older snapshot overwrite a newer record? | The older serial is rejected and the destination is unchanged |
| Can one environment's snapshot overwrite another history? | Different lineage is rejected and the destination is unchanged |
| What does identical configuration propose with no state? | Create; this plan is inspected and never applied |
| What follows restoring the matching snapshot into an empty folder? | The recorded IDs and outputs match; revision-3 configuration plans no change |
| Can an unrelated snapshot appear healthy in another empty folder? | Yes: it is accepted and its matching configuration plans no change; a separate lineage comparison exposes the wrong history |

**Lineage** identifies a state history. **Serial** orders snapshots within that history. Neither tells you whether customer records are intact. The drill uses `state pull` to obtain snapshots and `state push` to exercise the safeguards. It never uses `-force`. HashiCorp documents these checks and warns that forcing a push overrides them. [State push reference](https://developer.hashicorp.com/terraform/cli/commands/state/push).

Restoring into an empty destination is deliberately revealing: there is no existing history there to establish that you chose the right environment. The negative control actually accepts the unrelated snapshot into a fourth empty folder and obtains a no-op with its matching configuration. Comparing its lineage with the intended history exposes the mismatch. A successful push and no-op are therefore not proof of correct recovery. In real operations, establish the backend, workspace, account, configuration and actual resource inventory before deciding how to recover. Do not copy this disposable-folder procedure directly into a cloud incident.

The resource here has no external service behind it. Matching its ID and output proves that this synthetic record survived; it cannot prove recovery of a database, a live website, an S3 state version, remote locking or safe concurrent operation. All temporary snapshots and plans are removed, including on failure.

**Changed case:** yesterday's state remembers a database that someone deleted today. Does accepting that snapshot recreate the missing database or its rows? Explain your answer before asking Codex. Then ask it to identify which observations require AWS inventory, which require Terraform planning and which require a separate data-restore test. Use sanitized descriptions rather than uploading real state.

**Assessment:** the expected answer is no. A state write changes the management record. It does not itself restore an external object or its business data. An eventual provider refresh and plan may reveal differences; inspect those differences before deciding on an operation. A recovered record, reconciled infrastructure and verified customer data are separate evidence requirements.
