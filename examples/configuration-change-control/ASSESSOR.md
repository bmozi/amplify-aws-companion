# Assessor notes: change configuration without fighting its owner

This is one defensible response to the local fixture, not an AWS simulation or official answer key.

| Case | Local decision | Reason |
| --- | --- | --- |
| Fresh event, matching approved revision, no deployment conflict, scoped target | `UPDATE_TEMPLATE_AND_REFRESH` for an Auto Scaling group | Change the versioned launch template and roll instances in stages so replacement instances inherit the intended configuration. |
| Old evaluation | `STOP_STALE` | Gather a current read-only observation before acting. AWS Config auto-remediation can use its last evaluation snapshot and may act on a resource that has since become compliant. |
| Wrong account, Region or resource | `STOP_SCOPE` | An event name does not authorize a fleet-wide action. |
| An allowed resource ID is presented as the wrong specific kind | `STOP_TARGET_KIND` | A bucket name cannot supply the evidence that a managed node exists; match the proposed route to the inventory. |
| Observed, reviewed and current source revisions disagree | `STOP_REVISION` | A newer desired change or old event requires a fresh plan and evidence. |
| A revision is absent, an age/count bound is malformed, negative, or a required maximum is zero | `STOP_EVIDENCE` | Equality of missing values is not proof that a reviewed revision exists. Rebuild a complete, valid evidence packet. |
| Deployment is already changing the resource | `STOP_DEPLOYMENT` | Avoid two controllers writing competing state. Resume only after the current deployment owner and state are known. |
| Direct Systems Manager action targets an unregistered/offline managed node | `STOP_SSM_READINESS` | Verify the supported node, SSM Agent, instance role or approved management configuration, and network path before execution. |
| Human approval is required but absent | `WAIT_APPROVAL` | An approval must identify the exact reviewed revision, resource scope and action; the fixture is not a real approval. |
| Requested fleet concurrency exceeds the chosen bound | `WAIT_CONCURRENCY` | Queue or stage a smaller target set. Do not turn one event into an uncontrolled fleet wave. |
| Retry/error allowance is exhausted | `STOP_RETRIES` or `STOP_ERROR_BUDGET` | Gather failure evidence and change the runbook or recovery decision deliberately. |
| Same event ID and target/revision were planned earlier | `INSPECT_PRIOR_PLAN` | A plan is not a run or a repaired setting. Find approval, execution and independent verification evidence before suppressing or retrying work. |
| Event ID is reused for another allowed target or desired revision | `STOP_ID_REUSE` | Do not let a familiar ID silently refer to a different operation. Resolve the identity conflict and take a fresh observation. |

## Service responsibilities

- **AWS Config** evaluates recorded resource configuration against a rule. Its result is evidence with a scope and timestamp; it is not a live application health check or permission grant.
- **Systems Manager Automation** runs a versioned, parameterized runbook for a bounded operation. Check the caller's permissions separately from the Automation service role and the runbook's actions. Set target concurrency and an error threshold. A runbook's name does not prove its actions are safe.
- **Systems Manager State Manager** maintains a declared configuration on supported managed nodes using scheduled associations. It is a fit for ongoing host state, not a substitute for a code deployment pipeline or review of resource-level infrastructure source.
- **EC2 Auto Scaling** maintains a fleet's capacity and replaces instances from the group's launch configuration/template. For a fleet baseline change, change the owning launch template or infrastructure definition and use a staged instance refresh; a one-instance patch can disappear at replacement.
- **Terraform or another IaC owner** stores desired resource configuration in its reviewed source. Plan and apply that source through its approved path so a later run does not reintroduce drift.

These mechanisms can coexist, but only one should own a particular setting. If two controllers disagree, they can continually undo each other's work. Good evidence records the event, fresh observed state, desired-state owner and revision, exact target, effective role, approval, execution result, independent verification, rollback condition and cost.

The local map is deliberately process memory. It cannot prove a command ran, survive restart, coordinate two workers or establish a customer result. A repeated event triggers reconciliation, not an automatic success verdict. The fixture also rechecks current scope and safety gates before consulting its prior-plan map, so an old matching ID cannot hide a new wrong-account or stale-observation condition.

## What this lab does not prove

It does not verify AWS Config recording or rule scope, evaluation timing, remediation role permissions, SSM Agent health, State Manager behavior, Automation pricing, Auto Scaling activity, Terraform state, IAM policy evaluation, service quotas, rollback, customer outcomes, learner comprehension or certification readiness. The values in the fixture are not service limits. No AWS resource, account, credit or bill was inspected or changed.
