# Assessor notes — cost-effective database service selection

In Brief A, DynamoDB is a plausible initial candidate because access is bounded by device ID, traffic is bursty and relational joins are absent. On-demand mode is reasonable to price first because idle request capacity is not provisioned; a provisioned design is worth comparing only with a reliable workload forecast and an explicit scaling strategy. It still needs key-distribution and item/index-size evidence. The stated completion promise demands transactional/idempotent handling and a recoverable audit path. A scan-heavy design or concentrated hot key may change the candidate or data model.

In Brief B, relational services deserve initial comparison because flexible relationships, invoice rules and ad hoc reporting matter. DynamoDB is not categorically incapable of transactions, but the author must show specific access patterns, transaction boundaries, index maintenance, retries and reporting design. If its modeling complexity and duplicated data add ongoing costs, count them. If a relational engine cannot meet a proven scale or availability requirement at reasonable cost, revisit service selection with measurements.

Both candidates must be compared under equal query, data, retention, availability and recovery assumptions. DynamoDB on-demand cost follows read/write requests, while provisioned capacity is charged based on configured capacity; storage, indexes, backups and other features still contribute. RDS costs can include instance runtime, storage, IOPS, backup storage and data transfer. Add application compute, connections, operations and engineering effort. Use current regional pricing inputs; the numerical practice below uses fictional rates only.

Reject a service-name answer without workload fit and a reversal condition. A cost difference that comes from weaker consistency, shorter retention, no replica or slower restore is not an apples-to-apples saving unless the owner approves that trade. No calculator estimate, AWS deployment, performance measurement, bill or learner outcome is part of this worksheet.

## Fictional numerical comparison

At one million operations, metered costs $80 + (1,000,000 operations × $0.00002 per operation) = **$100**. Reserved costs **$240**, so the stipulated metered option is $140 cheaper. At ten million, metered costs **$280**, making reserved $40 cheaper within the stated eligibility and tested-range assumptions.

Solve $80 + $0.00002 × N = $240: the original intersection is **8 million operations**. Adding $40 to metered fixed cost gives $120 + $0.00002 × N = $240, moving the intersection to **6 million**. More supporting cost makes metered lose its price advantage sooner; it does not raise the other candidate's bill.

The ten-million arithmetic remains $280 versus $240 under the stipulated tariff, but the burst invalidates the supplied performance basis. Neither candidate has established the new response-time requirement. Require a representative arrival profile, per-key distribution and workload test before selecting on price; do not demand one particular AWS service.

A 40-minute recovery fails the 20-minute requirement. The candidate with the stipulated 15-minute whole-path recovery is the supported choice if it also satisfies the other unchanged requirements. A proposed repair to the cheaper option needs measured recovery and a revised whole-path cost, not a promise that adding capacity will fix it.

Fifteen million exceeds the stated 12-million range. The reserved price beyond that range and both candidates' capacity evidence are missing. Accept “not enough evidence” with named missing inputs; do not reward extrapolated certainty. These answers assess arithmetic and conditional reasoning, not a real service benchmark, live price, participant result or certification score.

## Dated request-unit transfer

Two million eventually consistent reads of stipulated 4,097-byte items consume two million read request units and cost $0.25 at the recorded rate. A projection does not itself shrink the stored item used for read-unit accounting. Accept relevant missing categories such as storage, indexes, backup, transfer or application compute, while requiring the reader to explain which apply. Do not award a complete-estimate or live-billing claim from this subtotal.
