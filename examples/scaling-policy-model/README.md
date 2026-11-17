# Choose a scaling signal and protect the bottleneck

This local lab supports the [DOP-C02 task 3.2 scaling design route](README.md#dop-c02-task-32-scaling-design-route) and Unit 02's scaling lesson. It uses only Python's standard library. It does not emulate AWS, call an AWS API, create infrastructure or estimate a bill.

## Part 1: size a queue target from a waiting-time promise

Suppose one ECS task takes 0.1 seconds to process one independent message, and the business accepts a queue wait of 10 seconds. In this simplified steady model:

```text
target backlog per task = acceptable wait / processing time per message
                        = 10 seconds / 0.1 seconds per message
                        = 100 messages per task

observed backlog per task = 1,500 visible messages / 10 running tasks
                          = 150 messages per task

candidate task count = 1,500 visible messages / 100 messages per task
                     = 15 tasks
```

The model helps connect a business wait target to a candidate scaling signal. It assumes one message at a time per task, constant service time, no retries, no initialization delay, no in-flight messages, no downstream limit and an accurate task count. Those assumptions are intentionally simple. AWS's ECS guide demonstrates backlog per task with target tracking; a real policy must use the service's supported metrics and behavior.

## Part 2: find the bottleneck before adding workers

The second fictional system receives 12 photo jobs per second. Workers can finish 20 per second and a database can save eight results per second. Its steady completion ceiling is the smallest stage: `min(12 arrivals, 20 worker capacity, 8 database capacity) = 8 per second`. Four jobs per second accumulate. Doubling worker capacity to 40 still yields eight completions per second because the database remains the limit.

If the save path is independently improved to 16 per second, completion can reach 16 while a backlog exists. With 12 new jobs per second, four spare completions per second can drain a 1,440-job backlog in six minutes. These are arithmetic consequences of the fixture, not AWS throughput claims or advice to resize a database.

Run the lab and its tests:

```bash
python3 examples/scaling-policy-model/lab.py
python3 -m unittest discover -s examples/scaling-policy-model -p 'test_*.py'
```

## DOP-C02 task 3.2 scaling design route

Complete each case before reading the separate [assessor notes](ASSESSOR.md). Draw the customer path and identify the bottleneck, capacity control, protective limit, evidence and cost driver. Change one fact and revisit your choice.

1. **Find the scaling problem.** A service has rising p95 latency and errors while average CPU is 35%; its database connection wait rises sharply. Identify the first measurement and bottleneck to investigate. Explain why scaling the API tasks may increase harm. Then change the database wait back to normal while CPU rises to 90% and state what new evidence supports adding tasks.
2. **Select auto scaling, load balancing or caching.** Static public help pages account for 70% of reads; authenticated repair records are tenant-specific. Choose what may be cached, where a load balancer belongs, and which requests must keep reaching authorized application logic. Change the cache key so it omits tenant identity and explain the failure.
3. **Deploy a container-based application.** A long-running image processor needs a custom library and graceful draining of accepted work. Compare ECS on Fargate, ECS on EC2 and EKS only against stated needs. Identify the image, service/task, capacity, permission, health, state and release evidence required. Then add a Kubernetes-specific admission requirement and reconsider EKS.
4. **Scale a workload across Regions for global users.** Customers in two continents report high static-image latency; booking writes require one authoritative record. Decide whether edge caching, regional reads, regional application cells or a different data design addresses the requirement. State what must remain single-writer or be partitioned, and how routing and failback work. Multi-Region remains design-only here.
5. **Configure a serverless request and worker path.** A short booking API request calls a Lambda function; image conversion can wait and runs as a separate queue consumer. Assign the synchronous API and asynchronous worker roles. Identify API/Lambda concurrency, timeout, retry, queue, database and cost limits. Change the database connection budget and show the safe concurrency bound before proposing more invocations.

For each answer, distinguish **assumption**, **observed evidence**, **candidate configuration**, and **unverified AWS behavior**. The supplied assessor explains decision boundaries; it is not a calibrated exam key or learner result.

## Cost and evidence boundary

This cloud-free worksheet creates no AWS resources. A later live implementation needs a scoped non-root identity, an entire-run estimate, spending and credit-reserve limits chosen for the account, and verified cleanup. Check current plan and credit eligibility before selecting services. No Organization is required for this case; work through multi-account and organization-based variants as design exercises unless you have a suitable, separately authorized environment.

The local arithmetic proves only the formulas for the supplied inputs. It does not prove the arrival rate, worker/database throughput, AWS metric freshness, scaling delay, task placement, regional feature support, cost, customer performance or that a learner can transfer the reasoning independently.
