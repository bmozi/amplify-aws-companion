# A02 index migration changed cases

Try each case before reading the criteria. Use `cutover.py` with a copied `cutover-case.json`; do not edit the reference file just to make a gate green.

1. The index is `ACTIVE`, two complete base scans match the index, but one old request has the wrong type for the proposed index key. What can the operator claim?
2. Two `ACTIVE` windows show no missing request IDs, but the second base scan stopped after a page whose filter returned no rows and still had a cursor. Does the comparison support a pilot?
3. A clean pair of windows has a reviewed estimate of index storage and query reads, but no named person owns the daily reconciliation. Is the lower read count enough?
4. A pilot has begun. A request accepted one second ago is not yet in the index. What path finds it before the customer's one-hour contact promise expires? What happens if the index never catches up?

## Assessor reasoning

1. Keep the scan. An `ACTIVE` index can omit an item with a key-schema violation. Investigate and resolve the item, then obtain new evidence. A status read is not coverage proof.
2. Keep the scan. An empty filtered page with a cursor is not a complete pass. The local input must set `scan_complete=false`; the program refuses to treat the missing-ID set as sufficient evidence.
3. Keep the scan. The estimate and observed reads answer different questions from who will notice and repair missing work. Assign and exercise ownership before a bounded pilot.
4. A base-table reconciliation or independently durable pending-work source must cover missing index entries. A query cannot reveal an item it did not return. Base rechecks and final conditions protect against stale candidates and races, but they do not discover an absent candidate. Select a cadence and response that meet the business deadline; this toy program cannot prove one-hour human contact or DynamoDB propagation bounds.

For each answer, ask Codex to identify the claim the current evidence supports, the next observation needed and the cost of leaving the full scan as a fallback. Reject an answer that treats two clean fixture windows as a service guarantee or recommends installing the index without the live cost, credit, identity and cleanup checks.
