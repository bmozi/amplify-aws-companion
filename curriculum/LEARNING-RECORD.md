# Keep a learning record you can explain

Imagine returning to a lab a month later. “It worked” leaves you guessing which version ran, what it checked and whether you understood it. A short record should let you repeat the task and explain its limits. Use this alongside [the learning routes](LEARNING-ROUTES.md) and [chapter exit checks](PREREQUISITES-AND-EXIT-CHECKS.md).

The companion already has a compact [JSON evidence template](../examples/advanced/evidence-template.json). This worksheet adds the teaching sequence: predict, observe, explain, change the situation, then assess the result. Either format can retain evidence; neither automatically proves skill.

## Copy this form for one attempt

Save your copy outside tracked source, or keep it in a private notebook. Do not commit credentials, raw Terraform state, customer records or sensitive account output. Name a sanitized evidence location when the underlying record needs restricted access.

| Field | Your entry |
| --- | --- |
| Date and attempt | Date; guided attempt, changed case or independent attempt |
| Exercise and requirement | Exact lesson/chapter ID and the capability you intend to show |
| Source | Git commit or distributed archive hash; describe local edits |
| Environment and scope | Tool versions; design-only, local, emulated or live AWS; never conflate these |
| Prediction, written first | Expected result and why; preserve this before viewing the answer |
| Action | Exact command or design decision; for a command, include its working folder |
| Observation | Actual result, exit status and relevant evidence location; leave blank until observed |
| Explanation | Why the result supports or contradicts your prediction |
| Assistance | What you did unaided; which hints, solutions, generated code or assessor help you used |
| Changed case | The new constraint, your revised prediction and separately observed or calculated result |
| Cost and cleanup | What was created, what remains and what cleanup was verified; distinguish fictional cost from actual usage |
| Unresolved | Untested behavior, failed requirements and the next observation needed |
| Judgment and reviewer | Self-assessment or named independent review; explain, demonstrate, transfer and scope each separately |

For a live AWS attempt, additionally identify the intended account, region, authorized temporary identity, resource boundary, estimate and price date, a run limit and credit reserve chosen for that account, stop conditions and cleanup owner before execution. Record actual usage and later billing reconciliation separately. An empty field is not approval, and the worksheet installs no spending controls. Organization-dependent work may require an account and permissions beyond a personal trial.

For a local attempt, write “no AWS resources” only after inspecting the selected exercise's purpose and code. A command beginning with `python3` can still call cloud APIs. Use [the first-exercise command guide](../docs/FIRST-LOCAL-EXERCISE.md#learn-to-classify-the-next-command).

## Worked editorial example: the forgotten experiment

This is an authored example of reasoning, not a real learner submission or an independent assessment. Its figures come from the [first local exercise](../docs/FIRST-LOCAL-EXERCISE.md), using invented rates. A reader must supply their own source revision, environment and observations; do not copy this paragraph as a claim that you ran the program.

**Requirement:** explain how duration and a credit reserve can independently prevent an experiment from fitting the plan.

**Prediction:** at $0.05 per hour, 72 hours costs $3.60 for running equipment. Adding $0.06 storage and $0.10 requests gives $3.76. Multiplying by 1.5 for the allowance gives $5.64. This exceeds an invented $4 run limit and leaves $74.36 from the fictional $80 balance, below its invented $75 reserve.

**Action to reproduce:** from the repository root, run `python3 examples/costs/lifecycle-exercise.py`. Record your own interpreter version and process result. The expected 72-hour line reports both comparisons as `False`. That is a prediction to compare with your output, not a substitute for your output.

**Explanation:** the longer duration changed the equipment term. Requests and storage were held constant in this model. The program checked arithmetic; it did not retrieve current prices, inspect credits or enforce a shutdown. If the output differs, preserve the discrepancy and identify the source and inputs before changing an assertion.

**Changed case:** ten hours gives $0.50 + $0.06 + $0.10 = $0.66; with allowance, $0.99. From a fictional $75.50 starting balance, $74.51 remains. The run passes the invented $4 comparison but fails the $75 reserve comparison. This changed case is hand-calculated in the worksheet; it is not a claim that the command executed a ten-hour test or rented equipment for ten hours.

**Cost and cleanup:** the arithmetic creates no AWS resources. Any local report or Python cache is a local artifact, not evidence of cloud deployment. Current AWS prices, account credits and actual billing remain unverified by this exercise.

**Assistance and judgment:** the example supplies the answer, so reading or copying it is assisted practice. For an unaided attempt, choose another duration and balance, preserve your first reasoning, and explain both comparisons before consulting the answer. No independent learner judgment is recorded here.

## Judge the evidence, not the appearance of success

| Entry a reader might write | What it establishes | What is still needed |
| --- | --- | --- |
| “The command exited zero” | The process reported success | Inspect which assertions ran and explain their scope |
| “I predicted failure, but both comparisons passed” | A useful disagreement between prediction and observation | Preserve both; check units and inputs, then explain the correction |
| “Codex calculated it correctly” | An assisted answer exists | Verify the arithmetic and attempt a changed case yourself |
| “I explained the reserve but have not run Python” | A design/arithmetic explanation | Execution evidence if the selected challenge requires it |
| “The local permissions test passed” | The tested local behavior | Real scoped identity and allow/deny evidence before claiming AWS enforcement |

A failed first prediction can lead to a strong learning record when the correction is reasoned and the next case transfers. Do not erase the initial answer to make the attempt look perfect. Equally, a confident explanation cannot cancel an observed privacy, data-loss or cost-boundary failure.

Ask Codex: “Read my sanitized learning record. Separate observation from inference. Ask one changed-case question without giving its answer. Do not fill in missing evidence, execute commands or assign an independent-review label.” Keep the feedback separate from your first attempt. If a human later reviews it, record that review as a new observation rather than relabeling the AI-assisted attempt.
