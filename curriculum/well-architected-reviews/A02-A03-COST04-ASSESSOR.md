# Assessor: COST 04 late-invoice case

Read the [learner case](A02-A03-COST04.md#changed-condition-exercise-a-late-invoice) only after writing the four-line receipt. This is authored reasoning against a fictional scenario, not a scored learner result or a live AWS observation.

| Receipt | Defensible statement | Evidence still needed |
| --- | --- | --- |
| Application work | The configured handler expiry should reject later actions through that handler; it does not prove every input or polling path stopped. | Actual invocation/event-source signals and rejected-post-expiry request under the selected deployment. |
| Exact managed inventory | A successful destroy is evidence that Terraform believes its managed objects were removed. It does not enumerate objects created manually or in another state. | Preserve the exact plan/state/resource IDs, inspect destroy output, then independently query those IDs and relevant service inventories in the selected Region. |
| Extra-resource ownership | The extra log group and similarly named queue are leads, not authorization to delete. | Match account, Region, ARN/ID, creator or state ownership, tags where present, consumers and retention obligations. A similar name is insufficient. |
| Billing period and measure | Zero **net** cost at 14:10 may reflect credits or delayed reporting. A later **pre-credit** increase may cover earlier usage. | Record usage dates, observation time, billing measure and inclusions; reconcile attributable meters after the billing data arrives. Do not equate account-wide changes with this run. |

For the changed seven-day retention request, accept a narrow approved copy or export only if its exact data, reader permissions, storage location, expiration action, owner and cost are named. Keeping the entire table and event-source mapping is not justified by one record. If any of these conditions are unresolved, mark the retained-data disposition pending. An S3 lifecycle rule or DynamoDB TTL may remove eligible data, but neither proves that every infrastructure object or billing meter ended.

Look for a learner who distinguishes **source configuration**, **provider observation** and **billing reconciliation**. A response that says “Terraform reported success, so all charges stopped” misses the extra-resource and delayed-bill controls. A response that deletes both named objects immediately misses ownership and shared-use risk. No pass rate is available because no independent learner has taken this exercise.
