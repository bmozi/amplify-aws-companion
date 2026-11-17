# Sustainability decisions: preserve the useful result

Original design-only assessment for the [cost and context lesson](../../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d). No cloud deployment, energy measurement or emissions estimate is performed. Answer before reading the [assessor reasoning](SUSTAINABILITY-ASSESSOR.md).

For each case, state the accepted business outcome, what the evidence supports, what remains unknown and the next bounded check. A service name alone is not an answer.

1. **The shortened night.** Four identical workers run continuously in the baseline and for three hours in the candidate. Both are stipulated to produce 2,400 correct, timely reports. Calculate provisioned worker-hours, the reduction and hours per accepted report. An engineer advertises the same percentage carbon reduction. Which part of that statement has evidence?
2. **A changed promise.** The candidate's input is complete at 02:00 and its capacity window ends at 05:00, ahead of a 06:00 deadline. A failed attempt requires 90 minutes for fresh capacity, reload and rerun. Failure is detected at 04:45. Does the remaining window satisfy recovery? The shop also adds a five-minute daytime correction requirement. Explain which design assumptions must change; do not solve this by silently weakening either requirement.
3. **Growth.** The candidate grows from 2,400 accepted reports using 12 worker-hours to 5,000 using 25. Compare intensity and total use. Now suppose only 4,000 of the new reports meet the quality and deadline rule. Recompute intensity with the correct denominator. Does a higher CPU utilization reading settle the decision?
4. **Similar bytes, different jobs.** One stored report can be regenerated in ten minutes from retained authoritative input. Another copy is the only tested recovery route for an unreproducible source record. Someone proposes deleting both because neither was opened last month. Identify the decisions and evidence needed separately for each; include downstream recovery and retention requirements.
5. **A greener-sounding region.** A proposal changes region based on a general sustainability claim. The workload's customer contract permits processing only in its current country, and the new design adds continuous cross-region copying. Required service availability and end-to-end latency are untested. Write a provisional decision that separates a binding constraint from an unknown and states what evidence could change the result.

Finally, ask Codex to critique your reasoning without selecting or provisioning resources. Explain one changed case yourself afterward. These authored cases and rationales have not been independently calibrated or tried with learners.

## Count accepted outputs from attempt records

After answering the design cases, run `python3 examples/costs/resource-intensity.py` from the repository root. It uses Python's standard library and an in-memory SQLite database. Inputs are fictional worker-seconds, not CPU measurements or AWS billing records. They are a separate small fixture from the 2,400-report case above.

Predict whether a duplicate successful attempt counts as a second useful report, whether a failed retry consumes resource time, and whether a correct report arriving after its deadline belongs in the accepted set. The valid candidate preserves all four required identities and reduces total worker-seconds from 28,800 to 10,800, including failed attempts. Its resource-time reduction is 62.5%; no energy or carbon result is supplied.

The deceptive candidate produces six nominally successful attempts but only three distinct correct, timely outputs. Its lower resource intensity does not excuse a missing required report. A separate candidate preserves the count while substituting the wrong identity. Finally, a run with no accepted output has an undefined ratio, not zero cost or perfect efficiency. Read the identities and acceptance result beside the ratio.

Change the fixture to add a failed retry and predict the total before rerunning. Then change the deadline without changing the observed attempt timestamps: explain why the metric changes even though the work did not. Keep the original customer deadline visible rather than quietly relaxing it to improve the result. Ask Codex to identify omitted resources such as idle capacity, storage and transfer; this script does not measure those components, heterogeneous worker equivalence, energy, emissions or real customer acceptance.
