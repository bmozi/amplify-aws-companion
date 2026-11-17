# Automate the steps; gate the decision

This local lab models a recovery cutover gate for Maya's fictional booking service. It uses Python's standard library only. It makes no AWS calls, provisions no resources, models no AWS service behavior, and produces no RTO, RPO, or price measurement.

Run it from the repository root:

```bash
python3 examples/recovery-automation/lab.py
python3 -m unittest discover -s examples/recovery-automation -p 'test_*.py'
```

The gate accepts a cutover only after the incident trigger is confirmed, observations are fresh, a recovery point is chosen, keys and dependencies work, business records are reconciled, the old writer is fenced, and survivor capacity is proved. A policy may allow that fully validated sequence to proceed automatically or require a named human approval. Missing evidence always returns `NO_GO`; approval cannot repair a failed prerequisite.

## Try the reasoning before the code

For each case printed by the lab, identify the first failed gate and explain what evidence would change the decision. Then edit one case at a time and run the tests.

1. The secondary application returns HTTP 200, but the record-reconciliation receipt is missing.
2. The backup restores and decrypts, but a worker can still write to the old database.
3. All data and capacity checks pass, but the recovery operator normally signs in through the unavailable Region.
4. The primary Region reports a health alarm, but the independent customer observer is stale.
5. All checks pass, and the written recovery policy requires approval before routing changes.
6. The backup restoration is correct, but the surviving environment can handle only half of declared demand. Name a valid degraded-service policy or keep the cutover blocked.

The model makes assumptions visible but does not establish that the checks are sufficient for a real workload. Adapt the evidence list to the actual application and business promise. Do not make a boolean `true` stand in for a tested AWS mechanism. Compare your reasoning with the separate [assessor notes](ASSESSOR.md) only after attempting the cases.

## AWS design translation

An AWS implementation could combine an AWS Backup plan and a cross-Region copy with a separately tested restore; Systems Manager Automation can orchestrate selected operational steps; EventBridge or an operations process can start a workflow; and Route 53, CloudFront, or another application-specific control can change customer routing. The exact supported resource, Region, encryption key, permissions, recovery destination and routing method must be verified. A runbook can automate steps without proving that its input data is correct or that the business is ready to reopen.

AWS Backup cross-Region copying has resource-specific support and constraints. Restore testing can invoke a validation workflow, but that workflow must check the business acceptance conditions. Systems Manager Automation runbooks require a service role with the permissions needed by the actions. Review [AWS Backup cross-Region copy guidance](https://docs.aws.amazon.com/aws-backup/latest/devguide/cross-region-backup.html), [AWS Backup restore testing validation](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing-validation.html), and [Systems Manager Automation runbook authoring](https://docs.aws.amazon.com/systems-manager/latest/userguide/automation-authoring-runbooks.html) before designing a real flow.

Before any live exercise, estimate the entire run against spending and reserve limits chosen for the account, use a scoped non-root identity, list resources and cleanup actions, and verify current account and service eligibility. This lab does not authorize live recovery, Region setup, or Organization-dependent work. Independent learner review and AWS integration evidence remain open.
