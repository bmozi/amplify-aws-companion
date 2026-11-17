# Decide how records become useful results

These six original cases are design-only. Read [the event lesson](../../reader/BOOK-LOCATORS.md#book-f0f0044d800d44b9), write predictions, then inspect [assessor notes](ASSESSOR.md). No cloud calls, failure injection or performance measurement is performed by reading this exercise.

For each case state the business deadline, what each consumer must receive, one candidate design, its failure boundary, and the observation needed before claiming success.

1. **Morning report:** A store closes at 18:00 and needs a reconciled report by 08:00. It has no requirement for intraday decisions. The proposal creates a continuously running streaming processor because “real time is always better.” Compare with a validated scheduled batch, including source completeness and repair time.
2. **Two applications, one queue:** A dashboard and fraud analyzer read and delete messages from one standard work queue. The designer claims both applications receive all sales. Explain the difference between competing workers and independent consumer histories.
3. **Early checkpoint:** A consumer records progress through event 41 before committing its ledger change. It crashes between those writes. Predict restart behavior and what evidence is missing.
4. **Late checkpoint:** The ledger commits event 41, then the process crashes before recording progress. A restart repeats event 41. Compare an unconditional counter increment with a ledger that recognizes a previously accepted business identity and rejects conflicting content.
5. **Ordered progress, unordered completion:** Parallel processing finishes 41 and 43, but 42 fails. The controller checkpoints through 43. Explain the potential omission and a requirement for the progress or quarantine policy.
6. **Backlog arithmetic:** For five minutes, arrivals are 120 records/second and successful completion is 100. Afterward arrivals become 80. Calculate the backlog and drain time, then change the post-burst arrival rate to 100. State why these constant-rate fixtures cannot prove a real latency target or retention setting.

Transfer challenge: the fraud application now needs to recompute last week's results using a repaired rule. Identify the needed source retention, authorization, replay isolation, output versioning and cost estimate. Ask Codex to challenge whether replay could repeat customer-facing effects. Explain how you would separate a recomputed analytical result from sending a second receipt.

## Frequency, volume and freshness: a seventh case

A shop needs a report within 300 seconds of each sale. Collection occurs every 300 seconds; a batch is 30 decimal MB, sustained transfer is a fictional 10 Mb/s, processing takes 45 seconds and publication takes six seconds. Assume these stages do not overlap. Predict the delay for an event just missing collection, then reduce the interval to 180 seconds. Finally change the file to 90 MB without changing the other inputs. Explain which assumption becomes questionable if smaller intervals normally produce smaller files.

After your prediction, run this Python-only local arithmetic check from the repository root:

```sh
python3 examples/ingestion-review/check-model.py
```

No network, AWS credentials or additional packages are used. The output compares four modeled totals and rejects invalid throughput values. It is not a transfer benchmark. Explain why a modeled result under the target does not prove a production freshness guarantee, and list the timestamps and volume/throughput observations needed for an actual test. For transfer, add a 60-second retry delay to the three-minute, 30 MB case and decide whether the original promise still holds.

## Who is allowed to submit the event?

Read unit 14's “Decide who may submit a business fact.” These four additional cases are design-only. For each, separate authentication, authorization, validation and duplicate handling; identify the component responsible and the observation needed.

1. A producer legitimately permitted to write to a shared stream sends a valid JSON record labeled as another shop. The designer says IAM already checked it. Explain which permission was checked and where business scope still needs enforcement. Compare a trusted ingestion application with resource separation, including a direct-write bypass.
2. A private endpoint permits the intended writer and stream. A team declares the public route impossible without checking the identity/resource policies. Explain the missing path test and why a private address alone is insufficient evidence.
3. Two legitimate shops independently issue event ID `42`. A stranger also submits `42`, and one shop retries its original delivery. Define trusted identity scope, acceptance/denial, duplicate and conflict outcomes without treating the ID as a password. State what changes in the reconciliation manifest.
4. A repair operator needs to replay retained input into a candidate report. A proposal grants stream administration and direct access to the live customer-notification output. Design the narrower required work, output isolation, approved replay interval and tests that would expose unintended notifications or excess authority. Do not invent the exact IAM action set without checking the chosen client operations.

Transfer: the sender is compromised but still holds valid credentials. Explain why valid authentication no longer implies truthful sales. Add source reconciliation, bounded ingestion, detection and credential-response ownership, while acknowledging which fraudulent facts cannot be detected from schema alone. No live identity, endpoint, producer or replay test has been performed here.
