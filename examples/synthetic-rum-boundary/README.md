# Three windows on one customer journey

**Offline learner exercise for Chapter 15 (stable source unit 28).** No AWS credentials, account access or cloud resources are needed. The names and counts are fictional. Read the [chapter's green-robot lesson](../../reader/BOOK-LOCATORS.md#book-bd39b2eaefd49109) and its [three-window figure](../../book/figures/synthetic-rum-ledger.svg), then try this without opening [the assessor](ASSESSOR.md).

## Start with a repair shop

Maya promises that an accepted repair booking will reach a durable confirmed state. A scripted browser books through the standard desktop path. Some real browsers send client reports. A separate intake ledger records accepted and completed bookings. Think of these as three windows into the shop: the test visitor, some actual visitors, and the order book. A view through one window cannot show everything happening behind the other two.

For this exercise, `browser_visits` is an independent, complete count of visits for each five-minute window; it is **not** supplied by RUM. The `accepted` and `completed` counts refer to the same fictional cohort. The accepted-work inventory is complete only when `accepted_inventory_complete` is true. Reported canary runs and received RUM sessions are observations, not guaranteed populations. An error session is counted at most once. These stipulations make arithmetic possible; a real incident would need evidence that they hold.

| Window | Scripted runs | Client reports | Accepted-work evidence |
| --- | --- | --- | --- |
| A: green probe, hurt browsers | 5 expected, 5 reported, 5 successful | 200 independently counted visits; 40 RUM sessions received; 12 reported an error | 70 accepted, 65 completed; inventory complete |
| B: silent client telemetry | 5 expected, 5 reported, 5 successful | 180 visits; 0 RUM sessions received | 60 accepted, 60 completed; inventory complete |
| C: incomplete probe and inventory | 5 expected, 3 reported, 2 successful | 150 visits; 20 RUM sessions received; 0 reported an error | 55 accepted, 55 completed; inventory completeness unverified |

## Make three decisions before running code

1. For each window, write a sentence about what the canary actually observed, a separate sentence about real-browser evidence, and a separate sentence about accepted work. Name every missing denominator or unverified population. Which window, if any, proves that every customer succeeded?
2. In A, calculate the error fraction among **received RUM sessions** and the unfinished count among **stipulated accepted requests**. Explain why neither `12/40` nor `12/200` establishes an all-customer error rate. In B, explain why `0/0` is unknown experience rather than a perfect score. In C, keep missing scheduled runs and an incomplete intake inventory visible even though the twenty received sessions reported no error.
3. Choose one next read-only observation for each window that could change an incident decision. Decide what can be communicated now, who would own any proposed change, and what would verify the customer outcome after it.

Run `python3 examples/synthetic-rum-boundary/observe.py` from the repository root to see bounded arithmetic. It reads [windows.json](windows.json), validates impossible counts, and prints separate evidence statements. `python3 -m unittest discover -s examples/synthetic-rum-boundary -p 'test_*.py'` checks the three different failure boundaries. The script does not estimate a population error rate, infer root cause, or declare recovery.

## Change one fact

Copy [windows.json](windows.json) to a temporary file outside the repository. In A, change `rum_received` from `40` to `0` and `rum_error_sessions` from `12` to `0`, leaving the 200 independent visits, five green canary results and unfinished accepted work intact. Run `python3 examples/synthetic-rum-boundary/observe.py /path/to/your-copy.json`. Rewrite your status sentence. What conclusion disappeared, and which concern did not? Do not edit the source fixture to make a test pass.

Next, restore A and set `canary_expected`, `canary_reported` and `canary_success` to zero. A `0/0` probe result means no scripted runs were scheduled, not that a test passed. The client errors and unfinished accepted work remain separate concerns. Ask who owns the schedule and whether a probe should have run before choosing a response.

## Design a bounded AWS observation

On paper, identify the canary route, identity, Region and schedule; the step/artifact check for a failed or missing run; the RUM pages, sample setting and client error types; the accepted-work source; and how you would align windows without exposing customer data. Include an owner, stop condition, event/URL field review, notice or consent decision, retention, and a whole-path cost estimate covering RUM events, optional logs/traces, canary runs, Lambda, metrics and S3 artifacts. Find current regional prices, account eligibility and your own spending limits before proposing any live run. This exercise stays offline.

Ask Codex: “For each fictional window, identify every claim that exceeds the observed source and denominator. Keep canary runs, received real-user sessions and accepted-work records separate. Propose a read-only next check; cite the current AWS Synthetics and RUM documentation for service-specific claims. Do not deploy or infer that no report means no error.” Verify its source links and arithmetic yourself.

The [assessor](ASSESSOR.md) gives expected reasoning and limits after your own attempt.
