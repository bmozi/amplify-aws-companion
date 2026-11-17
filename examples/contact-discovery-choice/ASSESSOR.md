# Assess the A02 contact discovery decision

Ask the learner to run `lab.py case.json`, then change the case: 20,000 unrelated table items, 30 contact checks during one exercise, five newly accepted requests per minute and a ten-minute interruption in the index reader. They must choose an initial discovery path and an escalation/reconciliation plan, not merely name a service. Treat the counts as invented workload facts; require current regional prices and item sizes before any live-run estimate.

A defensible response should:

1. Explain why `FilterExpression` cannot make the existing full-table scan cheap and why `Limit=20` is a page bound, not a whole-run read or price cap. Include every cursor and repeat pass.
2. Describe a proposed sparse-index key and why pending-to-contacted transitions add base-table and index work. Price index write/storage, index queries, base reads and transactions alongside existing queue/Lambda/log/cleanup meters. Consider migration/backfill and key distribution.
3. Recognize both index error shapes in the fixture: missing R1 and stale R2. Read the base record before acting on a candidate, recheck the final write condition, and independently reconcile missed work. State who sees a persistent overdue item and how missed checks are detected.
4. Keep the customer promise separate. A scheduled checker plus index does not establish human contact, a strict one-hour deadline, notification delivery or a verified operator response.
5. Leave the live choice pending until the exact account/Region, scoped identity, measured or bounded workload, applicable credits, current full-run price, account-appropriate run limit and credit reserve, stop and cleanup plan are reviewed. The paper question does not need a new index merely to answer this design question.

**Codex exercise:** “Compare the current A02 `check_contact_due` scan to a proposed sparse due index for the changed case. Trace what happens when a due request is absent from the index, a contacted request remains in it, and a contact arrives between a base read and the final write. List every cost and operational meter you would verify. Cite the source and AWS documentation, and distinguish this fixture from live service behavior.” The learner should challenge Codex's answer with R1 and R2 before accepting a design. Agreement between an AI answer and the fixture is not independent AWS or learner evidence.
