# Find the wait before buying the fix

Maya's booking request is late. This packet asks where it waited, what evidence would separate two plausible causes, and whether a proposed change would reach the customer deadline while preserving a correct booking. Read the [illustrated whole-path lesson](../../reader/BOOK-LOCATORS.md#book-8f46dac298efb5e9) and [E07](../../curriculum/EXERCISES.md#e07), make your own decision for each case, then compare the [assessor notes](ASSESSOR.md).

Run the standard-library arithmetic from the repository root:

```sh
python3 examples/performance-boundary-review/lab.py
python3 -m unittest discover -s examples/performance-boundary-review -p 'test_*.py' -v
```

The fixture adds stage durations from **one fictional request**, not percentiles from unrelated measurements. The EBS screen compares fictional attempted IOPS and MiB/s with supplied volume and instance ceilings. It neither reads AWS metrics nor models burst credits, queue behavior, EBS accounting of I/O size, latency, instance family, snapshot hydration or billing. A Boolean “exceeded” flags a candidate measurement, not a root cause or a license to resize.

| Case | New fact | Decide and defend |
| --- | --- | --- |
| 1. CPU headline | Average EC2 CPU is 45%, but one worker is saturated while others wait for a serialized step. Tags show which instance serves the affected tenant. | Identify the per-process and request evidence needed before changing family/size or scaling out. Which part of the code can actually use more cores? |
| 2. EBS volume gate | The fictional demand is 6,000 operations/s at 4 KiB each; the volume's supplied ceiling is 3,000 IOPS and 125 MiB/s; the instance's supplied EBS ceiling is 7,000 IOPS and 100 MiB/s. | Compute attempted MiB/s and identify which supplied gate binds. Which **real** CloudWatch volume and instance metrics would you inspect? What would make a volume change insufficient? |
| 3. Instance gate | Demand becomes 3,500 operations/s at 4 KiB, the volume ceiling is 5,000 IOPS, the instance ceiling is 3,000 IOPS. | Explain why buying more volume IOPS may not improve the path. Name a second check for first-read or guest file-system behavior. |
| 4. Distant transfer | An office has 8 TiB to upload in five days but can spare at most 80 Mbit/s; a second workflow sends ten million tiny independent objects. | Use the [transfer lower-bound lab](../migration-mechanisms/README.md) for the first claim. Decide where multipart upload, Transfer Acceleration, DataSync or object grouping could help, and which cannot defeat the uplink bound. Count incomplete parts, requests, retained versions and lifecycle/retrieval costs. |
| 5. Shared files | A Linux service needs concurrent NFS file operations. Another existing Windows application requires SMB and Active Directory. A third team has data already in S3 and wants both S3 API and NFS writers on the same names. | Compare EFS, FSx for Windows File Server and S3 Files by interface, identity, consistency/synchronization, active-data cost and first-read behavior. State a conflict test for the third team. |
| 6. Database wait | The same booking request spends 420 ms waiting for the database. A dashboard reports rising connections, but a query plan shows a broad scan and another trace shows lock wait. | Distinguish pool acquisition, SQL work and lock wait. Say when RDS Proxy helps and when it cannot. Explain the objective's older Performance Insights term against current Database Insights guidance. |
| 7. Placement | A tightly coupled simulation passes large messages between EC2 workers. A web API in the same account spends most of its time waiting for RDS. | Choose which workload merits a placement-group experiment. Identify capacity, network, AZ-failure, instance-support and cost checks before moving either one. |
| 8. The faster candidate | Halving file wait makes the modeled request 750 ms; reducing database wait by 300 ms makes it 580 ms against a 600 ms target. A faster query also returns a booking from another tenant. | Reject the incorrect result. Define the same-mix baseline/candidate experiment, correctness checks, p95/p99, error/failure headroom, full cost, rollback and stop condition. |

Before any real test, select a non-root identity and exact resources, verify current Region support and price for **every** candidate, and estimate an entire bounded run against limits and a credit reserve chosen for the account. Include running instances, EBS capacity/performance/snapshots, storage requests, DataSync or acceleration, shared-file capacity/access, database diagnostics/proxy, transfer, logging and cleanup. Do not treat a budget alert as an enforced stop. The packet makes no AWS calls, spends no credits, and does not select a production configuration. Organization-dependent cases stay design-only.
