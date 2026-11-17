# Assessor: cancellation at a separate publisher boundary

Read after preserving an unaided attempt. These answers describe the **local fixture policy**, not a general provider guarantee.

| Order | What the workflow can say | What the provider evidence says | Next step |
| --- | --- | --- | --- |
| Cancel before worker claim | `cancelled_before_send`; this fixture rejects a later claim | No fixture effect was sent through this path | Check that other workers and paths cannot bypass the gate before making a deployment claim |
| Worker claims, cancel requested, provider commits and reply is lost | `cancel_requested` until lookup; then `completed_after_cancel` | One matching operation, digest, destination, artifact and receipt prove this fixture effect | Treat correction as a new authorized action with its own visitor check |
| Worker claims, cancel requested, one provider lookup returns no row | `cancel_requested`, outcome unknown | One absent read is not a durable negative receipt | Investigate worker state and provider lookup/consistency; do not show green cancellation |
| Provider effect is confirmed before cancellation | `confirmed`; cancel returns `too_late` | Matching effect exists | Authorize any reversal separately; do not relabel the effect as canceled |

The changed timing case matters because the worker may still have the stable operation after the first empty lookup. A later send can commit. The first honest screen can say **cancellation requested; publication outcome being checked**. A later matching provider receipt proves this fixture effect, while the visitor may still need a separate observation. A corrective publication has a new artifact, decision and operation identity; recycling the old approval would hide the change.

One negative control writes a provider row with the wrong target and digest. The reconciler reports `conflict` and preserves the cancellation request, even though a provider row exists. Another invokes the fixture provider directly after a pre-claim stop: reconciliation reports `conflict_after_stop`, exposing the bypass instead of presenting a false safety claim. An actor with no cancellation authority leaves the dispatch state unchanged. Tests do not authenticate people, prevent such outside calls, prove cross-process fairness or test a cloud callback.

Assess a response as strong only if it keeps these claims distinct: admission, local cancel request, provider effect, and visitor-visible result. A statement that “Cancel succeeded” solely because the workflow row changed or one provider lookup was empty is a material reasoning error. A correct first answer and a Codex-coached correction should remain separately labeled.
