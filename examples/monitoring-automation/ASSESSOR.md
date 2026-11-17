# Assessor notes: match the automation to the signal

These notes explain one defensible reading of the packet. They are not an official AWS answer key or certification exam content. Product behavior must be rechecked against current AWS documentation before implementation.

## Expected local results

| Case | Expected decision | Why |
| --- | --- | --- |
| First incoming log object version | `PROCESS` | Exact bucket, prefix and suffix match the configured fixture |
| Same object version again | `DUPLICATE` | Delivery repetition must not repeat the intended business effect |
| Derived file under `processed/` | `FILTERED_OUTPUT` | The output is outside the intake prefix, preventing a self-triggering loop |
| EC2 state-change event for `terminated` | `ROUTE` | The three selected EventBridge fields match exactly |
| EC2 state-change event for `running` | `NO_MATCH` | It does not match the requested state transition |
| `OK` to `ALARM` | `NOTIFY` | The configured action is associated with a state transition |
| `ALARM` observed again | `NO_TRANSITION` | Repeated state is not a second transition in this local model |
| Allowlisted resource with recent noncompliant result and known action | `REMEDIATE` | The local safety gates all pass |
| Same resource with stale result | `STOP_STALE` | Refresh the evidence before acting on a potentially outdated evaluation |
| Resource outside the explicit allowlist | `STOP_SCOPE` | A broadly matching rule is not sufficient authorization to modify a resource |
| Unknown action or exhausted attempt cap | `STOP_ACTION` or `STOP_RETRIES` | The repair must be understood and bounded |

## Architecture reasoning

S3 notifications and EventBridge events are asynchronous messages. A delivery acknowledgment does not prove that downstream processing completed. Design for duplicates, delayed delivery, failures, retry limits, dead-letter handling and an operator-owned replay path. For S3 specifically, output written into the triggering scope can cause a loop. Use narrow event filters, durable idempotency and separate output scope.

CloudWatch alarms evaluate measurements and state. An alarm action is a separate destination and permission path. For an SNS notice, verify topic access and delivery. For Lambda, verify CloudWatch's invoke permission, the Lambda execution role's downstream permissions, duplicate-safe behavior and the function result. Do not treat `ALARM` as proof that the action succeeded.

Scaling controllers change specific capacity dimensions. EC2 Auto Scaling changes instance count; ECS service autoscaling changes desired task count; an EC2-backed ECS capacity provider can separately change cluster instances; DynamoDB adjusts provisioned throughput; RDS storage autoscaling changes storage; EKS workload replicas and worker nodes are separate layers. Select a metric tied to work per capacity unit, define bounds and timing, check quotas and dependencies, and estimate the largest allowed configuration.

AWS Config automatic remediation uses Systems Manager Automation documents. It is suitable only when the rule, target resource, role, document, parameters and correction are understood. Config evaluation can be based on a stored compliance snapshot, so a safety-sensitive action should obtain sufficiently current evidence before acting. Limit retries, inspect execution results and preserve a recovery path. A scoped exercise should not silently grow into organization-wide remediation.

SSM Agent supports Systems Manager management of a node. CloudWatch Agent gathers selected host/application metrics and logs. A management agent being present does not demonstrate that the intended telemetry is configured, authorized or arriving.

ALB target health and Route 53 endpoint/DNS health answer routing questions. They are not end-to-end business completion checks. ALB's documented fail-open behavior when every registered target is unhealthy is a useful exam and design edge case. DNS caching and resolver behavior also mean an unhealthy record is not an instantaneous global traffic switch.

## What the lab does not prove

It does not validate AWS IAM policy semantics, pattern syntax in full, S3 event order, duplicate frequency, service retries, a DLQ, notification delivery, agent installation, Config snapshots, SSM Automation execution, actual autoscaling, ALB behavior, Route 53 propagation, current pricing, credit availability, learner mastery or certification readiness. Those need separate, authorized evidence. No live AWS resources were used by this lab.

## Crash window

The four local outcomes are respectively two, zero, one and two provider records, with a worker receipt in every case. The first worker crashes after the effect; the retry repeats it. The second records completion but crashes before the effect, so the retry skips work. The third relies on the toy provider's unique key, which the retry reuses. A new key defeats that protection. These outcomes do not prove the behavior of a real provider: check its key scope, retention, concurrent requests, mismatched payloads and retrieval/reconciliation contract. A timeout is an unknown result until the provider's documented status or reconciliation process resolves it; changing the key just to get a fresh answer can duplicate the effect.

The `changed_amount` retry is a separate fifth case: the toy provider retains one original payment, returns `conflict`, and the worker writes no completion receipt for the changed request. It is an unresolved decision, not proof that the changed payment occurred. The toy comparison is a design choice; check the actual provider contract.

For the four fictional lookup results, a confirmed matching operation supports a receipt; authoritative absence supports a same-key retry only while the toy key protection is known to be active; an unavailable lookup and a different amount both require investigation. When protection is expired or unknown, the model holds even an absent result. A confirmed matching result can still support recording a receipt because this action does not send another payment. Authoritative absence is an explicit assumption in the exercise, not a property of every empty search result. Check whether the real provider's lookup is complete and current, its idempotency-key scope and lifetime, and the process for resolving uncertain or conflicting records. A key past its retention window may no longer prevent a duplicate.
