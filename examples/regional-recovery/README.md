# Regional recovery review: reopening is a data decision

This is an original fictional tabletop exercise for [the recovery lesson](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d). No regional environment is deployed, no time below is measured, and no AWS service is assumed to implement the described behavior automatically.

For a separate **measured same-host** exercise, use the [customer failover clock](TIMELINE-LAB.md). Its loopback HTTP record puts distinct timestamps on failure, reconciliation, route change and first correct read; the open-writer changed case has no recovery endpoint. Those local milliseconds do not replace this tabletop's multi-Region analysis or establish an AWS RTO.

A booking company operates in Region A with an asynchronously updated recovery copy in Region B. Its fictional objectives are to restore useful booking service within 30 minutes and lose no confirmed bookings. The recovery team initially knows the following:

| Time | Observation supplied by the exercise |
| --- | --- |
| 09:58 | B's reconciliation receipt includes confirmed booking IDs 101–110 with matching values. |
| 10:00 | A confirms booking 111. No receipt proves that B contains it. |
| 10:01 | The office loses access to A. This does not establish that every client or worker has lost access. |
| 10:04 | B's application health endpoint returns 200. The recovery operator cannot yet access a required decryption key. |
| 10:08 | A remote worker reports that it can still reach A. Its write permissions have not been fenced. |
| 10:12 | A separately retained business journal is recovered and contains the confirmed values for booking 111. |

Before reading the assessor notes, write a decision record for each stage. State what is known, what is unknown, whether new writes may begin in B, the minimum next evidence, and who owns the decision. Do not invent successful fencing, key access or journal replay.

Then evaluate these changed scenarios independently:

1. At 10:15, approved reconciliation has restored IDs 101–111, operator key access is tested, and a verified mechanism prevents A's old writers from committing. A representative booking and tenant-denial check pass in B. Which additional capacity/dependency checks remain before reopening? What interval would you measure?
2. After reopening, B confirms booking 112. A later becomes reachable but contains only IDs 101–111. Someone proposes moving DNS back to A immediately.
3. A faulty release changes a booking amount, and the same changed value appears in both Regions. Both health endpoints return 200.
4. The independent journal never becomes available. B still proves only IDs 101–110, and a customer presents a confirmation for 111 without enough trusted details to recreate the full record.
5. The secondary's application is correct for ten requests but cannot sustain the business's stated recovery workload.
6. The recovery operator normally authenticates through a service in A, which is unavailable during the incident.

Produce two architecture options for the original requirements, with data authority, source-of-truth evidence, dependencies, recurring cost categories, recovery procedure, failback procedure and unresolved assumptions. Compare the effect of relaxing the no-loss requirement rather than silently relaxing it inside the design. Include a declared test boundary and cleanup inventory for any future authorized rehearsal.

This exercise does not authorize multi-region deployment, account creation or a paid-plan transition. Choose whole-run spending and reserve limits from your account terms. A realistic continuously running regional standby may not fit that experiment budget.

[Assessor reasoning](ASSESSOR.md) is separate so learners can predict first. The criteria and fictional observations have not been independently assessed with learners.


## Strategy-selection extension

Answer before consulting the assessor notes. These cases are independent of the clock in the original regional incident.

1. A recovery location has replicated data and core infrastructure, but application workers must be created before it can serve a booking. Distinguish this from an already functioning reduced-capacity application. State one observation that would confirm the claimed readiness.
2. In the lesson's fictional sequential rehearsal, detection/decision takes 4 minutes, target preparation 12, reconciliation 6, application/access checks 3, and client transition/verification 2. Compute total time against a 20-minute objective. Recompute with a prepared candidate that reduces only target preparation to 2 minutes. Does either calculation establish RPO?
3. Both locations already serve bookings, but each can handle only half the normal total demand. One disappears. Explain why the active/active label does not establish surviving capacity or correct last-seat handling.
4. The prepared candidate restores service quickly but reproduces a corrupted booking. Propose the additional recovery evidence needed and identify which earlier timing assumptions must be reconsidered. Explain how a requirement to restore only one tenant changes the acceptance check.

These are design assessments, not instructions to create recovery resources. Compare the strategy's normal recurring costs and the rehearsal's incremental costs separately before any later authorized experiment.

## Professional recovery choice

These independent cases extend the [recovery lesson](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d). For each, record the customer operation, RTO/RPO, data authority, dependency and capacity evidence, estimated steady and rehearsal cost, stop condition, and the first test that could disprove your choice. Read the [assessor reasoning](ASSESSOR.md#professional-recovery-choice-reasoning) only after answering.

1. A licensed parts server has installed software and local files that take a day to rebuild. The business needs the lookup restored in two hours. Its separately managed orders database has a tested 45-minute restore, but no one has timed the joined application path. Compare AWS Elastic Disaster Recovery (DRS), rebuilding the server and restoring data, and a running warm standby. Identify which components each option actually protects and the rehearsal evidence needed. Include ongoing replication/staging and drill costs for DRS.
2. A recovery location has one ready worker with **assumed** useful capacity of 300 requests/s. Demand is 600. A larger compatible worker is assumed to serve 650 but takes 16 minutes to replace and validate; two more 300-capacity workers can be ready in six minutes. The recovery deadline is 12 minutes and the database limit is 700. Which scale choice can plausibly meet the deadline? Recalculate after an AZ containing two of the three small workers fails. State what load test and dependency checks could overturn the arithmetic.
3. Change only the database limit in case 2 to 450 requests/s. Does adding a fourth worker fix the customer promise? Give a suitable degraded-service decision if the business permits one; otherwise name the unmet requirement. Do not invent a quota or database upgrade.
4. The warm standby passes its health endpoint but the newest confirmed order is absent from its asynchronous copy. An automatic traffic switch is proposed while an old writer can still commit in the source Region. Run the [local recovery gate](../recovery-automation/README.md) with corresponding inputs and explain its decision. State which independent reconciliation and fencing observations would permit a new evaluation; a model result is not a live AWS cutover.
5. Both Regions agree on a corrupted order total. A retained historical backup predates the error but also predates legitimate new orders. Explain the restore, replay and external-effect reconciliation needed before reopening, and why the recovery clock may change.

The figures and times are fictional design inputs. This packet does not launch DRS, Auto Scaling, a database or a regional standby. Choose whole-run spending and reserve limits for the account you will use.

## Walk a customer through the recovered shop

Run `python3 examples/regional-recovery/customer_path_lab.py` from the repository root, then `python3 -m unittest discover -s examples/regional-recovery -p 'test_customer_path_lab.py' -v`. The program uses only Python's standard library. It starts a loopback HTTP server and two temporary SQLite databases; both close and the temporary directory is removed. It makes no AWS calls and creates no billable resource.

Imagine a shop that copied its booking book after confirming booking 110. The main shop then confirmed 111, but the copy never received it. The main shop becomes unreachable to our local visitor. Predict the first three receipts **before** running:

| Observation | Expected result | Meaning |
| --- | --- | --- |
| `GET /candidate/health` | HTTP 200 | The candidate handler responds; its data may still be wrong. |
| `GET /bookings/111` on the current customer route | HTTP 503 | The route still points to the unavailable source. |
| Candidate comparison with the fictional confirmation journal | Booking 111 missing | Reopening on the candidate would hide confirmed work. |

The operator first tests a fictional key-access flag, stops the cooperative old writer, replays **only** the known missing 111 from the separate journal, and checks exact IDs and amounts. The switch then points the local customer route to the candidate. `GET /bookings/111` returns its 2,300-cent confirmed value; `POST /bookings` confirms 112 for 900 cents; a follow-up GET reads 112. A proposed return to the old source is refused because it lacks 112. Nine focused tests include missing/changed data, absent key or fence, premature writes, duplicate booking, direct-SQL bypass, the full HTTP path, a pinned old-endpoint read and the redirect gate.

The journal is supplied by the exercise; it is not authenticated, independently secured or a real capture stream. The key and writer-stop flags are cooperative application variables, not KMS policy tests or a distributed fence. An uncooperative direct database writer could bypass the flag. The HTTP route is a process variable, not DNS, CDN or cached-client behavior. The local run does not measure regional RTO/RPO, capacity, tenant isolation, external payments or notifications. Those claims still need separately designed and authorized evidence.

Answer before opening [the assessor](ASSESSOR.md#customer-path-changed-cases):

1. Booking 111 is in the journal, but its amount differs from the candidate's row. Should replay overwrite it, reopen, or stop? What evidence identifies the correct amount?
2. The candidate is exact, but one old source worker still writes after the route changes. Which promise can the local flag no longer support? What would a real writer-fence test need to observe?
3. The journal is unavailable. The candidate is healthy and contains 110. Can the operator claim zero confirmed-work loss?
4. Booking 112 succeeds in the candidate. The source returns and a teammate moves customers back immediately. Which observation rejects that move?
5. Ten requests succeed after cutover but the normal peak is 600 requests/s. What remains untested before a capacity claim?
6. A customer already has a cached source address. Why does the program's single route variable fail to describe that customer?

Ask Codex to trace each claim to a receipt, then have it propose one missing dependency and one falsifying observation. Check its explanation against the returned HTTP statuses and rows. The [Unit 07 lesson](../../reader/BOOK-LOCATORS.md#book-5236b2630bdb4f13) connects this concrete path to the larger recovery runbook. Choose whole-run spending and reserve limits for the account you will use.

## The old door can open again

The same loopback run now lets the old source endpoint respond *after* the current route has moved to B and accepted booking 112. Look at `pinned_client_after_old_endpoint_returns`: a customer following `/bookings/112` gets HTTP 200 from B, while a deliberately pinned client using `/pinned-source/bookings/112` gets HTTP 404 from A. The pinned client can still read old booking 111, which makes A look healthy enough to mislead someone. The [two-path figure](../../book/figures/recovery-pinned-client.svg) maps the two reads to different books. The eighth focused test holds the route on B while these different answers appear.

Predict the two responses before running the lab, then decide what the business may claim about reopening. Compare (a) keeping A unavailable, which leaves a pinned customer unable to reach a booking, with (b) a controlled read-only old endpoint that helps the customer reach B. The second option now has a **local redirect model**: once A is reachable, the selected route points to B, the cooperative old-writer flag is off, B is healthy, and B contains the requested booking, `GET /pinned-source-bridge/bookings/112` returns HTTP 307 with `Location: /bookings/112`. A client that follows reads booking 112 from B with HTTP 200. A client that does not follow sees only 307; when B is unavailable, the bridge returns 503. The bridge rejects unknown booking IDs and nonnumeric paths. It accepts no POST. This is a logical second path on one loopback server, not a deployed redirect on a real old host.

```text
Pinned client -> old A path -> 307 /bookings/112 -> selected B -> 200
                  |               |
                  |               +-- client refuses redirect: stops at 307
                  +-- B unavailable: 503, no recovered-service claim
```

Before reading the output, predict what a nonfollowing client and an unavailable B observe. Then change `source_writable` to true before calling `bridge_target`: why must the local gate refuse even though one HTTP read might work? The guard is only a cooperative variable; direct SQL can still bypass it. Real use would also need verified identity and authorization, redirect/retry and method behavior for representative clients, a genuine old-endpoint routing plan, continued monitoring and cost, and a tested writer fence. Neither option makes immediate failback safe while A lacks 112. Ask Codex to explain how it would detect clients still reaching A and falsify the claim that every customer sees the same confirmed bookings. Check the answer against the local HTTP responses before reading the [assessor](ASSESSOR.md#pinned-client-reasoning).

The fixture uses an explicit second HTTP path, not DNS caching, a cached connection, regional routing or a distributed writer fence. A real cutover would need representative old and new clients, a supported endpoint transition plan, old-writer denial, customer read/write checks, reverse reconciliation and measured timing. Choose whole-run spending and reserve limits for the account you will use.
