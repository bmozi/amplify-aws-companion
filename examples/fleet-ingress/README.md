# A09: follow a van reading into a useful report

Read [the fleet lesson](../../reader/BOOK-LOCATORS.md#book-761da2059236b662). Draw the path before looking at [assessor notes](ASSESSOR.md). This is fictional design and arithmetic. It creates no AWS resource and has no device certificate, IoT policy, stream, customer data or cloud charge.

The modeled fleet has three vans. Each reading is supposed to identify its device, event and occurrence time. The dashboard needs a warning within five minutes, and an analyst must replay yesterday's data. Predict whether total write capacity alone answers the burst question, then run:

```sh
python3 examples/fleet-ingress/lab.py
```

The invented interval lasts 120 seconds. The three rates are 70, 10 and 10 records per second. For this arithmetic **only**, one user-managed key can carry 50 records per second, aggregate intake can carry 100 and the consumer completes 60. Predict the hot key, offered records that cannot enter under the toy limits, and backlog created from admitted records before reading output. Unadmitted records are **unresolved upstream**, not assumed lost. The model does not hash keys into actual shards, emulate IoT or account for retry, bytes, rule limits, billing or delivery latency. Do not substitute its numbers for AWS service quotas.

## Follow one delayed reading into the maintenance ledger

The capacity model cannot tell whether a reading becomes an accepted business fact. Predict three outcomes first: what an empty window means while van 17 is disconnected, whether a late 85°C observation belongs to the earlier six-minute window, and whether a second arrival of that same event raises its count. Then run the separate in-memory SQLite fixture:

```sh
python3 examples/fleet-ingress/reading_ledger.py
python3 -m unittest discover -s examples/fleet-ingress -p 'test_*.py'
```

Six expected readings have occurrence seconds 0, 60, 120, 180, 240 and 300, but arrive after second 600. The report begins `unknown` against its invented expected-ID list. After five arrivals, the missing `e5` stays visible even though the high observed value already requires a warning. The sixth completes **that list**, not physical proof that every actual reading was captured. An exact replay is counted once. A replay with a changed temperature is rejected for investigation. Van 18 may legitimately use the same local event ID because identity is scoped by device.

An empty expected-ID list also stays `unknown`: absence of a plan is not evidence that the van was supposed to be silent. This fixture rejects event times later than arrival rather than modeling clock skew; a real design needs an explicit skew rule and quarantine path. Its integer temperature type check is not a physical-plausibility test.

Try changing the trusted fixture device from `van-17` to `van-18` while leaving the message's claimed `device_id` unchanged. The acceptance boundary must reject the mismatch without adding a van 17 or van 18 reading. Explain why the `trusted_device` function argument is only a test stand-in: no certificate, connection or topic-policy check produces it here. The invented expected-ID list can omit a real physical observation, and one valid credential can still lie about temperature. Record who would investigate each unresolved condition before calling the dashboard safe.

The two local fixtures answer different questions: `lab.py` models offered versus admitted work and backlog under toy limits; `reading_ledger.py` models sequential acceptance and an event-time report. Neither joins a real stream, provides durable delivery across process failure, authenticates a device, enforces an AWS policy, establishes a live quota or measures AWS cost.

The first ledger returns a rejection reason but does not persist a quarantine record or notify an investigator. A real design needs an owned, access-controlled reject path with bounded retention and repair rules; never call a rejected event resolved merely because the accepted table stayed clean.

## Keep the failed reading available for repair

The first ledger above teaches acceptance but its rejection is only a return value. Run this second local drill to see two distinct operator issues:

```sh
python3 examples/fleet-ingress/failure_journey.py
python3 -m unittest discover -s examples/fleet-ingress -p 'test_*.py' -v
```

The script supplies both the device context and the forwarding result. It puts one invented reading in a **forwarding-failed** inbox and a second, falsely claimed reading in a **business-rejected** inbox. Neither reaches the accepted ledger. It closes and reopens its temporary SQLite file; both issues remain. A fixture reviewer supplies a source note and retries only the first. That reading becomes accepted once, while the false claim remains open and the report still shows a missing expected event. The file is deleted at the end. Tests also refuse an altered delivery ID, a second retry and a conflicting replay; an injected receipt-write failure rolls back the accepted reading in the same local database transaction.

This models a distinction, not AWS infrastructure. AWS IoT [error actions](https://docs.aws.amazon.com/iot/latest/developerguide/rule-error-handling.html) respond to rule-action activation problems; they do not validate downstream business content. An actual design needs a protected error destination, permitted role, alarm, bounded retention, access review and a documented repair owner. A Kinesis write can also partially fail per record in a batch; inspect each [PutRecords response](https://docs.aws.amazon.com/kinesis/latest/APIReference/API_PutRecords.html) before acknowledging a producer batch. The local script has no IoT rule, stream, certificate, real principal, parallel consumer or crash-between-services test. A nonempty reviewer string is a teaching placeholder, not authorization. Do not put customer payloads or credentials into an unrestricted log simply to retain failures.

Changed case 7: A rule-forwarding failure is retried after inspection and its record appears in the accepted ledger. Another message reached the stream but claimed the wrong device. The dashboard's report is still `unknown`. Which issue can be closed, which cannot, and what evidence would you need before declaring the van's six-minute window complete? Then suppose the retry's receipt write fails after the local ledger insert. Predict the test result and explain why the same assertion would require a different design across AWS services.

Answer each changed-condition case with an owner, a failure signal, what receipt counts as business acceptance and what would need live verification:

1. Van 17 publishes `device_id: van-18` inside valid JSON. Its own credential and topic are otherwise permitted. Where must the mismatch be rejected? Would an IoT connection receipt prove the reading belongs to van 18?
2. The IoT rule's stream write fails. Name the separate IAM role, the error path, the missing business receipt and the person who repairs or replays the gap. Then change the failure to a malformed but successfully forwarded temperature and revisit the reject point.
3. The total modeled rate is below 100, but van 17 alone exceeds 50. Explain why adding capacity elsewhere does not automatically split one user-managed partition key. Compare keying by device, spreading records without related order, and a deliberately changed per-device ordering requirement.
4. A van sends six saved readings after reconnecting, and another repeats the same event ID with changed temperature. State occurrence versus arrival time, duplicate versus conflict, and what a provisional dashboard may change. A zero-reading gap is not proof of a safe temperature.
5. An alert consumer falls behind while the analyst continues. Specify separate progress and retained-history requirements. Under the toy caps, distinguish the 2,400 offered records that did not enter from the 1,200-record consumer backlog. Calculate whether a 60/second consumer can drain that admitted backlog if new valid traffic remains at 60/second. Change arrivals to 30/second and calculate modeled drain time. Who owns the unresolved upstream records?
6. A valid device key is copied by an attacker. Explain why schema validation and a narrow topic policy do not establish physical truth. Define revocation, investigation and reconciliation evidence without claiming every fabricated reading can be detected.

Ask Codex to review your diagram for a boundary where an untrusted payload becomes trusted device identity, and for an outcome labeled “delivered” before a consumer has accepted it. Check every proposed fix against the stated facts and the official sources in the lesson. Before any live version, verify the selected account's identity, plan and credit terms, regional prices, and a whole-run estimate against limits chosen by that account's owner. This exercise does not authorize provisioning.
