# Keep the booking lane open

Maya's shop receives four slow report jobs at minute 0. One booking arrives at minute 1 and must finish by the end of minute 3. Each report occupies a worker and a database slot for four fictional minutes; the booking needs one of each for one minute. No job is preempted. A waiting booking gets first choice when a slot becomes free. These are invented units for reasoning, not measured AWS throughput.

Run the local, standard-library exercise from this folder:

```sh
python3 lab.py
python3 -m unittest test_lab.py
```

Before reading the output, predict the booking finish time in three cases:

1. Two workers share one queue and two database slots.
2. One report worker and one booking worker have separate queues, with two database slots.
3. The workers stay separate, but every job shares just one database slot.

For each case, say whether the booking meets minute 3, how many reports remain unfinished then, and which resource sets the result. Then change the booking's arrival to minute 0 and explain why the shared design may pass this one case without becoming safe against the original flood. The assessor notes are in [ASSESSOR.md](ASSESSOR.md).

The program is a deliberately small discrete-time model. A job holds a database slot for its whole fictional duration; real applications may use connections for only part of a request. It does not model SQS ordering, Lambda scaling, database lock contention, retries, fairness across tenants, failures, AWS prices or production scheduling. A real design needs observed queue age, booking completion, rejected work, worker concurrency, database connection use, and a tested customer path. Separate Lambda functions or queues are candidates; they are not proof of isolation if they share a constrained database, account quota, network path or operator control.

Ask Codex to draw the resources used by each job and predict the third case before showing it the output. Require it to identify the hidden shared limit, one changed workload that reverses the conclusion, and one measurement that could disprove its recommended capacity split. Compare its answer with the program and the stated assumptions; AI agreement is not an AWS load test.

No credentials, network access, paid service or AWS resource is used.
