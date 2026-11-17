# Individual-skill review: SAA-C03 task 4.2

Internal editorial review, October 18, 2026. The official [Domain 4 objective](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain4.html#solutions-architect-associate-03-domain4-task2) includes selecting an instance family and size in addition to compute mode, scaling and availability decisions. Skills 01–06 now have separate partial mappings.

## Skill 01 — Determine an appropriate load-balancing strategy

Unit 05, “Choose the load balancer by the job, then compare the full bill,” and the [case](../../examples/load-balancer-strategy/README.md) distinguish HTTP host/path routing with ALB, transport flow and stable zonal addresses with NLB, and network-appliance insertion with GWLB. The case asks learners to reject ineligible candidates before cost comparison, draw a packet/request path, account for load-balancer usage units, GWLB endpoints, target and appliance compute/licenses, transfer, logs and operations, and then revise a choice after a changed constraint. [Assessor notes](../../examples/load-balancer-strategy/ASSESSOR.md) describe expected reasoning and explicit evidence limits.

Current AWS primary documentation was checked for routing behavior, GWLB endpoints and appliance flow, and pricing dimensions. This is partial design evidence. No listener, UDP protocol, appliance, route, endpoint, Terraform plan or price was tested. Workload measurements, a regional estimate, independent technical review and learner outcome remain open. The case is not an official exam question.

## Skill 02 — Select the scaling method for the workload and cost promise

Unit 02, “Pick the kind of change that fixes the bottleneck,” and the [three-workload case](../../examples/scaling-methods/README.md) distinguish adding workers for divisible work, resizing/replacing an instance for an indivisible process, and hibernating a supported individual EC2 machine to preserve in-memory state across idle time. The case gives a queue-capacity calculation, tests whether a slower database removes the benefit of more workers, and changes restart, compatibility and availability requirements. The [local checker](../../examples/scaling-methods/hibernation_check.py) validates selected user-supplied hibernation assumptions; eleven unit tests cover RAM boundaries, storage size/encryption, launch-time configuration, Auto Scaling membership, instance-store loss, input types and unverified support. Passing it means only that the fictional inputs pass those selected local rules.

Current AWS primary guidance was checked for the hibernation state transition, supported AMI/type prerequisites, RAM limits, volume encryption/size, charges while stopped, instance-store loss, Auto Scaling limitation and launch-template replacement behavior. This remains partial design and local-rule evidence. No instance, group, resize, hibernation, AMI/type support or price was verified in AWS; no customer workload or recovery time was measured. Independent technical review and learner result remain open.

## Remaining task work

## Skill 03 — Determine cost-effective AWS compute services for the workload

Unit 02, “Compare the whole cost before calling a compute service cheaper,” and the [calculator-only worksheet](../../examples/compute-service-economics/README.md) compare a standard Lambda event function, an ECS task on Fargate and EC2 On-Demand using one fictional image-processing workload. The sequence rejects ineligible designs before cost comparison, asks learners to estimate a common workload over a month, include surrounding services and idle/retry capacity, identify operational ownership, and state what evidence would reverse the choice. The assessor guide addresses common cost-modeling errors. Current AWS primary pricing pages and the official SAA-C03 objective were checked. Lambda Managed Instances are called out as a distinct current mode for further comparison rather than being hidden inside a generic Lambda price.

This is partial design evidence. No AWS Pricing Calculator estimate was retained, workload was benchmarked, candidate tested for compatibility, failure/recovery behavior demonstrated, or account-specific cost verified. Pricing and feature details must be refreshed at the time of an actual comparison. Independent technical review and learner outcome remain open.

## Skill 04 — Determine the availability required for different workloads

Unit 02, “Set availability from the interruption the business can accept,” and the [three-workload exercise](../../examples/compute-availability/README.md) separate a customer booking journey, a scheduled nonproduction sandbox and a deadline-driven batch. The learner defines the measurement window, distinguishes availability from RTO/RPO/deadline, compares one-zone recovery with surviving multi-AZ capacity and regional recovery, and transfers the reasoning when a training environment becomes customer-facing. The assessor specifically rejects “production always needs multi-region,” “two AZs guarantee availability,” and “healthy worker means batch success.” Current AWS guidance on availability design goals, EC2 Auto Scaling zone distribution and ECS Fargate zone behavior was checked.

This is partial design evidence. The targets and workload are fictional and are not owner-approved SLOs. No customer path, failure, quota, cost, capacity after AZ loss, availability, or RTO/RPO was measured in AWS. Independent technical review and learner outcome remain open.

## Remaining task work

## Skill 05 — Select an appropriate EC2 instance family

Unit 02, “Select the family by the resource the program actually needs,” explains the separation between family and size and relates general-purpose, compute-optimized, memory-optimized, storage-optimized, accelerated, HPC and burstable categories to observable workload evidence. The [four-profile exercise](../../examples/instance-family-selection/README.md) tests CPU, working-set memory, local I/O and accelerator cases, and adds x86 architecture/licensing, local ephemeral storage, cache warm-up, and falsifiable benchmark constraints. The assessor avoids declaring an exact generation or winner because family inventory, specifications and regional availability change. Current AWS instance-type documentation and naming conventions were checked.

This is partial design evidence. The fictional measurements are not AWS data. No current type or family was queried in a selected Region, price checked, application benchmarked or launched. Independent technical review and learner outcome remain open.

## Skill 06 — Select an appropriate EC2 instance size

Unit 02, “Pick the size that meets the peak promise, with a measured margin,” and the [benchmark worksheet](../../examples/instance-size-selection/README.md) provide three same-family fictional test profiles, a p95 response-time goal, a 700 requests/second peak, one-zone-loss requirement and explicit headroom. The learner must select the smallest tested option meeting all conditions, estimate the full operating path in the Pricing Calculator, and revise after memory grows and when EBS becomes the bottleneck. The assessor checks the 840 requests/second capacity calculation and warns that default EC2 metrics do not include all guest-memory measurements. Current EC2 metric, CloudWatch agent and Compute Optimizer documentation was checked.

This is partial design evidence. The profiles and all measured performance are fictional; no instance name, type, Region, cost, Compute Optimizer result, memory metric, benchmark or failover was tested. Independent technical review and learner outcome remain open.

## Remaining task work

All six SAA-C03 task 4.2 skills now have separate partial teaching and assessment mappings. This is not task completion, complete certification coverage or exam readiness. Technical/learner review, live evidence and release gates remain open.
