# Find the avoidable cost without hiding the overloaded path

This fictional, cloud-free case accompanies [the cost investigation lesson](../../../reader/BOOK-LOCATORS.md#book-ce2c0ca8478b6d63). The [CSV line items](line-items.csv) are a **normalized teaching extract**, not an AWS CUR 2.0 file or a measured bill. The [adjustments](adjustments.csv) are account-level fictional credits. Run `python3 examples/costs/optimization-audit/lab.py` from the repository root, write your decision, then read the [assessor notes](ASSESSOR.md). The script uses exact decimal arithmetic, validates the supplied rows and makes no AWS call.

For the [COST 03 cost-per-result continuation](../../../curriculum/well-architected-reviews/A02-A03-COST03.md), the separate [outcome-count fixture](outcome-counts.csv) declares **invented summary counts**, not customer receipts. Run `python3 examples/costs/optimization-audit/unit_cost_lab.py`, then `python3 examples/costs/optimization-audit/unit_cost_lab.py --current-outcomes 0`. The first comparison reports only a *direct repair-tagged, pre-credit proxy*; the second keeps the charges but makes the per-result ratio undefined. The script rejects missing, duplicate, fractional, negative or falsely relabeled outcome summaries. It cannot verify distinct identities, correctness or deadlines from two aggregate rows, allocate shared/unattributed charges, or prove live AWS unit cost. Keep those missing observations visible when writing the decision.

Continue with the [tag-coverage exercise](../tag-coverage/README.md) to choose a simple taxonomy, reconcile valid and missing labels, and distinguish historical tag assignment from activating a key for billing. Its numbers are a separate fictional month.

## The seemingly stable project dashboard

Maya's repair company has two complete fictional monthly snapshots called `baseline` and `current`, using the same pre-credit accounting measure and scope. The `repair` project view looks unchanged. The full account cost rose. A teammate says the worker is underused and should be resized immediately; another says the account credit kept the bill below the proposed alert level. Neither has checked the monthly close, destination traffic, resource inventory or customer report deadline.

Separate evidence from the CSV adds four facts:

- A 14-day worker recommendation window shows 12% average CPU, but the monthly close on day 28 reached 92% CPU and finished just before its 06:00 deadline. Recovery rerun demand has not been tested.
- The database's ordinary CPU is 54%; during close it reached 89%, and its measured p99 response time was 250 ms against a 100 ms promise. The cause of the latency is unknown.
- `old-volume` is unattached in the fictional resource inventory, but no owner or restore requirement has been established. `snapshot` is owner-retained until a fictional November 30, 2026 review date; it is not an orphan merely because no process writes to it.
- The `internet_out` line moved from 20 GB to 180 GB. The source, destination, customer purpose and transfer boundary have not been traced. Its `Network` service name in this toy extract is a teaching label, not a real AWS product code or rate.

## Your investigation

1. Reconcile the `repair`, `shared`, `unallocated`, full-account pre-credit and after-credit totals for each period. Compute the change in network quantity and cost. Explain how an unchanged tagged view can coexist with a higher account total. Do not assign an untagged row to repair by guess or subtract the full account credit from repair's usage.
2. Which resource is a **candidate** for safe waste removal? What owner, attachment/history, snapshot, retention and restore checks would precede deletion? Which resource is a candidate for rightsizing, and why is the 14-day average insufficient? Which path may be underprovisioned despite the opportunity to save elsewhere? Write the customer-result test and rollback for each proposal.
3. Design a monthly **fictional** pre-credit cost alert around the expected $101 baseline and a $110 investigation threshold. State period, scope, cost measure, actual/forecast choice, inclusions, recipient, delivery check and operator action. Compare the result if the team instead watches after-credit net cost. Explain why neither is a hard USD 110 cap or a substitute for a bounded run estimate and reserve chosen for the account.
4. For a real CUR 2.0 investigation, specify the billing period and usage period, line-item type, service and usage type, optional resource ID, active cost-allocation tag and omitted rows. Explain why enabling resource-level data can enlarge the export, why a filtered query needs reconciliation to the same-scope total, and why the destination/query/retention/access cost belongs in the design. No export is created in this exercise.
5. Offer two bounded explanations for the network change and identify the evidence that would distinguish them: for example, legitimate customer downloads versus an unintended cross-boundary copy. State the transfer direction and endpoints before pricing. Do not infer a security incident from the bill alone.

## Change cards

- The monthly close now misses its deadline after a proposed worker resize. What would the rollback and customer check require?
- The `old-volume` owner says it contains the only decryptable recovery point. What changes before deletion?
- A new project tag is activated halfway through the current month. Can it make the earlier unallocated rows disappear retrospectively without a documented supported backfill?
- The next billing snapshot raises the credit adjustment but leaves the pre-credit network line unchanged. Did resource efficiency improve?
- A newly added file transfer uses a different Region and sends data back to an office. Which route, direction, request and fixed-hour meters might apply, and which ones must be checked rather than assumed?

Ask Codex to make two competing explanations for each anomaly, identify a query or observation that separates them, and flag any cost-saving recommendation that would break the report deadline or the retained restore promise. Verify its AWS-specific claims in current primary documentation. An AI-generated savings figure is not an observed saving.
