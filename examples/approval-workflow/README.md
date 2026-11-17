# Approval belongs to a specific action

Run `python3 examples/approval-workflow/lab.py` from the repository root. It uses Python's standard library and a temporary SQLite database; no messages, payments, deployments or AWS calls occur.

A request records its action, a digest of that action, designated reviewer, expiry and status. The synthetic action names a fixture artifact and target. The executable verifies that execution without approval fails, the wrong reviewer fails, a mismatched reviewed digest fails, duplicate approval is harmless, changing the target fails, and approval cannot be used to start a new effect at or after expiry.

The effect and its receipt are rows in the same SQLite transaction. A replay after execution returns the existing result rather than creating another effect, even after the approval window closes. This permits receipt lookup; it does not grant renewed authority. An external cloud API, email or payment would not share this transaction and needs its own idempotency/reconciliation design.

Identity and time are trusted test inputs. The code does not authenticate a human, create callback tokens, verify current membership or perform real workflow orchestration. A SHA-256 digest binds the reviewed JSON fields; it does not prove the reviewer understood them or that omitted fields are safe.

The fixture now permits the designated reviewer to cancel pending or approved requests, including an expired approved request. Repeating cancellation returns `duplicate`. A late approval and a later execution cannot reactivate a cancelled request. Cancellation after committed execution returns `too_late` and preserves the existing effect and receipt. These are explicit fixture policies, not universal workflow semantics.

Before running, predict the state and effect count for cancellation-before-approval, approval-then-cancellation-before-execution, and execution-before-cancellation. The program checks these controlled serial orders in the real SQLite database and verifies the final rows. The additional contention cases release two threads through a barrier, each using its own SQLite connection. They do not interrupt an external worker or cancel an external operation. Connections are explicitly closed before temporary-directory removal.

Challenge: give the requester cancellation authority without approval authority. Identify every permission check that changes and retain the wrong-actor cases. Then add two-person approval with distinct reviewer identities and explain whether either reviewer may also be the requester. Ask Codex to find an omitted action field that could change the consequence without changing the approval record.

Read [the human-approval lesson](../../reader/BOOK-LOCATORS.md#book-842e431cbcce6c95) and revisit A24. Neither this fixture nor its passing assertions establishes an AWS workflow or an external exactly-once guarantee.

For the separate-provider boundary, first use the [lost-reply publication drill](EXTERNAL-EFFECT.md), then the [after-dispatch cancellation drill](EXTERNAL-CANCEL.md). The latter keeps `cancel_requested` distinct from an observed provider effect and includes an outside-send bypass as a negative control. Preserve an unaided timeline before opening its [assessor](EXTERNAL-CANCEL-ASSESSOR.md).

## When two callers arrive together

The `overlapping_callers` report adds three pairs: approval/cancellation, execution/cancellation, and two executions. A barrier makes both callers ready before they attempt their operations. It does not choose which acquires SQLite's write transaction first. Do not copy one observed tuple as the only correct output.

| Pair, in reported order | Accepted result pairs | Required stored result |
| --- | --- | --- |
| Approval, cancellation | `approved, cancelled` or `rejected, cancelled` | Cancelled request; no effect |
| Execution, cancellation | `executed, too_late` or `rejected, cancelled` | Executed with one effect, or cancelled with none |
| Execution, execution | One `executed`, one `duplicate` | Executed with exactly one effect |

The checks read committed request states and effect rows after both callers finish. A successful cancellation must never coexist with an executed fixture effect for that request. Unexpected exceptions fail the run; only the specified state-rejection errors become `rejected`. Barrier/future and database-lock waits are bounded. Existing controlled-order cases still establish both execution/cancellation orders; one overlapping run need not observe both.

This is local contention evidence for these operations and fixtures. SQLite serializes the write transactions. It does not establish fairness, throughput, process-crash recovery, a network service's delivery semantics or a cloud database's isolation behavior. A provider API outside the transaction remains outside this guarantee.

## Design the two-reviewer extension

Use the [two-reviewer challenge](TWO-REVIEWER-REVIEW.md) and preserve your initial answer before opening its assessor guide. This gives explicit policy and acceptance criteria for the extension proposed above. The original `lab.py` remains single-reviewer. After the design attempt, the separate `two_reviewer_lab.py` demonstrates local admission rules; it does not publish externally or implement a complete two-reviewer service.
