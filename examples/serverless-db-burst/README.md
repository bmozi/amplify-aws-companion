# Six requests, two database seats

Maya's booking function is short and can start several copies at once. Her database can handle only two of this exercise's connection attempts at a time. Think of six customers arriving at a counter with two open windows. A faster door does not create a third window.

**Predict before running:** If all six handlers try the two slots together and a full slot refuses immediately, how many save? If Maya puts the six jobs in a local waiting line served by two workers, how many eventually finish? Write the two numbers and why before opening the output.

```bash
python3 examples/serverless-db-burst/burst_lab.py
python3 -m unittest discover -s examples/serverless-db-burst -p 'test_*.py' -v
```

The direct path launches six real local threads together and holds the two admitted slots until all six have tried. Its repeatable result is **two saved, four `database_busy`**. The second path places six numbered jobs in a volatile in-process queue. Two local consumers wait for a slot, and all six complete once a slot becomes available. This is a deliberately small concurrency experiment; the queue does not survive a process crash and there is no real database, Lambda function, SQS event source, API Gateway or bill.

## Change the condition

1. Run `direct_burst(database_slots=3)` from Python. Predict the new saved/busy split and explain why this change affects the direct path.
2. Run `queued_work(consumers=3, database_slots=1)`. Check `completed`, `remaining` and `peak_database_slots_used`. Explain why more consumers do not add a database seat. The default two-consumer run uses a barrier to make both first workers hold a slot together. There is no modeled service-time delay, so neither run is a throughput benchmark.
3. Maya now has a **synchronous** booking API. Suppose she caps the function at two concurrent invocations but six requests arrive at once. State what must happen to the four requests that cannot invoke immediately. Do not assume a concurrency cap creates a durable queue. Decide whether the API should reject, retry, or explicitly accept work into a durable path and return a receipt. Each choice changes the customer promise.
4. Maya instead uses an SQS-triggered worker. Name the function's reserved concurrency, each event source mapping's maximum concurrency where supported, the database's safe work capacity, timeout, retry and duplicate-effect rules. Add a second event source mapping and explain why its cap cannot be considered alone. An API trigger on the same function would also compete for function concurrency.
5. A teammate proposes provisioned concurrency to cure `database_busy`. Explain which problem that setting addresses and which database observation would still need to change. Ask Codex to critique your explanation only after you save your first answer. Check service claims in current AWS documentation.

Read the separate [assessor notes](ASSESSOR.md) after attempting the changed cases. Keep first answer, revised answer, help received and the exact local observation in your [learning record](../../curriculum/LEARNING-RECORD.md).

AWS describes [reserved and provisioned concurrency](https://docs.aws.amazon.com/lambda/latest/dg/configuration-concurrency.html) as different controls. It documents [SQS event-source scaling and maximum concurrency](https://docs.aws.amazon.com/lambda/latest/dg/services-sqs-scaling.html); a source-level maximum does not reserve function capacity. [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html) can manage and reuse connections when the workload allows it, but that is a separate design decision and does not create more SQL work capacity. Verify current settings, support, quotas and costs before proposing a real implementation.

**Evidence boundary:** This standard-library exercise uses local threads, a semaphore and a volatile queue. It demonstrates those exact local rules. It does not establish Lambda scaling, AWS throttling/retry, database connection behavior, SQS durability, customer latency or a safe production concurrency number. A live follow-up requires the intended account/Region and scoped identity, bounded traffic, cleanup and later billing review. Choose whole-run spending and reserve limits for the account you will use. No AWS resources or credits are used here.
