# Decide which part of an incident is actually finished

Maya's booking dashboard turns green. A booking accepted before the alarm is still waiting for confirmation. The green tile can be true while the customer promise remains broken. This exercise makes you check two finish lines separately: **customer recovery** and **operations handoff**.

From the repository root, predict the two printed cases before running:

```sh
python3 examples/operations-closure/lab.py
python3 -m unittest discover -s examples/operations-closure -p 'test_*.py' -v
```

The local model receives preselected fictional account, Region, journey, probe, accepted-work and alert-delivery records. It will call a customer path recovered only after two distinct recent successful journey checks and reconciliation of every stipulated accepted request. A green alarm alone cannot satisfy either requirement. It calls the operations handoff complete only after customer recovery, a named owner, a current `OK` alarm and acknowledged delivery for each distinct fictional transition. Two attempts for the same transition are not two new incidents; a later transition with a new ID remains separate work.

Change one condition at a time: make the latest probe old, give both probes the same run ID, move one probe to another Region, leave the booking unfinished, omit an accepted booking from the work export, fail the alert delivery, or add a new unacknowledged alarm transition. Before opening [assessor notes](ASSESSOR.md), write which finish line changes and what read-only observation would settle the uncertainty. Then compare the [illustrated lesson](../../reader/BOOK-LOCATORS.md#book-3ccf3fa7b7378fbc) and [figure](../../book/figures/operations-two-finish-lines.svg).

The `accepted_ids` set is stipulated as an independently checked intake ledger. A real system must establish its completeness and join it to durable work and external effects. The model has no authentication, authorization, telemetry ingestion, EventBridge delivery, CloudWatch alarm evaluation, durable alert outbox, concurrency, customer traffic or actual operator acknowledgment. Its five-minute freshness window and two-probe rule are invented teaching choices, not AWS defaults or production service-level objectives. A local `acknowledged=True` is only a fixture fact; it does not prove a human received a notification. No AWS credentials, resources, recipients or charges are used.

If Codex helps, give it only these fictional records. Ask it to separate directly observed facts, stipulated inputs, proposed interpretations and the next falsifying check. A generated incident summary is a draft for human review, not authority to run a remediation. A future live experiment still needs a scoped non-root identity, a complete estimate against spending and reserve limits chosen for the account, a selected Region and cleanup evidence. Organization-wide collection remains design-only in this packet.
