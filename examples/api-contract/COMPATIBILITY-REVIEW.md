# Yesterday's client meets today's server

This original design exercise complements the [receipt lab](README.md) and [database-schema exercise](../schema-compatibility/README.md). It concerns a response consumed by software outside the server's release. No API Gateway, client update mechanism or version router is implemented here.

The fictional original response is `{"request_id":"R17","state":"accepted"}`. The old client requires both fields and recognizes accepted, completed and rejected. A second client also rejects every additional field. A proposed prepared client tolerates additional response fields and shows a non-success message for unknown states while preserving the operation ID for recovery. All identifiers are fictional.

Before running the script, predict each client's response to four server representations: the original, an added optional `status_url`, renaming `request_id` to `id`, and a new `inspection_required` state. Then answer:

1. Is adding a response field compatible with every installed client? What observed client behavior would support the claim?
2. Can the prepared client safely complete the business workflow when it receives an unknown state, or does it merely avoid a false success?
3. Could a server keep the original representation on one supported contract while offering a new representation to explicitly upgraded consumers? Compare this with changing the representation for everyone. Include testing and retirement costs.
4. An offline mobile client returns after the planned retirement date. What happens to its unresolved request and retry key? Do not silently create new work as a substitute for locating the original.
5. A new server has already produced records with the new state. Is restoring the original consumer a safe rollback? Explain the evidence needed to define a usable rollback target.
6. A request gains a mandatory `branch_id`. Why is this a different compatibility direction from adding an optional response field? What business meaning would an omitted value have, and who can authorize that default?

Run `python3 examples/api-contract/compatibility_lab.py` from the repository root without `-O`. It serializes real JSON bytes and runs three miniature consumers against four representations. A deliberately unsafe consumer reports unknown states as completed. The script demonstrates that defect and an old-consumer rollback failure. It has no HTTP transport, persisted records, real clients, authentication or release controller. Passing its matrix does not inventory installed consumer versions or prove application usability.

Ask Codex to enumerate request and response compatibility separately, then challenge every proposed default with a business counterexample. Require fixtures for the exact older client behavior rather than a newly written client that happens to accept the new response. Keep production payloads and credentials out of shared examples.

## Assessor reasoning — read after responding

1. The legacy fixture ignores the added field, but the strict fixture rejects it. “Additive” describes the JSON change, not evidence of every consumer's behavior. Verify supported client implementations and generated validators.
2. The prepared client preserves identity and avoids falsely announcing completion. It cannot interpret the new state's required action. A supported status/recovery experience and escalation path remain necessary.
3. Parallel explicit contracts can preserve older behavior while new clients adopt new semantics, but add routing, documentation, authorization consistency, monitoring and retirement obligations. Neither a version label nor a new path proves compatibility. Do not translate a safety-critical new state into an old success merely to keep a response parseable.
4. Publish the supported lifetime and retirement behavior, measure usage where possible, and retain an authorized reconciliation route for unresolved operations according to policy. Absence of recent traffic does not prove an offline client has disappeared. Contract retirement and retry-record retention must be considered together.
5. The old consumer cannot interpret the new state in the fixture. A prepared consumer may be a valid rollback target only if the full required behavior is verified; its generic fallback alone does not establish service restoration. Account for already-written data, queued messages and older clients as well as the server binary.
6. Old request producers do not send the mandatory field. The receiving server must either support the old input under an explicitly correct default, negotiate a supported new contract, or reject it through a documented transition. Guessing a branch can change ownership, routing or physical fulfillment. Tolerance of extra response fields gives no permission to accept arbitrary unvalidated request fields.

Assess preserved meaning, mixed-version evidence, unresolved outcomes, retirement and recovery. These practice cases do not produce a certification score.
