# Cost-effective database service worksheet

This paper exercise practices SAA-C03 task 4.3 skill 03: choose cost-effective database services for an eligible workload. It creates no AWS resources. Read [Unit 25](../../reader/BOOK-LOCATORS.md#book-f54a970f305e11c7), write the design and calculator assumptions, then review the [assessor notes](ASSESSOR.md).

## Two workload briefs

### A. Device status lookup

The application stores one current status per device and a bounded list of recent status changes. Requests are keyed by device ID; there are no cross-device joins. Traffic is near zero overnight, rises sharply during two daily maintenance windows and has predictable but brief bursts. Reads can use eventual consistency unless a specific operation proves otherwise. The business requires a bounded response time and cannot lose confirmed maintenance completion.

Compare DynamoDB on-demand, DynamoDB provisioned with an evidence-based capacity estimate, and an RDS design only if you can explain a relational requirement that merits it. Check hot keys, item size, index write amplification, backup/recovery behavior and the treatment of a confirmed completion.

### B. Appointment and invoice system

The application relates customers, appointments, parts and invoices. Users need flexible queries over overdue appointments and invoice totals, and a last-part reservation must not oversell inventory. Traffic is steady during business hours. The business requires the reservation and invoice rules to remain correct under retries and simultaneous requests.

Compare RDS for a relational engine, a suitable Aurora candidate if its features matter, and DynamoDB only if you can specify keys/indexes/transactions that support every required operation and report. Include database capacity while quiet, connections/proxy needs, indexes, availability, backup, recovery and operations. A relational service is not automatically cheapest just because the model is relational; DynamoDB is not automatically cheapest because the company has few employees.

## Workcard

For each brief:

1. State what is known, assumed and missing. Identify the operation and correctness requirements that rule out or qualify each candidate.
2. Estimate a quiet month, ordinary month and peak month. State Region, request rates, read consistency, transaction mix, payload sizes, growth, data retention, backup policy, availability and transfer assumptions.
3. For DynamoDB, compare request-metered on-demand with hourly provisioned capacity when the forecast supports it. Add storage, indexes, backup/PITR, streams/global replication if chosen, and application compute. For RDS/Aurora, include instance/runtime, storage, IOPS, backup, replicas or multi-AZ capacity, data transfer, proxy/connections and application compute as applicable.
4. Use current AWS pricing information and record the date. Compare like-for-like behavior, reliability and restore requirements; leave unknown prices marked unknown.
5. Name the measurement or changed business rule that would reverse your selection.
6. Ask Codex to challenge your cost model. Verify all service billing facts in current AWS documentation and every price in the selected Region. Codex output is not a quote or a benchmark.

No AWS resource should be deployed for this exercise. It does not establish a real bill, approved architecture or learner result.

## Practice the comparison before collecting AWS prices

Imagine two suppliers offer ways to store the same device-status data. One charges mostly for each operation; the other charges mostly for reserved capacity. Start with the same basket of work, just as you would compare two grocery bills only after checking that both include the same food.

The following numbers are **invented teaching inputs**, not AWS prices or named service configurations. Both candidates have been stipulated to meet the same correctness, retention, recovery and response-time requirements **up to 12 million operations per month with the stated arrival pattern**. An operation here is one fictional billing unit, not an AWS read/write capacity unit. These monthly totals are paper calculations; do not deploy either design.

| Candidate | Monthly fixed cost, including the stipulated supporting services | Variable cost |
| --- | ---: | ---: |
| Metered | $80 | $0.00002 per operation |
| Reserved | $240 | No additional charge within the stipulated tested range |

Write your answers before opening the assessor:

1. At one million operations, calculate both totals and their difference. Repeat at ten million. Keep the units in each multiplication.
2. Find the operation count where both totals are equal. Explain what would happen to that point if the metered candidate needed another $40 per month of supporting services. Do not silently leave that service out of its total.
3. Change the arrival pattern: ten million monthly operations still arrive, but now half arrive in one hour. The prior response-time evidence did not test that burst. Which arithmetic remains valid under the fictional tariff, and which selection claim must wait for new evidence? Do not turn a monthly count into a peak-capacity measurement.
4. Change the recovery evidence: the cheaper candidate takes 40 minutes to restore the whole customer path; the requirement is 20 minutes. The other candidate restores it in 15 minutes at the same stipulated total. State your decision and the evidence you would need before accepting a proposed cheaper repair.
5. At 15 million operations, explain why extending the reserved candidate's $240 line is unsupported. List the additional pricing and capacity facts needed rather than inventing them.

A break-even point is where two cost lines meet under stated assumptions. It is not a promise that either design works there. For an AWS estimate, replace every fictional meter with the selected service's actual units, sizes, consistency, indexes, capacity settings, Region and price date. Retain uncertainty where those inputs are missing.

Ask Codex to check your units and identify one assumption that could reverse your choice. Keep your original arithmetic and decision, its feedback, and your revision separate. A correct AI calculation does not establish measured capacity or current AWS pricing.

After completing the fictional comparison, use [the dated Ohio request-unit example](PRICE-SNAPSHOT.md) to connect actual public rates to item size and consistency. It prices only selected request components, not the complete workload.
