# Did the cheaper service do the required work?

This is an original fictional exercise, not an AWS price quote or a certification question. No account or cloud resources are needed. Read [the cost lesson](../../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d), answer the questions, then compare your reasoning with the assessor notes.

## Your decision

A repair shop needs reports that are both correct and delivered before the morning meeting. All figures below cover the same period, workload boundary and cost-allocation method. The baseline costs $100 and delivers 1,000 accepted reports. A proposed change costs $72 and completes 900 reports. Of those, only 600 are **both correct and on time**. The other 300 are outside the acceptance rule. Assume these counts have been independently reconciled for this fictional exercise.

1. Calculate the candidate's cost per completed report and cost per accepted report. Compare the latter with the baseline. Can you recommend the change from the lower bill alone?
2. A dashboard includes 1,200 processing attempts in its denominator. What does that ratio measure, and why does it answer a different question?
3. A credit covers the candidate's entire $72 usage cost. What changes in the comparison, and what does not?
4. During an outage, the service costs $12 and produces no accepted reports. What should the dashboard show for cost per accepted report?
5. A second design has a fictional fixed charge of $40 per period plus $0.002 per accepted report; a third costs $0.01 per accepted report. Calculate both at zero, 1,000 and 10,000 accepted reports. What else must be true before cost alone decides between them?
6. A team shifts $15 of shared costs to another project and reports $15 of savings. What evidence would distinguish lower resource consumption from a different allocation policy?

Before accepting an AI answer, ask it to name its denominator and list missing evidence. Then check each figure yourself. Do not send account credentials or customer data to obtain help with this fictional exercise.

## Run the arithmetic

From the repository root:

```sh
python3 examples/costs/lifecycle-exercise.py
```

The script uses decimal arithmetic and checks expected results, including the changed acceptance rule above. It does not retrieve prices, measure report quality, read bills, enforce a budget or authorize deployment. A passing script checks these fixtures, not your ability to choose a real architecture.

## Assessor notes — read after answering

1. The candidate costs $0.08 per completed report but $0.12 per accepted report. The baseline costs $0.10 per accepted report. The candidate has a smaller bill and worse cost per useful result. Investigate why 300 completed reports failed acceptance; do not silently relax the business requirement to make the metric look better. These figures alone do not explain causation or show whether demand changed.
2. $72 divided by 1,200 is $0.06 per attempt. That describes processing cost per attempt, not delivery of accepted business outcomes. Retries can be necessary; do not delete them simply to reduce the attempt count.
3. Under the stated full-coverage assumption, the amount payable for these charges becomes zero. The underlying usage cost and acceptance failure remain. Keep the credit adjustment visible separately. Actual credit eligibility and expiration need their own account evidence.
4. Show “undefined: zero accepted reports,” together with the $12 cost and zero count. Zero dollars per report would falsely suggest efficient delivery. Do not average undefined ratios into later periods; aggregate comparable costs and counts before calculating a combined ratio.
5. At zero: $40 versus $0. At 1,000: $42 versus $10. At 10,000: $60 versus $100. Both are $50 at 5,000. These simplified models must describe equivalent accepted work, with appropriate capacity, security, latency and recovery. Omitted storage, networking, operational effort or idle resources can change the comparison; this is not a claim about any named AWS service.
6. Reconcile the total shared bill and usage before and after the change. If the total and usage remain unchanged, this is redistribution, not consumption savings. State the allocation rule, affected projects and interval. A real cost reduction still needs evidence that required service outcomes were preserved.

## Transfer the lesson

Replace “report” with a correctly fulfilled order or an approved claim. Define acceptance, the measurement window, deduplication of repeated events and treatment of late arrivals. Identify who can verify the count. Then write a recommendation with three parts: the observed cost, the accepted outcome count and the uncertainties that could change the decision. No independent reader assessment has yet been performed for this exercise.
