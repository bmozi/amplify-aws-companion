# Customer outcomes: assessor notes

Use these notes after making your own prediction. The numbers are fictional and describe the local fixture, not a service guarantee or a CloudWatch result.

## Change the target

At a 99.9% request-based success target, the allowed bad fraction is 0.1%. In a fixed set of 1,000 eligible requests, that permits one bad request. Ten bad requests consume ten times the allowance; twenty consume twenty times it. With 10,000 eligible requests, the same target permits ten bad requests. This is a calculation over the specified set, not a prediction of future traffic. A fractional allowance is possible for a different count; do not round it before checking the ratio.

## Give the jobs 45 seconds

At second 60, the three jobs accepted at second 0 are mature; the job accepted at second 50 is not yet due. The completions at seconds 20 and 40 are on time under the changed deadline. The unfinished job accepted at second 0 is overdue. The mature result is therefore two on time and one late or missing, with one job not yet due. It differs from the 30-second case because the second job now meets the deadline, not because the recent job failed.

This fixture assumes a complete, trustworthy history and a consistent clock. Delayed or missing events could change what an operator can conclude; the local program does not establish collection completeness.

## Check the changing mix

Web improves from 90/100 (90%) to 19/20 (95%); counter improves from 1/10 (10%) to 20/100 (20%). Combined, acceptance falls from 91/110 (about 82.7%) to 39/120 (32.5%). More of the later requests came through the lower-rate counter channel. A single aggregate hides the channel improvement, while channel percentages alone hide the overall change experienced across the combined workload.

If a feed stops, the complete aggregate is **unknown** until the missing population is accounted for. A zero measured count is not proof of zero requests. A staffing decision also needs the volume and complexity of each channel, staffing and coverage during each period, and any other relevant changes. The counts alone do not prove the reason for the rates or which staffing action will help. Ask Codex to explain its denominators and competing hypotheses; check its arithmetic and assumptions yourself.
