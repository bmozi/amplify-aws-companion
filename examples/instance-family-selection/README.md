# Select an EC2 instance family from workload evidence

This original design exercise supports SAA-C03 task 4.2 skill 05. It is not an exam question, instance recommendation for a real application, or live EC2 test. Do not launch instances for this paper exercise.

## Start with evidence, not a family name

A team says its EC2 worker is “slow” and asks for a larger instance. You have the following fictional observations from a representative local profile. Each row describes one different worker; do not assume the same family should run all of them.

| Worker | Observed profile | Software/data constraint |
| --- | --- | --- |
| A: invoice renderer | CPU stays near 90% for most of the run; measured peak memory is 2 GiB; calculations can be split across cores | x86-only license library; work input and output are durable in S3 |
| B: product cache | Most time is waiting for the complete active dataset to fit in memory; 60 GiB is used and CPU is usually below 35% | Cache contents can be rebuilt from durable records; restart must not lose authoritative data |
| C: analytics reader | CPU is near 20%, RAM has headroom; measured data access stalls on random local reads from a 1.5 TiB working set | Data can be reconstructed from an independent durable store, but warm-up time affects customer latency |
| D: image classifier | General-purpose CPU processing is slow; the model library can use a specific GPU runtime but transfer and batching have not been tested | Model and library compatibility are believed possible but not yet proven on AWS |

The numbers are fictional clues, not AWS measurements or guaranteed instance performance. In a real case, record workload duration, time-series CPU and memory, disk/volume latency and throughput, network, queue age, startup, concurrency and the success measure. Confirm that the observation covered peak and failure/retry behavior.

## Your investigation

1. For each worker, name the observed limiting resource, the strongest family category to investigate, one plausible alternative and a reason to reject it provisionally.
2. Explain why “slow” alone is not evidence for compute-optimized capacity. Identify a serial process, disk wait or database wait that would weaken that choice.
3. For worker B, state why more memory may help the current working set, and what would show that the apparent need is a memory leak instead.
4. For worker C, distinguish local instance-store behavior from EBS-backed storage. State what data must be durable, how a replacement warms the cache and how much warm-up is allowed before the customer promise fails.
5. For worker D, list the compatibility and utilization tests required before paying for accelerator capacity. State what happens if the model cannot use the accelerator or transfers dominate total run time.
6. For worker A, identify the architecture constraint. Explain why a family that looks attractive on price or CPU alone cannot be selected until the license and artifact's supported architecture are verified.
7. Choose two possible current families to investigate for each workload, using official AWS documentation to confirm their existence and specifications in one Region. Do not assume the family roster or size offerings are identical in every Region.
8. State what is deliberately outside this family-selection decision: exact instance size, regional price, capacity availability, purchase option and production architecture. Those need their own evidence.
9. Ask Codex to argue for a different family for one worker. Require it to point to a measured constraint and identify a benchmark that could disprove its proposal. Check its claims against current official documentation.

## Decision worksheet

| Worker | Measured bottleneck | Family to test | Rejected alternative and reason | Required compatibility/recovery evidence | Observation that could reverse the family choice |
| --- | --- | --- | --- | --- | --- |
| A: invoice renderer | | | | | |
| B: product cache | | | | | |
| C: analytics reader | | | | | |
| D: image classifier | | | | | |

## What evidence would strengthen the choice?

For a reversible, bounded AWS benchmark, define the exact input, warm-up, peak concurrency, success/latency target, data handling, architecture, instance types, region, cost stop and teardown first. Compare one variable at a time where practical. Keep startup, price, CPU, memory, storage and customer completion time together. An EC2 recommendation from Compute Optimizer is useful evidence for supported existing resources, but it does not replace compatibility, workload testing or owner review.

## Cost guardrail

This worksheet creates no resources. Choose whole-run spending and reserve limits after checking current account terms. Do not buy a Savings Plan or Reserved Instance to explore an unproven family.

## Evidence boundary

The completed exercise shows only that the learner can relate selected fictional resource signals to family categories and identify evidence needed next. It does not establish a concrete instance type, price, compatibility, Regional availability, performance, savings, capacity, customer success or learner mastery. Read the [assessor notes](ASSESSOR.md) after writing a first-pass decision.
