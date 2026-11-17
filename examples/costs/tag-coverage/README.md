# Find the part of the bill your labels cannot explain

Maya puts labels on boxes so she can tell which repair shop owns each one. An AWS resource tag is a label on a resource; activating a cost-allocation tag makes an eligible tag key available for cost reporting. Those are separate actions. A label is useful only when its meaning is consistent, it was applied to the relevant resource at the relevant time, and the selected billing data actually carries it.

This is a fictional paper exercise. It creates no AWS resources, makes no AWS calls and supplies no current price. Work the questions before opening [the assessor](ASSESSOR.md).

## Choose labels before counting

For this example, agree on three case-sensitive keys: `Workload` (`repairs`, `booking`, or `shared`), `Environment` (`production` or `test`), and `Owner` (a team identifier, not a person's email). Maintain approved values and a named owner who handles changes and exceptions. Do not put secrets or personal information in tags. A shared component marked `shared` is identified, but its cost has not yet been divided between workloads.

For user-defined cost-allocation tags, AWS says to apply the tag to resources and activate the **key** in Billing and Cost Management. It can take up to 24 hours for a newly applied key to appear for activation, then up to another 24 hours for activation. These are documented delays, not a promise that every bill line immediately acquires a value. Check the [activation instructions](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/activating-tags.html) and billing access for the account you actually use.

## Inspect a fictional month

The table is a complete, invented monthly **pre-credit cost** ledger, after the expected reporting delay. Assume all numbers are positive and in USD. A valid direct value is `repairs` or `booking`; `shared` is valid but is not a direct workload allocation.

| Cost line | Amount | Workload value in report | Additional observation |
| --- | ---: | --- | --- |
| Repair application | 60 | repairs | Valid direct label |
| Booking application | 25 | booking | Valid direct label |
| Shared network | 10 | shared | Shared driver not measured |
| Older test resource | 5 | blank | Tag applied halfway through the month; this line represents earlier use |
| Monthly support | 10 | blank | Fictional charge has no resource tag |
| Mislabelled resource | 10 | repair | Typo; ownership not independently verified |

1. Calculate the total, the fraction with any nonblank value, and the fraction with a **valid direct** workload value. Explain why they answer different questions. List the shared, blank and invalid amounts separately; reconcile them with direct amounts to the total.
2. The dashboard hides blank rows and reports $105 in tagged spend. Is that the whole bill? Does its nonblank total establish that every label is valid or that shared costs have been fairly assigned?
3. The team activates `Workload` after the month closes and requests a supported historical backfill. Which earlier blank value could this recover? What additional history must exist before you can answer? What cannot be created merely by activation? Check AWS's [backfill documentation](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-allocation-backfill.html), including its conditions and limits. A mid-month tag change can split reported costs; consult the [cost allocation report guide](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/configurecostallocreport.html).
4. Propose a review: record the same billing period and cost measure, valid-value coverage, invalid and blank amounts, shared-cost method, owner, follow-up date and a reconciliation to the unfiltered account total. Name an independent resource or billing observation needed to resolve `repair`. Do not silently rename it based on a guess.

**Changed case:** The owner verifies the $10 typo belongs to repairs, fixes the resource tag today, and shows no historical tag with the correct value. What changes about a current inventory report? What can and cannot be concluded about last month's bill and a historical backfill? A documented finance allocation may be proposed separately, with its evidence and effective period; do not pretend the original line had the corrected resource tag.

Ask Codex to inspect your arithmetic and identify one unsupported ownership or backfill claim. Save your first answer before using assistance, and verify any service claim in current AWS documentation. A local worksheet or model response cannot prove current account activation, billing coverage, a fair shared-cost driver, alert delivery or an actual customer result.
