# When a receipt outlives memory

Maya promises customer R17 that a repair appointment is confirmed. The fast worker can keep that fact in memory, but a restart clears the worker's memory. What must happen before the worker sends the confirmation receipt?

First read the [Chapter 12 authority lesson](../../reader/BOOK-LOCATORS.md#book-1a9c241595d0995a). Predict four observations: whether R17 survives record-before-ack, whether an older snapshot includes R17, whether ack-before-record survives, and whether a retry with the same operation ID creates a second record. Write your first answers before running the code.

```sh
python3 examples/in-memory-authority/lab.py
```

The script uses only Python's standard library. It creates two temporary SQLite journals, replaces each in-memory worker with a new object and database connection, checks the recovered records, then removes the temporary files. It has no network, AWS credential, paid service or retained resource. Do not run with `python -O`, which disables its assertions.

The **record-before-ack** path commits R17 to the local journal before returning its receipt. The replacement worker reads it back. The old snapshot contains R16 only, so snapshot-only recovery would still lose a confirmation. A repeat using the same operation ID and intent finds one record; changed intent under R17 is rejected. The **ack-before-record** path intentionally returns R17 while only process memory holds it. After that memory is discarded, a new worker cannot find the acknowledged R17. Compare your predictions with the [separate assessor](ASSESSOR.md) after the run.

This is an ordering and recovery model, not ElastiCache or MemoryDB. SQLite commit behavior on this machine is not a measurement of AWS Multi-AZ logs, failover time, replica freshness or service durability. The exercise does not model an authenticated caller, last-slot capacity, a second Region, an external notification or filesystem failure. For a real design, check the exact AWS service, engine version, durability mode, Region, access path, recovery procedure and full current cost before claiming that an acknowledged business action survives. This exercise does not provision either in-memory service.

**Changed case:** Suppose R17 was recorded but the network reply disappeared. The customer retries with the same operation ID and exact intent. Explain why one journal record can still exist even though the customer did not see the first reply. Then change the intent under R17 and explain why treating it as a new appointment would break the receipt's meaning. Ask Codex to name an observation that would distinguish a recovered record from a recovered customer promise; verify its answer against the actual `SELECT` result and the missing application boundaries above.
