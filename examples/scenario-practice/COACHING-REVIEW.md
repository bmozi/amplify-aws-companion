# Audit an AI tutor without surrendering the first answer

This original fictional packet accompanies [Unit 34](../../reader/BOOK-LOCATORS.md#book-c1f601e7d3ee86b5). It uses no AWS account or paid model. Read the transcript below, write your own diagnosis, then open [the assessor reasoning](COACHING-ASSESSOR.md). It is an authored exercise, not an actual Codex conversation, learner result or certification question.

Maya's repair intake promises two things: a caller receives **Accepted** only after the request is in durable, recoverable state; and the repair worker may later retry a supplier call without creating a second customer order. The supplier may be unavailable for several minutes. The question asks which of two proposed flows better satisfies the supplied promise, and what proof is still needed.

- **Flow A:** return **Accepted** from the web worker immediately, then try to place the request in a worker-local memory list. The worker may restart before writing it elsewhere. On supplier failure, the browser retries the whole request with a new request ID.
- **Flow B:** validate the caller, write the request with a stable caller-scoped operation ID to a durable queue or store, and only then return **Accepted**. A worker retries the supplier call under that operation ID and reconciles an uncertain supplier result before completing the order. The exact store, authorization and supplier behavior are not yet implemented.

The following fictional exchange is a **bad tutoring sequence**:

> Learner: “Give me a hint. I have not chosen yet.”
>
> Assistant: “Choose B. A queue always guarantees exactly-once delivery, so the supplier cannot get two orders. You have mastered this topic.”
>
> Learner: “I guess B, because queues are reliable.”

Before reading the assessor, answer these questions in your own words:

1. Which part of the assistant's timing destroyed an independent first attempt? What can still be learned from this exchange, and what cannot be inferred about the learner?
2. Which supplied facts directly undermine Flow A? Which *additional* conditions must be implemented and tested before Flow B can fulfill both promises? Do not import a generic “queue equals exactly once” slogan.
3. Rewrite the learner's request to Codex so it waits for a choice and explanation, critiques one assumption, asks for a changed case and does not award a mastery label. State where you would check any service-specific claim.
4. **Change the business promise:** the caller may receive **Pending** immediately, but **Accepted** must still mean durable capture. The supplier now offers no lookup by operation ID, and repeating a call might create another order. Which wording or workflow may change? What uncertainty cannot be erased by retrying blindly?
5. Fill the relevant [learning-record fields](../../curriculum/LEARNING-RECORD.md): first answer, assistance, corrected explanation, changed-case answer, evidence still missing and scope. If the first answer was contaminated by the hint, say so rather than inventing an unaided response.

For transfer, ask Codex to generate a *different original case* about a failed release or stale cache, but keep its rationale hidden until you submit your own answer. Check the generated scenario for sufficient facts and a defensible key before using it. Ask for one counterexample to your reasoning, then explain the revised decision without the assistant. A generated case is not an official AWS question or a calibrated measure of exam readiness.
