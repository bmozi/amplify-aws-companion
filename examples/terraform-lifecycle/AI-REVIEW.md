# Check an AI explanation of a Terraform plan

A mechanic's equipment list can say a spare pump is on the shelf. The list does not prove the pump is there or that it works. Terraform state is also a record. A normal plan compares configuration and state and, by default, refreshes existing objects through the provider; other planning options can change what is observed. The plan is useful evidence, but a reader still has to establish which account and environment it describes, how it was made and what the application actually does.

## Make your own call first

You have run the local [lifecycle exercise](README.md). In a separate, **fictional** cloud review, a saved plan reports no resource changes. The report excerpt does not show the AWS account, Region, backend, workspace, provider identity, plan creation time, planning options or a customer test. The team asks whether it is safe to announce that yesterday's deleted database and its customer records have been recovered.

A hypothetical AI reply says: “The plan is empty, so the original database and all customer records are restored. Apply it immediately.”

1. List what the supplied plan result actually shows and what it does not show. Does a no-op itself restore data? Do not invent a successful database read.
2. Name the account, Region, backend, workspace, identity, configuration revision and state lineage evidence you would compare before treating a plan as relevant. Name a separate service-inventory observation and a customer-data restore check.
3. Write a stop condition and a safer next action that does not change infrastructure. State when a fresh plan would be needed; a saved plan is a snapshot, not an open-ended permission to apply later.
4. Keep real state files, plan files, credentials and customer records private. Describe the problem with synthetic values or a minimal sanitized action summary. Sanitizing removes useful context too, so label unknowns rather than filling them in.

**Change the case:** The team supplies the command that created the plan: it used `-target` to focus on a networking resource unrelated to the database. What can that no-change result say about the database? Explain why you need to know the plan's scope as well as whether refresh was enabled. Check [Terraform's targeting guidance](https://developer.hashicorp.com/terraform/cli/commands/plan#resource-targeting) before treating a targeted plan as an overall infrastructure review.

After predicting the result, run `python3 examples/terraform-lifecycle/target_scope.py` from the repository root. It creates two disposable local `terraform_data` objects, changes the proposed database-shaped object's input, and inspects two plans without applying either one. The targeted network plan reports only a network no-op; the full plan also reports a database-shaped update. The state inspection still reports input `1` afterward: the proposed input `2` has not been applied. Both names are teaching labels: neither object is an AWS network or database. The temporary folder and local state are removed after the run.

Save your answer, then ask Codex: “Challenge my interpretation of this fictional no-op. List assumptions and observations still needed. Do not run commands or recommend an apply.” Check its claims against the observed local lab and [HashiCorp's plan documentation](https://developer.hashicorp.com/terraform/cli/commands/plan). Compare with the [answer guide](AI-REVIEW-ASSESSOR.md). This is a paper decision; it makes no AWS call and does not test a live provider, saved-plan contents or an actual restore.
