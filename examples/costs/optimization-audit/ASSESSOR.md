# Assessor notes: optimization audit

The figures come only from the local synthetic CSVs and `lab.py`; they are not AWS prices, a bill, account-credit balance or recommendations from a real AWS service. Other answers can be sound when they preserve the same scope, business promise and uncertainty.

## Reconciliation and evidence

The script reports baseline pre-credit $101.00 and current pre-credit $117.00. Repair-tagged usage is $78.00 in both periods; shared usage is $12.00 in both; unallocated rows rise from $11.00 to $27.00. The current account credit is −$15.00 and current after-credit account cost is $102.00. Internet-out volume rises from 20 GB to 180 GB, and its fictional cost rises from $2.00 to $18.00. The current pre-credit total is above a fictional $110 threshold while the after-credit total is below it. A stable tagged subtotal therefore does **not** prove stable account usage. The account credit is not a repair-tag allocation or a resource-efficiency improvement.

`old-volume` is only a waste **candidate**. Its unattached state needs an owner, retention, recoverability, attachment-history and exact-resource check before deletion. `snapshot` has an explicit retained purpose and review date; keep it until that decision. A worker with a low 14-day CPU average cannot be safely downsized from this evidence because a day-28 close reached 92% and barely met its deadline. Compare a representative close and recovery rerun on a candidate size with output correctness, finish time and rollback. Database p99 latency above its promise is a performance investigation, not proof that “more CPU” is the remedy; inspect query, locks, storage, connection and load evidence. A cost review can find waste and capacity risk at the same time.

The proposed $110/month pre-credit threshold is an **investigation trigger** grounded in the fictional $101 baseline, not a claim that AWS will stop at $110. A complete budget design names the account versus project scope, cost measure and inclusion of credits/refunds/taxes, monthly period, actual or forecast notification, recipient, delivery/permission check, and a prewritten stop/inventory procedure. A run-level estimate and credit reserve are separate operating gates chosen for the actual account. AWS Budgets billing data and delivery can lag resource use; a forecast is a prediction, not a cap. If the chosen budget uses after-credit net cost, its threshold will answer a different question and can mask the pre-credit network increase.

For real CUR 2.0, identify the selected billing period and actual usage-time range, cost/usage line-item types and measure, and whether resource IDs were included. Enabled cost-allocation tags appear in a map; a missing tag does not prove the row belongs to another project. Resource-level exports can be larger. A query filtered to `repair` or just one service needs a same-period, same-measure reconciliation with shared, untagged and adjustment rows before claiming an account total. Treat the export bucket, retention, readers and Athena/query spend as a cost and security decision. The CSV here intentionally avoids claiming to be a deployable CUR parser.

The network delta is arithmetic, not a root cause. Possible explanations include a valid surge in customer delivery, a changed route crossing Regions/AZs, an unexpected copy, or meter/classification changes. Compare application/CDN transfer logs, source/destination inventory, usage type, direction and time, and business volumes. Do not infer a breach or a specific rate from the toy service label.

## Changed-fact reasoning

- A resize that causes a missed close must be reversed or adjusted under a named rollback plan, with correct and timely reports checked. The low CPU average does not trump the business result.
- A sole decryptable restore point makes volume deletion unsafe until an approved replacement restore path is tested and retention decisions are made.
- A mid-month tag activation needs coverage/backfill verification; earlier rows cannot simply be relabeled by wishful reporting.
- A larger credit changes net payment, not the same pre-credit resource use. Keep both measures visible.
- A cross-Region/office transfer requires its actual route and direction plus service requests, transfer, endpoints/processing and fixed-hour components if present. Do not add every possible meter automatically; price only chosen components using current regional terms.

Score each dimension 0–2: full-scope reconciliation; resource-state and performance judgment; alert design and delay; granular-report/tag handling; network investigation and changed-case revision. Ten points are possible. A small net bill alone cannot earn full reconciliation or alert credit. No score here represents an actual learner result.
