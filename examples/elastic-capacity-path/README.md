# Three capacity dials on one request path

Maya's shop sees a lunch rush. Work the [illustrated lesson](../../reader/BOOK-LOCATORS.md#book-d1b4552f4da8e9ca) and [E07](../../curriculum/EXERCISES.md#e07) before opening the [assessor reasoning](ASSESSOR.md). These are original teaching cases, not exam questions or AWS measurements.

From the repository root, run:

```sh
python3 examples/elastic-capacity-path/lab.py
python3 -m unittest discover -s examples/elastic-capacity-path -p 'test_*.py' -v
```

The standard-library model uses **steady average requests per second** and supplied independent ceilings. It does not simulate queueing, cache eviction, per-key hot spots, burst capacity, service scaling delay, real request latency, database query cost or AWS prices. Its “fits” result means only that none of the three supplied arithmetic ceilings is exceeded. It is not a deployment recommendation.

Before reading the assessor, write an answer for each change:

| Case | Changed condition | What the learner must decide |
| --- | --- | --- |
| 1. Lunch baseline | 60 requests/s; 10% writes; safe cache hits equal 40% of all requests; two ready workers each handle 20 origin requests/s; database allows 28 reads/s and eight writes/s. | Calculate hits, origin requests, database reads and writes; identify the binding ceiling and a customer signal that would confirm the suspected wait. |
| 2. More clerks | Add one ready worker; leave request mix and database limits unchanged. | Recalculate every stage. Explain why a successful Auto Scaling activity is not proof that bookings became faster. |
| 3. More safe hits | Raise hits to 50% of all requests by caching only public, freshness-tolerant reads. | Recalculate and identify which limits now fit the supplied snapshot; state a cache correctness and cold-cache test before doing this on AWS. |
| 4. Private response | A developer proposes sharing each customer's booking-result response under one URL to obtain 70% hits. | Reject or redesign the cache key/policy. State which identity and freshness facts must be checked and what must never be shared. |
| 5. Database changed | The actual service is RDS and free storage is low, while traces show expensive read queries. A teammate enables storage autoscaling alone. | Explain which limit it addresses and which it does not. Compare query/index work, a compatible read replica and the primary write path with freshness and cost. |
| 6. Different database | The same design is moved to a DynamoDB table. Throttling names an index write hot spot, while table read utilization is modest. | Identify the affected table/index and read/write dimension. Explain why table read scaling and an unrelated cache hit-rate increase may miss the cause. |
| 7. Changed mix | Writes rise from 10% to 20% while safe hits remain 50% of all requests; retain the baseline capacities. | Recalculate and locate the new limit. Name an appropriate operational observation and stop condition before increasing any database setting. |

For a real experiment, verify the selected service mode, Region, workload and complete current prices. Choose whole-run spending and reserve limits for the account you will use. This packet makes no AWS calls and spends no credits. Ask Codex to challenge your arithmetic and cache safety, then verify its claims against the linked AWS sources rather than accepting a fluent answer as evidence.
