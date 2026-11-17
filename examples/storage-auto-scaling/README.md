# When should storage growth be automatic?

This is a design exercise only. It creates no resources or alarms and does not read cloud metrics. For each case, state which quantity is growing, how quickly, how much safe runway remains, who can respond, and what the change might cost.

## Case A: A disk that can fill before the next review

An EC2 workload has 50 GiB of safe free space and has recently written 100 GiB per day. The operator reviews capacity once each week. Writes may not pause without customer impact. The volume is EBS-backed; the OS filesystem and partition are tracked separately from the EBS volume size.

Should growth remain a manual task, trigger a warning, or trigger a tested automatic action? Give the runway calculation. If you recommend automation, name its maximum volume size, quota check, retry behavior, operator alert, expected bill review and end-to-end acceptance check. Explain what can still fail after an EBS resize request succeeds.

## Case B: Data grows on its own

A shared file workload grows unpredictably as customers upload documents. It uses EFS. The team wants to create a weekly job that preallocates another fixed amount of storage before uploads.

Which storage-capacity problem does EFS already handle? Which separate cost, access pattern, throughput, permission, backup and recovery questions still belong to the team? Decide whether a capacity-resize job adds useful protection or merely duplicates managed behavior.

## Case C: The bucket has no size setting

A customer archive uses S3, and the team says, “Because S3 scales, this archive has no scaling problem.” List which concerns that statement does not settle: data growth cost, retention, request rate, object count, application throughput, account quotas or spending controls. Choose evidence for each relevant concern.

## Change one assumption

In Case A, free space rises to 600 GiB and growth becomes a steady 10 GiB per week. The operator can safely extend the volume every month during a maintenance window. Explain why an automated increase may no longer be needed, and state which new evidence would reverse your decision.
