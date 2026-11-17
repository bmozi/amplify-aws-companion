# When two good checks cannot both be right

Maya has eight fictional capacity units left. Two teams each need six. Both look at the same snapshot and both receive a green answer. The question is what happens **after** the answer but **before** either team obtains the units.

Read [Chapter 22's stale-check lesson](../../reader/BOOK-LOCATORS.md#book-fe1bf84a91cdb675) and case 5 of the [capacity review](../capacity-review/README.md). Predict the printed results before running:

```sh
python3 examples/quota-race/lab.py
python3 -m unittest discover -s examples/quota-race -p 'test_*.py' -v
```

The standard-library lab creates a temporary SQLite file. It starts with a **fictional limit of 20** and **12 units used**. A and B each read the same eight-unit headroom and each asks for six. Both preliminary checks pass. If they both act only on that old reading, total demand becomes 24. A shared conditional update instead accepts one six-unit reservation and rejects the second, leaving 18 used and two free. The test starts two local workers from separate database connections and checks that exactly one reservation succeeds.

There is a second trap. Imagine team C claims the last two local units and the reply disappears. A new request under a new ID could claim something else later; repeating the **same ID and same amount** retrieves C's saved decision without adding to use again. Reusing the ID with a different amount returns `conflict`. A denied intent remains denied under its original ID even if someone later raises the fictional limit; a changed plan needs a new ID and review. The `requests` table and capacity update commit in one local SQLite transaction. This is a model of an accountable retry, not an AWS reservation API.

Before reading the [assessor](ASSESSOR.md), answer these changed conditions:

1. A third team asks for two units after the first six-unit reservation. Does the shared record fit it? What must still be checked before an actual deployment?
2. Another application creates a resource without using this local record. Can this record still prove the AWS account has two free units? Identify the boundary it does not control.
3. The second team's request is denied by the shared record. Should it retry the same six units immediately, choose a three-unit replacement, or pause? Include Maya's minimum serving capacity, rollback and the evidence each choice requires.
4. The local record accepts a request, but the provider returns a capacity error. Which earlier claim remains true? Which customer and cleanup claims are still unproved?
5. C's local reservation succeeds, but the reply is lost. What must C repeat to recover the saved result without claiming another two units? If C changes from two to three units, should the same ID be accepted? What still has to be reconciled with the actual provider?

Ask Codex to draw a timeline with the read, competing change and conditional update. Make it label the local coordinator, actual account quota, available provider capacity and customer readiness separately. Check its arithmetic and do not let a green local result stand in for an AWS response.

The file and numbers are invented. SQLite serializes only participants that use this file; it does not contact Service Quotas, EC2 or a deployment API, reserve provider capacity, grant IAM permission or prove a recovery Region can serve customers. This lab uses no AWS credentials and spends no credits.
