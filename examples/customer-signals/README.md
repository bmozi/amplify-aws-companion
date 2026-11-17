# Count customer outcomes before choosing an alarm

Run `python3 examples/customer-signals/lab.py` from the repository root. It uses the standard library and synthetic fixtures; it sends no telemetry or notifications.

The first window has 5 bad requests out of 10. The second has 5 out of 990. The combined bad-request fraction is 10/1,000, or 1%. Averaging the two window percentages gives about 25.25%, which answers a different question because it weights a ten-request window equally with a 990-request window.

At a fictional request-based 99% target over the evaluated interval, 1,000 requests allow 10 bad outcomes. Twenty bad outcomes consume twice that allowance and leave minus 10. These are scenario calculations, not an AWS service-level agreement, a time-based availability calculation or a production alert recommendation. No observations return an explicit unknown state rather than a perfect score.

The second exercise considers four accepted jobs at time 60 with a 30-second completion deadline. One completed on time, one completed late, one is overdue and unfinished, and one is not yet due. The mature cohort therefore has one good and two bad outcomes. A recent job does not count as failed merely because it is unfinished.

Predict the results before running. Then change the request target to 99.9%, recompute the allowance, and explain why the number of requests matters. Change the completion deadline to 45 seconds and identify the revised cohort. Ask Codex to critique your denominator and event chronology before letting it compute the answer.

The executable assertions also reject impossible counts, booleans masquerading as counts, fractional counts and a completion before acceptance. The lab does not simulate delayed telemetry, CloudWatch alarm evaluation, sampling, alert routing or an actual queue. See [the observability unit](../../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115) and E12.

## A changing workload can reverse the overall rate

The same script checks a complete fictional two-period fixture. Web acceptance rises from 90/100 to 19/20; counter acceptance rises from 1/10 to 20/100. The combined rate nevertheless falls from 91/110 to 39/120 because the workload mix changes. The chart in unit 08 reads these fixture counts and displays both counts and percentages. This is arithmetic evidence, not measured customer performance or proof of causation.

Explain why both the aggregate and segmented rates matter. Then suppose one channel's feed stops: describe the incomplete state instead of treating missing records as zero requests. For a manager's staffing decision, identify the missing workload-complexity and staffing evidence. These are original transfer prompts; no independent reader assessment has been conducted.

After recording your predictions, compare them with the separate [assessor notes](ASSESSOR.md).
