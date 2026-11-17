# Change the configuration at its source of truth

This local decision lab asks what should happen after an event reports configuration drift. It uses only fictional Python dictionaries and the standard library. It does not call AWS, emulate AWS Config or Systems Manager, create an Auto Scaling group, or modify a resource.

Run from the repository root:

```sh
python3 examples/configuration-change-control/lab.py
python3 -m unittest discover -s examples/configuration-change-control -p 'test_*.py' -v
```

Before running, predict the response to a fresh noncompliant event, a stale evaluation, an event from another account, missing or outdated revision evidence, invalid age/concurrency bounds, an active deployment, a managed node that is offline, a missing approval, a busy fleet, an exhausted retry budget and a repeated event.

The in-memory `planned_events` map records only that this process **selected a plan** for an event ID and exact target/revision. It is not an execution log. When the same event arrives again, the model returns `INSPECT_PRIOR_PLAN`: find whether the proposed change was approved, started, completed and independently verified before deciding what to do next. Reusing the ID for a different target or desired revision returns `STOP_ID_REUSE`. A repeated event still passes the current scope, freshness and deployment checks before either result. Restarting the script forgets this toy map; a real controller needs durable, trusted work identity and outcome reconciliation.

Safety evidence must be explicit: all six deployment, prior-attempt, approval and managed-node flags must be Boolean values. A missing value, a number, or text such as `"false"` returns `STOP_EVIDENCE` without recording a plan. In this teaching model, an unknown answer is not evidence that a deployment is inactive or approval is unnecessary. Even an explicit value is only a fictional input; a real process needs trustworthy, current evidence.

An allowed name alone also does not identify the kind of resource. The fixture's small inventory binds its group, node and bucket IDs to their fictional kinds. A group-specific or managed-node route naming the wrong kind returns `STOP_TARGET_KIND`; the generic Terraform review route can still cover an allowed resource. Real inventory and effective permissions must be checked independently.

The model asks the learner to make four decisions:

1. Is this event fresh, in the reviewed account/Region/resource scope, and still relevant to today's desired configuration?
2. Who owns the desired state: a reviewed Terraform change, an EC2 launch template/Auto Scaling refresh, or a Systems Manager association for a supported managed node?
3. Are prerequisites satisfied: managed-node reachability, approval when needed, bounded concurrency, error/retry limits and no conflicting deployment?
4. What independent read proves the new configuration and customer outcome, and who owns rollback if it fails?

This is a small policy fixture, not an AWS service emulator. Its revision, freshness and concurrency values are teaching inputs, not AWS Config fields or service limits. It does not implement Terraform plans, SSM runbooks, State Manager associations, EC2 Auto Scaling, event delivery, IAM, approval authentication, rollback, current AWS pricing or customer verification.

## Changed cases

- A security team changes the launch template while an old Config result is waiting in a queue. Which source revision may the operator use?
- The change is already in Terraform, but the event targets a live resource. Why is manually editing the resource not an acceptable substitute for reviewing and applying the source change?
- The target is an Auto Scaling group. Why should the fleet's launch template and staged instance refresh be considered instead of patching one disposable instance?
- A standalone node has no online SSM Agent. What must be restored or verified before a runbook can act?
- The proposed runbook is disruptive, an application deployment is in progress, or the error budget is exhausted. Which action waits or stops, and what evidence permits reconsideration?
- The first event selected a plan, but the operator never ran it. The same event ID arrives again. What evidence would distinguish a pending proposal from a completed repair? What if that ID now names another allowed resource?

Then read the separate [assessor notes](ASSESSOR.md), compare them with the [illustrated Unit 08 lesson](../../reader/BOOK-LOCATORS.md#book-12b2da15275ed913), and complete [E23](../../curriculum/EXERCISES.md#e23). No AWS cost is incurred by this local lab. Any future live exercise needs a scoped non-root identity, a current whole-run estimate, spending and reserve limits chosen for the account, explicit target inventory and verified cleanup, and fresh AWS source and price checks. Organization-wide remediation remains design-only unless separately authorized in a suitable environment.
