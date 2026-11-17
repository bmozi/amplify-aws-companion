# A smaller worker pool can miss the promise

Maya's repair desk accepts 90 synthetic requests at the start of a shift. The customer-facing promise has two parts: acknowledge an accepted request durably, then complete all 90 correct repairs by the end of minute four. A queue can separate those moments, but it cannot make capacity or a deadline disappear. The small [model](lab.py) examines only the second part. It **assumes** every request was accepted durably, every job takes equal work, no retries occur and all completed jobs are correct. It does not test SQS, Lambda scaling, per-customer fairness, billing, electricity or carbon.

Run from the repository root:

```sh
python3 examples/demand-alignment/lab.py
python3 -m unittest discover -s examples/demand-alignment -p 'test_*.py' -v
```

One fictional worker completes 15 jobs per minute. Four workers retained for all eight observed minutes use 32 **provisioned worker-minutes** and meet the deadline. Two workers retained for four minutes use eight worker-minutes and also meet it. One worker for six minutes looks smaller at six worker-minutes, but only 60 of 90 finish by minute four. Thirty are late. The model counts provisioned capacity, including idle minutes; it does not equate that proxy with actual Lambda charges, energy or emissions. The two-worker plan has a nominal one-minute completion margin, yet a one-worker loss immediately after minute one leaves 15 late. If the burst becomes 120, the two-worker plan consumes all four minutes; one lost worker-minute leaves 15 unfinished at the deadline.

| Candidate | Correct by minute four in the model | Provisioned worker-minutes | Decision under the stated promise |
| --- | ---: | ---: | --- |
| Four workers for eight minutes | 90 of 90 | 32 | Meets; extra provisioned time is a review target. |
| Two workers for four minutes | 90 of 90 | 8 | Meets nominally; test burst and recovery margin. |
| One worker for six minutes | 60 of 90 | 6 | Reject under the unchanged deadline. |
| Two, then one after an interruption | 75 of 90 | 7 | Reject if that interruption belongs in the required recovery envelope. |

Try changing the burst, worker schedule and deadline in a temporary copy. Keep the same accepted jobs, correctness rule and observation horizon when comparing options. Report peak backlog, late and unfinished work, retries you have **not** modeled, queue polling, table reads/writes, logs and the client-visible delay. The checked-in A02 [Terraform](../../architectures/reliable-workflows/infra/main.tf) has an SQS work queue and a Lambda mapping capped at two concurrent workers, but its worker batches and durations are not this fictional rate. A03 last-seat admission cannot be delayed into this queue without changing the customer promise: its conditional authoritative decision is separate.

The [six-practice SUS 02 review](../../curriculum/well-architected-reviews/A02-A03-SUS02.md) asks you to choose a bounded next measurement. Ask Codex to argue for the cheapest-looking option, then require it to count late jobs and name the missing AWS meters and failure cases. The [assessor](../../curriculum/well-architected-reviews/A02-A03-SUS02-ASSESSOR.md) explains the changed cases after your first answer. No AWS resource or credit is used here.
