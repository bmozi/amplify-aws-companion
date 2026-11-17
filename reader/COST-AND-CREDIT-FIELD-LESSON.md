# A cloud lab needs a price, a stop plan and a return visit

Maya rents a workshop for an afternoon. Paying for two hours of tools does not automatically return them at closing time. A cloud experiment has the same trap: the request may finish while storage, logs, an idle resource or a recovery copy continues to exist. Before Maya starts, she needs to know what she might rent, how long she intends to use it and who will check that it was returned.

You can practice this reasoning without an AWS account. Run the [first local cost exercise](../docs/FIRST-LOCAL-EXERCISE.md), predict its result before reading the output, and write down which quantities changed. Its prices and credit balance are invented. Then use the [three-price decision exercise](../examples/costs/reader-budget-decision/README.md) to test a case where credits pass but gross monthly budget headroom fails. Both exercises check supplied arithmetic, not current AWS prices or a cloud spending limit.

## Four different answers to “can I afford this?”

| Question | Evidence to collect | What it cannot prove |
| --- | --- | --- |
| **What might this experiment use?** | A dated, Region-specific estimate for the selected resources, requests, data, retries, logs, transfer, runtime and anything retained afterward | The amount AWS will eventually record |
| **What does my account allow today?** | The current plan, service eligibility, credit balance and each relevant credit's terms and expiry | That every selected charge will be covered by credit |
| **When will I notice a problem?** | A budget and reachable notification recipient, with the actual threshold and included charges checked | That spending stops at the threshold |
| **How will I stop and verify?** | A named owner, stop time, removal steps, exact resource inventory and a later billing check | That closing a browser tab, stopping traffic or seeing an empty local state file removed every resource |

AWS distinguishes **Free** and **Paid** account plans. The Free plan has eligibility limits and ends when its time or credits run out; a Paid plan can create charges beyond available credits or for ineligible usage. Creating or joining an AWS Organization or setting up Control Tower can also change a Free account's plan and credit treatment. Check [AWS's current plan guidance](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-plans.html) and the [Free Tier FAQ](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-FAQ.html) before making an account decision. Your own Billing console and credit terms, not an author's dated balance, decide what is true for your account.

An exercise may supply a fictional spending limit or credit balance so you can practice a decision. Treat those numbers as **case inputs**. For a real run, choose limits from your own plan, eligibility, workload, risk tolerance and available credits; copying a worksheet's thresholds cannot make your run safe or affordable.

An estimate is a **prediction**. A budget is an **alarm**. A workload limit can constrain one route through the system. Cleanup removes selected resources. These are useful together because none is a universal dollar cap. AWS says budget information and notifications can lag usage; costs can pass a notification threshold before it arrives. Review [AWS Budgets guidance](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) when you configure alerts.

## Make one bounded lab decision

Suppose Maya wants to publish a small demonstration page. First draw the path: browser request, Hosting, any backend call, stored data, logs and downloads. If the page is static, do not invent a database. If it has private notes or file uploads, include the services and permissions that actually provide them. Then write one row for every charge driver, with unit, quantity, duration, Region, dated price source and a reason for the quantity. Add retries, failure logs and resources that survive the demonstration. A low Hosting subtotal does not price an unexamined backend.

Before an authorized live run, record:

1. **Account and authority:** account, Region, scoped non-root deployment identity and the exact resources it may change.
2. **Plan and price:** current plan, selected-service eligibility, each relevant credit's applicability and expiry, a complete estimated run, your chosen spending limit and a reserve for later work.
3. **Stop and cleanup:** maximum runtime and traffic, stop signal, cleanup owner, retained-resource decision and a way to query the exact resources afterward.
4. **Later evidence:** observed requests and results, removed-resource inventory, credit and budget readings with timestamps, and a later billing reconciliation. Record unrelated account activity and billing delay as attribution limits.

Use the [cost worksheet](../examples/costs/worksheet.json) with the [local calculator](../scripts/estimate-lab-cost.py) for practice, and inspect the selected lab's own README before running commands. A plan with `pending` prices or cleanup decisions is a lesson draft, not a deployment ticket. Organization-dependent exercises in this guide stay on paper unless the learner has a suitable, separately authorized environment.

## Test whether you understand the boundary

**Predict first.** A budget alert is set at your chosen limit. A load test is allowed to run for another hour after that alert. Which charges can still grow, and who acts when the message arrives?

**Change one fact.** The page now accepts private files and sends notifications. Revisit the resource list, access rules, estimate, failure paths and cleanup plan. If a service is not available under your current account plan, explain the design on paper rather than changing the plan merely to finish this exercise.

**Check your explanation.** A strong answer names the meters that continue to accrue, treats notification delivery and response as separate events, includes the new storage and messaging paths, and keeps the remaining uncertainty visible. It does not claim an alert or a credit balance prevents a final charge. Ask Codex to challenge an omitted cost driver or surviving resource; keep its suggestion separate from your estimate and verify current AWS rules and prices yourself.
