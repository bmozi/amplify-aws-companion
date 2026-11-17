# Three prices for one cloud experiment

Maya plans a small demonstration. She has enough trial credits to cover the estimated run, so a teammate says, “We can launch.” The monthly budget report tells a different story: gross usage plus this run and a chosen safety margin would pass the alert threshold. Both observations can be true. Credits help pay eligible charges under their terms; a cost budget can [exclude credits](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_budgets_CostTypes.html) and show a separate pre-credit view. AWS also [warns that budget data and notifications can lag usage](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html).

This standard-library exercise uses **fictional** balances and reader-chosen limits. It never reads an AWS account. The values in `cases.json` are practice inputs, not thresholds to copy. Before running it, predict the decision for each row:

| Case | Per-run estimate versus limit | Credits after run versus reserve | Gross monthly usage plus run and margin versus budget |
| --- | --- | --- | --- |
| A | USD 3 ≤ USD 4 | USD 85 − USD 3 ≥ USD 75 | USD 46 + USD 3 + USD 2 > USD 50 |
| B | USD 3 ≤ USD 4 | USD 80 − USD 3 ≥ USD 75 | USD 40 + USD 3 + USD 2 ≤ USD 50 |

Run from the repository root:

```sh
python3 examples/costs/reader-budget-decision/lab.py
python3 -m unittest discover -s examples/costs/reader-budget-decision -p 'test_*.py' -v
```

Case A should **hold** even though its credit arithmetic passes. Case B becomes a **review candidate**, not permission to deploy. The program trusts the supplied estimate, checked-credit flag and current-usage flag. It cannot tell whether the forecast includes transfer, logs, retained resources, cleanup or another team's work. It cannot fetch credit terms, judge whether credits apply to the selected service, reserve headroom across two operators, stop spending or account for delayed billing.

## Change one fact at a time

Copy `cases.json` to a temporary file outside the repository. After each edit, run `python3 examples/costs/reader-budget-decision/lab.py /path/to/your-copy.json`. This preserves the original cases for the next reader.

1. In Case B, raise `gross_monthly_used_usd` from `40` to `46`. Which decision changes without changing the credit balance?
2. Give Case B two separate USD 3 runs against its USD 80 balance and USD 75 reserve. Each operator independently calculates USD 77 after one run. What happens to the **combined** USD 6 plan? Run the [two-operator commitment lab](../credit-commitments/README.md) to see why a shared reservation process matters.
3. Set `credit_applicability_checked` or `usage_snapshot_current` to `false`. Explain why favorable arithmetic cannot replace a current account reading or the selected credit's terms.
4. Make the estimate omit a surviving log group. The code still accepts the number you typed. What inventory, stop rule and later billing check would expose the omission?

Set both flags to `false` as well: the result names both missing evidence items and holds. Fixing one supplied flag leaves the other hold in place. The flags are your statements about evidence, not checks performed by the program.

Write your first answer before reading the [assessor](ASSESSOR.md). Ask Codex to find one hidden cost driver and one way the two-operator case could pass separate checks but exceed a shared limit. Check its arithmetic and source assumptions yourself. If you later plan a real lab, choose your own whole-run limit, credit reserve and gross-budget margin for your account; check current plan and eligibility, use a scoped identity, name cleanup, and reconcile the later bill. A budget alert and this exercise are **not** hard spending caps.
