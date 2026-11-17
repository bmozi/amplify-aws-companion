# COST 05 lab: the cheapest-looking worker

Maya's shop accepts repair requests. Two teams offer designs that, **for this paper exercise only**, are assumed to durably accept each request, finish 99% within five minutes, preserve one day of retry state, and recover within one hour. The *managed* candidate is a queue plus managed worker and managed data service; the *self-operated* candidate keeps workers and a database running. These are architecture sketches, not measured AWS implementations. The labels do not prove either design meets the promise.

The [fictional input](fictional-case.json) gives two months at 1,000 jobs per month and ten at 500,000. Every amount is an invented USD teaching input, **not an AWS price**. Both candidates include fixed service cost, per-job usage, storage, transfer, logs, human operations time, and license cost. The same $60/hour labor assumption makes the comparison transparent; a company would supply its own fully loaded labor basis. No discounts, credits, taxes or one-time migration are included. A real estimate would identify those omissions and price every applicable meter by Region, date and service terms.

Run `python3 examples/costs/service-selection/compare.py` from the repository root. The script uses decimal arithmetic and refuses a missing cost meter. Its results are a reproducible calculation of the **stated assumptions**, not a bill or a certification answer key. It makes no AWS call.

```text
Customer promise ──> candidate architecture ──> complete meters
       │                       │                       │
       └──────── verify fit ───┴──── usage over time ──┘
                                      │
                              choice and revisit date
```

Before opening the [assessor](ASSESSOR.md), write an architecture decision record with (1) the identical customer promise, (2) pilot and growth monthly and lifetime totals, (3) a license-term question, (4) the capacity/failure test that might disqualify each candidate, and (5) a revisit trigger. Then change growth usage to **1,000,000 jobs/month** and recompute. Would you switch services immediately? Ask Codex to act as a skeptical reviewer: name an omitted meter, challenge the operations estimate, and propose a failure that the cheap candidate might hide. Verify its arithmetic with the script and its AWS statements against current official sources. Do not treat the assistant's answer as measured throughput or an account spending limit.

To adapt this to a real project, map the candidate's actual components and direction of data movement, check current regional prices and license terms, estimate setup/migration and exit cost, test correctness and deadlines under normal and failure conditions, then capture observed usage and revisit the decision. Before a live trial, select the account and Region, check credits and eligible services, and compare a whole-run estimate with spending and reserve limits chosen for that account. The [cost-and-credit field lesson](../../../reader/COST-AND-CREDIT-FIELD-LESSON.md) explains the decision. This exercise authorizes no cloud deployment.
