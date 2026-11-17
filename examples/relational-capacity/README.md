# Find which storage meter is busy before buying capacity

Imagine Maya's repair-shop database is slow. One teammate wants a larger server; another wants more storage IOPS. Neither has shown where the customer waited. Start by separating three things: **how many storage operations finished**, **how many bytes they moved**, and **where the database and application spent time**. One SQL query can cause many storage operations or none when its pages are already in memory.

Predict the two ceiling comparisons for each fictional one-second window, then run from the repository root:

```sh
python3 examples/relational-capacity/lab.py
python3 -m unittest discover -s examples/relational-capacity -p 'test_*.py'
```

The standard-library calculator uses pre-stated storage I/O operation rates and average KiB transferred per operation. It calculates `operations/second = reads + writes` and `MiB/second = (reads × KiB/read + writes × KiB/write) ÷ 1024`. The 3,000 IOPS and 125 MiB/s ceilings are **fictional inputs for this exercise**. They are not a selected RDS instance or storage configuration, account measurement, guaranteed limit or price. AWS documents [RDS storage IOPS and throughput as separate performance dimensions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html); actual capabilities vary with the selected engine, size, storage and instance choices.

| Window | Stated fictional storage work | Question before running |
| --- | --- | --- |
| Large reads | 1,000 reads/s at 128 KiB and 200 writes/s at 16 KiB | Which meter crosses its ceiling? |
| Small busy reads | 2,500 reads/s and 300 writes/s, each 4 KiB | Does being below both ceilings prove the customer is fast? |
| Many tiny reads | 3,100 reads/s and 100 writes/s, each 4 KiB | Which meter crosses its ceiling? |

After the output, answer a different question: a request takes 950 ms, including 900 ms waiting for a pool connection and 20 ms executing its SQL. Which part of that trace should the operator inspect first? What would a lock-heavy database trace change? A capacity calculation alone cannot answer either. AWS's [database load and wait view](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html) can help separate CPU, I/O and lock work when supported and enabled; also inspect the application's pool wait and customer latency. See the [connection-budget](../connection-budget/README.md) and [query-plan](../query-plans/README.md) exercises for separate local evidence.

Change one input at a time before reading the [assessor notes](ASSESSOR.md): make the large reads 32 KiB each; double the number of application clients without increasing completed storage operations; and retain the same I/O totals while a lock wait grows. Explain which arithmetic changes and which decision needs new observation. Ask Codex for a proposed diagnosis, then require it to distinguish calculated demand, configured limits, measured wait, and actual customer result. Keep your own first answer in the learning record.

This lab does not create RDS, simulate an engine, measure physical I/O, select a safe capacity setting or estimate a bill. In a real authorized study, verify the selected engine/version/Region, available metrics, instance and storage limits, expected run cost, credit eligibility, cleanup and a spending limit before deployment. No AWS account is needed here.
