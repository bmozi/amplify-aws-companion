# Individual-skill review: SAA-C03 task 3.2

Internal editorial review, October 18, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task2) lists four skills. Our IDs are editorial positions; labels and assessment scenarios are original paraphrases. All four remain partial. Teaching is in [unit 2](../../reader/BOOK-LOCATORS.md#book-1b1379691a2f6239), with the container comparison in unit 15.

## Skill 01 — Separate independently scaling work

A web application accepts photographs and transforms each one before replying. Traffic rises, but only transformation needs additional capacity. Propose a boundary and explain how the customer learns that work finished. Then introduce a failure between saving the request and sending the message.

Look for: independent acceptance/worker capacity, durable work identity, dispatch recovery, status reporting and duplicate-safe effects. Separation adds network and consistency responsibilities. Unit 2 develops this reasoning and links the request-processing companion. Local fixture behavior is not a live independently scaled fleet.

## Skill 02 — Choose scaling signals and conditions

Eight workers complete at most 16 jobs per second; arrivals rise to 17. The supplier caps the whole fleet at 18. Explain why the backlog grows, what 12 workers change, and why a CPU percentage alone cannot decide whether customers receive timely service. Now make the supplier temporarily unavailable.

Look for: negative versus positive spare capacity, supplier bottleneck, oldest-job age, arrivals/completions, throttling, startup delay and recovery margin. At 18 effective completions and 17 arrivals, only one waiting job per second drains. These are arithmetic assumptions, not measurements. The revised unit 2 now adds an EC2 target-tracking explanation and a queue-wait-to-backlog target calculation; compute case 8 tests changing duration and missing/zero-capacity observations. A configured autoscaling policy, observed alarms and load test remain absent.

## Skill 03 — Match compute characteristics to requirements

A sustained image transform runs quickly at first on a burstable machine, then its performance or charges change. A colleague proposes changing to Arm and doubling the instance size together. Explain which observations and compatibility checks you need before approving either change. Change the scenario so most elapsed time is a supplier call.

Look for: CPU credit mode versus promotional account credits, sustained behavior, CPU/memory/network evidence, compatible artifacts and controlled comparisons. More compute does not necessarily shorten an external wait. Unit 2 supplies the selection method and a worked three-job function/container/VM comparison. Complete cases 1–5 in the [compute selection exercise](../../examples/compute-selection/README.md), including the standard-invocation timeout boundary and separate host/image maintenance responsibilities, before reading the assessor notes. No actual EC2 family comparison or architecture migration was performed.

## Skill 04 — Choose resource size from outcomes

Use a new fictional benchmark: P allocates 0.5 GiB and takes 2.4 seconds; Q allocates 1 GiB and takes 1.0 second; R allocates 2 GiB and takes 0.8 seconds. All return correct results for the supplied input. Calculate GiB-seconds, then choose the lowest-resource-time eligible candidate for a 1.2-second execution target and for a 0.9-second target. Explain why neither choice establishes a monthly bill or a p95 customer-response guarantee. Finally, suppose R produces incorrect output on the largest valid input. What can you conclude for the 0.9-second requirement?

Look for: P = 1.20 GiB-seconds, Q = 1.00, R = 1.60. Q has the lowest resource-time among candidates meeting 1.2 seconds; only R meets 0.9 seconds in the original fixture. If R fails correctness, no tested candidate satisfies both correctness and 0.9 seconds; investigate or change the design rather than select an invalid result. Require representative repeated samples, whole-path timing and complete costs. These are authored timings, not a Lambda experiment or learner result.

## Knowledge review and findings

The official task names six knowledge areas. Existing manuscript sections address messaging, scaling, serverless patterns and container orchestration at differing depths. Compute selection now has a resource-shape and sizing method, and unit 14 now develops Batch scheduling versus Glue integration and EMR framework use cases with six design assessments. Actual service-mode compatibility and measurements remain open. Distributed/global/edge compute comparison also remains incomplete. Knowledge ordinals 01 and 04 now have partial individual evidence entries; the other four areas remain unreviewed individually under this task. These observations do not complete the knowledge-bullet evidence ledger.

The material previously explained scaling capacity without developing a controlled resource-sizing experiment. Added selection tradeoffs, burst-credit versus trial-credit distinctions, architecture compatibility, fictional memory-duration calculations and a bounded experiment protocol. All four skills remain partial; live scaling/sizing, broader service comparisons and independent assessment remain open. Give learners prompts without rationales, then record their reasoning and any assistance rather than inferring mastery from the existence of these questions.
