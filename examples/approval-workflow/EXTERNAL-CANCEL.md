# Can the manager still stop the publication?

The manager notices a mistake in a reviewed training-site price list. A worker may already have passed the point where it can stop before contacting the publisher. The manager presses Cancel. What should the screen say?

Before running the fixture, write down your prediction for each order of events:

1. The manager's cancellation reaches the workflow **before** the worker claims the operation.
2. The worker claims the operation, then the manager requests cancellation, then the publisher commits but its reply is lost.
3. The worker claims the operation and cancellation is requested, but one lookup finds **no provider row**.
4. The provider effect is positively confirmed before the manager requests cancellation.

For each, state the local workflow state, whether a provider effect is established, the honest user-facing status and the next observation needed. Use `unknown` where the evidence ends. Do not peek at the [assessor](EXTERNAL-CANCEL-ASSESSOR.md) until you have preserved your first answer.

From the repository root, run:

```sh
python3 examples/approval-workflow/external_cancel_lab.py
python3 -m unittest discover -s examples/approval-workflow -p 'test_external_cancel_lab.py'
```

The first SQLite file holds the admitted action, the stable operation ID and the manager's cancel request. The second file acts as a publisher. Two matching reviews admit the original action. `start_dispatch()` claims it under one local write transaction; `request_cancel()` uses the same transaction discipline. If cancellation wins **before** the claim, this fixture stops its send. Once a worker has claimed the operation, a cancellation request cannot prove the worker stopped. The separate `publish()` function may commit and then lose its reply. A matching read by operation ID can establish the effect; one absent read cannot establish a durable absence.

The six focused tests check these differences through stored rows and responses: stop before claim, an outside effect that bypasses the stopped send, confirmed effect after cancellation and lost reply, missing provider observation, wrong cancellation actor or conflicting provider row, and attempted cancellation after a confirmed effect. The publisher's idempotency behavior is a local fixture assumption. The demonstration uses trusted fixture identities and clocks, not login, a cloud workflow, an HTTP publisher or a real visitor.

## Change the timing

The manager requests cancellation while the worker is paused just after its claim. A provider lookup returns no row. The worker resumes and sends the same operation. Explain why a green **Cancelled** message after that first lookup would be false. Identify the positive receipt needed to say publication happened. If publication happened, decide who may approve a corrective publication and how you would verify that a visitor sees the corrected page. Keep those two actions and receipts separate.

Now change one fact: the manager's cancellation commits before the worker's claim. What has this fixture prevented? What has it **not** proved about another worker or a provider call that bypasses this code? Your answer should describe the boundary you actually tested rather than promise a distributed cancellation guarantee.

Ask Codex to draw the local and provider timelines, mark each observation and invent one negative control. Preserve its coaching separately from your first answer. Compare with the [assessor](EXTERNAL-CANCEL-ASSESSOR.md) afterward.

No AWS resource or trial credit is used. A future live test still needs scoped non-root authority, a conservative whole-run estimate against account-chosen spending and reserve limits, a defined stop, cleanup and delayed-bill review. Organization-dependent infrastructure remains design-only in this exercise.
