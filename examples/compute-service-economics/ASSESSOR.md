# Assessor notes: compute-service cost comparison

This guide evaluates the quality of the decision process, not whether a learner chooses a predetermined winner. The workload has too little measured detail to establish a universal or production answer.

## Strong answer characteristics

- The learner first verifies that the chosen Lambda mode, Fargate task shape or EC2 instance path can meet duration, runtime, concurrency, networking, queue, availability and recovery requirements.
- All candidates are estimated for the same monthly accepted work, 2% retry allowance, S3 outcome and 10-minute normal completion promise. If measured execution time or capacity differs, the learner changes the model and explains why.
- The learner distinguishes standard Lambda event-function request and configured-resource-time charges from Fargate task vCPU/memory/storage/time charges and EC2 instance runtime charges. They use the selected Region and current prices, not stale memorized rates.
- The estimate includes necessary integration and whole-path costs. Plausible categories include queue/API access, S3 requests and storage, CloudWatch logs/metrics, image storage and transfer, addresses, load balancing, EBS, snapshots, licensing, idle capacity and other network or service charges.
- The learner does not assign an unsupported dollar value to staff work but names ownership and the tasks that create operational effort: patching image dependencies, host maintenance, scaling, alarms, retries, dead-letter handling, restore, capacity cleanup and cost review.
- The learner notes that Fargate removes customer management of underlying host capacity but does not patch application dependencies in the image. EC2 adds host lifecycle work. Lambda removes server administration for the selected mode but leaves function, event, data and recovery design responsibilities.
- The decision remains provisional. It names what evidence could reverse it, such as larger images, measured cold-start/startup behavior, a shorter deadline, sustained overnight throughput, host-only dependency, changed failure objective or a materially different full-path estimate.
- Codex's answer is treated as a draft: the learner checks source dates, service mode, units, Region, included services, arithmetic and estimate assumptions.

## Common reasoning defects

| Defect | Why it fails | Useful correction |
| --- | --- | --- |
| “Lambda is always cheapest because it scales to zero.” | A per-use model is not enough to compare request volume, duration, memory, integrations and latency requirements. | Estimate the actual selected function mode and full workload path. |
| “Fargate has no infrastructure, so the application needs no maintenance.” | Host management and application/container maintenance are different responsibilities. | Keep image dependencies, permissions, logs, scaling and recovery in the operating plan. |
| “EC2 is cheaper because the instance hourly price is lower.” | Instance uptime is not the whole cost, and spare capacity may remain idle; host operations also have a cost. | Include EBS, transfer, monitoring, licensing, minimum capacity and lifecycle responsibilities. |
| Compare a function's peak workload to a container's quiet workload. | The candidates are solving different amounts of work. | Normalize volume, time window, retries and customer promise. |
| Put a missing calculator line at zero. | Unknown dependencies and transfer may materially change a result. | Mark it unknown and bound or investigate it before recommendation. |
| Pick a Savings Plan because its displayed rate is lower. | A commitment can cost more than the flexible baseline if usage falls or the workload changes. | Validate steady demand, scope, term, eligible usage and downside before commitment. |
| Treat promotional AWS credits as a reason to ignore list-price cost. | Credits are finite and can hide a design that is unsustainable afterward. | Show both the estimated service cost and the separate remaining-credit budget. |
| Let Codex supply current prices without source verification. | Model output can confuse Regions, pricing models, discounts and dates. | Use official current pricing and calculator inputs; retain the estimate date and assumptions. |

## Evidence boundary

This paper exercise does not run an image benchmark, create a queue or worker, demonstrate multi-AZ recovery, query the learner's AWS bill, preserve a calculator estimate, or measure learning. A written recommendation is design evidence only. The next stronger evidence would be a safe representative benchmark and an independently reviewed cost model, each with its own scope and guardrails.
