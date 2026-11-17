# A22: a booking survives its worker

Maya sends an appointment request. The worker saves it, but Maya's browser gives up before the reply arrives. This time the operator **ends that worker process** and starts a different one. The new worker reads the same local SQLite file. If Maya repeats the same request ID, will the second worker recognize the first booking or create another?

Run from the repository root:

```sh
python3 examples/resilience-exercise/process_lab.py
python3 -m unittest discover -s examples/resilience-exercise -p test_process_lab.py -v
```

This is a local-only extension of the [one-process fault lab](LOCAL-LAB.md). It opens only an ephemeral loopback HTTP port. A temporary SQLite file contains invented bookings and is removed after the run. It does not use AWS, real customer information or account credits.

Read the receipt as a sequence, not a score. `committed_before_worker_stop` means the operator read one `fault-1` booking through a **separate database connection** after Maya timed out. The old worker is then terminated. `worker_pids_differ` shows that the retry reached a new process. The second worker returns the original booking ID, rejects the same ID with a changed synthetic customer, and handles two new probes. `fault_request_records` comes from another direct SQLite read, not the worker's health endpoint. The measured interval begins at Maya's timeout and ends at the second new response; it is one same-host timing sample, not a customer RTO.

SQLite's unique request-ID index and an immediate transaction keep the safe fixture's lookup and insert inside one database decision. The third test also races two live worker processes against the same ID and checks that both receipts name one row. A real product must choose the correct scope for a request ID, retain it for the promised retry window, bind it to the authenticated caller and operation, and decide how a conflict is returned. This fixture has only synthetic names and no authentication. Its unsafe mode removes the unique index and inserts a new row on retry. The new worker is healthy, yet two `fault-1` rows remain and `hypothesis_met` is false.

Before reading [assessor reasoning](PROCESS-LAB-ASSESSOR.md), explain these changed conditions:

1. The first worker dies **before** the database commits. What would the new worker's same-ID retry need to do? Why can Maya not choose a new ID simply because she saw a timeout?
2. The second worker has a different process ID but reads a different or stale database file. Which receipt field or additional identity check should prevent a success claim?
3. The database read shows one `fault-1` row, but the booking confirmation was also sent to an outside calendar service. Which effect is absent from this ledger? What stable operation ID and provider lookup would make reconciliation possible?
4. The unsafe mode reports two rows after restart. Does a correct new probe repair the earlier customer state? Describe the operator's next business check.
5. Two retry requests arrive concurrently at two local workers. Which part of this fixture protects the same-ID rule, and why does its green race test still not prove that a selected cloud database behaves correctly?

Ask Codex to predict both receipts before running them, then challenge its explanation with the SQLite rows and the broken-rule result. Have it name the first observation that would disprove recovery. This extension crosses a **process boundary** and persists a local record across worker replacement. It still shares one host, one SQLite file, one operator and one storage failure domain. It does not test an independent alarm, authorization, AWS FIS stop condition, network partition, multi-Region recovery or real customer time/data loss. A later AWS experiment needs scoped identity, selected-service checks, a complete estimate, account-appropriate spending and reserve limits, and cleanup evidence; see the [tabletop](README.md).
