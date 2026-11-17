# Two green credit checks can make one unsafe plan

Maya has an **invented** USD 80 credit balance and chooses to leave USD 75 for later learning. Two lab operators each plan a USD 3 run. Each separately sees `80 − 3 = 77` and calls the run safe. Together they have promised USD 6, leaving USD 74. The arithmetic did not fail; the operators used the same headroom twice. These numbers are a fixture, not a suggested limit or reserve for your account.

Predict the accepted and rejected counts, then run this standard-library exercise from the repository root:

```sh
python3 examples/costs/credit-commitments/lab.py
python3 -m unittest discover -s examples/costs/credit-commitments -p 'test_*.py'
```

The first comparison performs two independent checks. The second starts two local threads against one temporary SQLite register. `BEGIN IMMEDIATE` makes cooperating writers take turns while reading the existing commitments and adding a new one. Either A or B may win; exactly one USD 3 commitment is accepted and one is rejected. The winner's remaining uncommitted headroom is USD 2. The temporary register is removed after the run. Review the [illustrated decision](../../../book/figures/credit-commitment-boundary.svg) and [assessor reasoning](ASSESSOR.md) after recording your own explanation.

This is a planning model, not a link to AWS credits. The companion's `credit-check.py` reads a current account-plan snapshot and assesses one estimate; it does not reserve credits, atomically coordinate a GitHub job with a local Terraform run, cap usage or account for unrecorded work. A local SQLite file would also be invisible to another host. Until an accountable, shared active-run process exists, use **one live lab at a time** and inspect unfinished runs and retained resources before authorizing another. Set limits and a reserve appropriate to your account, then verify teardown and later billing separately.

Three focused tests change the number of contenders, repeat a run ID and submit invalid estimates. The fixture accepts positive whole cents and a nonblank ID; fractional cents, Boolean values and blank IDs are rejected before a claim is written. Three USD 3 starters still yield only one local commitment. A repeated ID returns `False` without adding a second claim, whether or not estimated headroom remains. That response still cannot tell a caller whether an outside job actually ran. A real shared coordinator would need an authenticated run identity and a way to reconcile uncertain outcomes. [Unit 34](../../../reader/BOOK-LOCATORS.md#book-2bdcd6c8f5763890) carries the same arithmetic into a separate GitHub-versus-Terraform decision.

Changed case: A third operator says yesterday's lab finished, but its queue and log group remain. Decide whether to release its commitment, start the next run, or investigate first. Ask Codex to explain why a successful destroy command, an account credit snapshot and a completed customer test answer different questions. Inspect the run record and resource inventory before accepting its answer. This local exercise uses no AWS resources or credits.

Second changed case: the admitted USD 3 run eventually costs USD 6. The original local commitment did not enforce a USD 3 spending cap, and even this one run would leave only USD 74 if the fictional balance were otherwise unchanged. Explain which observation would reveal the difference, when it might arrive, and why the next run must wait for a fresh balance and resource review. Read the [assessor](ASSESSOR.md) only after writing your answer.
