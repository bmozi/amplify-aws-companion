# Pricing-commitment lab: Would a lower rate lower the whole bill?

Imagine Maya's shop needs a worker for six hours. A commitment promises to pay a fixed amount every hour in exchange for a lower rate on eligible work. It is like buying a transit pass: its per-ride price can be attractive, but an unused pass still costs money. **All numbers below are invented.** They are neither AWS prices nor actual account usage.

The local model assumes six one-hour periods, an eligible On-Demand equivalent of USD 0.80 in a busy hour, a USD 0.40 hourly commitment, and a uniform 25% discount. It treats USD 0.40 as covering USD 0.5333… of otherwise On-Demand use per hour. Additional use stays at the illustrative On-Demand rate. There is no rollover from an idle hour. The model omits taxes, other charges, credit rules, real AWS discount application, purchase terms and the rest of any one- or three-year obligation. **Do not extrapolate six hours into a purchase case.**

First predict which schedule saves money: six busy hours, or three busy hours followed by a light hour and two idle hours. Then run from the repository root:

```sh
python3 examples/costs/pricing-commitment/compare.py
python3 -m unittest discover -s examples/costs/pricing-commitment -p 'test_*.py'
```

Read the [assessor](ASSESSOR.md) after writing down your prediction. Change the light hour from `0.20` to `0.80` and rerun. Which question is still unanswered even if the short sample becomes cheaper under a commitment?

For a real organization, start with representative eligible usage **after** removing waste and checking the customer promise. Compare On-Demand, a conservatively sized Savings Plan, and any matching Reserved Instance over their **full term** with current regional rates and terms. Account for variable demand, workload migration, capacity requirements, up-front payments and unused commitment. Review coverage and utilization later. A Reserved Instance's billing benefit and a capacity reservation are distinct; check the exact offering and scope. AWS documentation explains [Savings Plans commitments](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html) and [EC2 purchasing choices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-purchasing-options.html).

**Do not buy a commitment or upgrade an account to run this exercise.** AWS states that Free account plans exclude Savings Plans and Reserved Instances. The lab makes no AWS call and uses no credits. For any separately authorized experiment, check the current plan and credit terms and choose an appropriate whole-run limit and reserve. [AWS account-plan guidance](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html).

Ask Codex to challenge the stable-baseline assumption and propose a demand-drop case. Verify its arithmetic with the script and its AWS feature claims against current AWS documentation. Codex can help draft the decision record; it cannot establish future utilization, credit eligibility or authority to purchase.
