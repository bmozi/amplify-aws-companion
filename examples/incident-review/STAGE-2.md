# Stage 2: additional fictional evidence

These observations are authored teaching inputs. They are not real logs, measured percentiles or a complete sampled population.

At 09:04, the investigator obtains:

| Observation | Evidence supplied |
| --- | --- |
| Version comparison | During 09:02–09:03, 8 of 40 completed v1 bookings and 2 of 10 completed v2 bookings exceed two seconds |
| Three correlated requests | Two v1 requests and one v2 request each spend most of their elapsed time waiting for the same supplier call |
| Local resource view | The sampled application workers show no CPU or memory saturation; connection/queue details are not available |
| Supplier notice | A notice posted at 09:03 reports elevated API latency beginning at 08:59; it does not name an internal cause |
| Accepted-work inventory | Twenty accepted bookings are unfinished; eight have passed the selected completion deadline |

The coordinator pauses rollout expansion and returns traffic to v1 at 09:05. The observed latency remains elevated through 09:08. At 09:09, supplier-call timing improves in the sampled traces. New synthetic bookings succeed within the target. At 09:10, five previously accepted bookings remain unfinished; two are overdue. At 09:12, the exercise supplies a reconciled inventory with every accepted request assigned a terminal business outcome and no unexplained missing IDs. Some outcomes are failures that need customer follow-up; “terminal” does not mean “successful.” A relevant cross-customer access check still denies access.

Revise your hypotheses and state their limits. Calculate each version's observed late fraction, but do not claim that these small, possibly different samples prove equivalent versions. State what rollback did and did not establish. Decide whether to declare recovery at 09:09, 09:10 or 09:12, and define which meaning of recovery you use. Identify the missing evidence needed to measure the complete incident's success rate and customer impact.

Write a short update to the fictional coordinator, without sending anything. Include observed impact, current action, uncertainty, next check and owner. Then propose one detection improvement and one operating improvement with acceptance criteria. Finally change the case: suppose only v2's supplier requests use a new timeout setting. Explain what additional comparison is needed before reusing your original conclusion.
