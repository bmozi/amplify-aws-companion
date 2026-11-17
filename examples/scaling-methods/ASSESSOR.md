# Assessor notes: scaling method

This is reasoning guidance, not measured learner performance. Accept a different recommendation when it meets the same stated workload contract and names its evidence.

## Photo conversion queue

At the fictional average rate, 300 jobs divided by 10 jobs per worker per minute requires 30 worker-minutes. To finish in 15 minutes at a constant rate requires at least two workers before allowances for launch/warmup, failures, varying job duration and retries. A 30-minute deadline might permit fewer workers if jobs arrive over the full interval, but the event's arrival curve and current queue age matter. The 80-result/minute database ceiling can support the nominal 20-job/minute capacity of two workers, but only if those rates describe the same interval and database work is otherwise bounded. With the changed 35/minute database, two workers can complete at most 20 jobs/minute, three at most 30 and four at most 35. Adding a third worker can therefore help; adding a fourth has only five jobs/minute of useful headroom, and further workers cannot raise this modeled ceiling. A database rate lower than its old value is not automatically the current bottleneck. Recheck queue age and the deadline before paying for capacity. Choose a durable queue, stable retry identity, sufficient headroom and an accepted-to-completed measure. Do not claim an exact Auto Scaling response from this arithmetic.

## License-bound solver

The process cannot be made parallel by adding workers unless the vendor/application can split and coordinate the model. Benchmark its CPU, memory, storage and I/O limits with a representative run, then compare compatible instance types and license terms. A vertical change may require stopping or replacing the instance, and a launch-template update does not change already-running ASG instances. Preserve application state outside instance store and plan for the interruption. A bigger type is not automatically a faster or cheaper completed job.

## Resumable workstation

Hibernation can be a candidate because the user values returning to in-memory process state after an idle period. It has to be enabled at launch, needs a supported AMI/type and an encrypted EBS root volume large enough for RAM plus the OS/application and remaining working space. On the current AWS prerequisites, Linux RAM must be below 150 GiB; Windows RAM may be at most 16 GiB. Verify the specific current regional instance type and AMI, root volume type and size, and perform a controlled resume test. Instance-store contents are lost. In the stopped state compute usage is not billed, but EBS storage remains billed; separately review IP and other persistent resources. Hibernation alone is neither high availability nor a guaranteed fast restart.

## Checklist scope

The local Python check catches missing/contradictory assumptions in a candidate record. Its booleans for AMI and instance-type support come from the reader; the tool does not independently query AWS. A passing result means “the supplied fictional fields are consistent with these selected rules,” not “AWS will hibernate this instance.” No instance, launch template, Auto Scaling group or bill was observed.
