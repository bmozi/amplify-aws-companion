# Assessor notes: instance-family selection

Score the evidence-to-hypothesis reasoning, not the instance family chosen by name. The rows deliberately omit the information needed for a production recommendation.

## Suggested hypotheses for the fictional cases

- **A — invoice renderer:** A compute-optimized family is a candidate because CPU is persistently busy, memory is modest, and work parallelizes. The x86-only license blocks an Arm family until the vendor confirms support and licensing. A general-purpose family is a reasonable benchmark alternative. Verify that parallelization actually improves end-to-end completion.
- **B — product cache:** A memory-optimized family is a candidate because a real 60-GiB active working set is the constraint, not CPU. General purpose is an alternative if the dataset shrinks or can be partitioned. First rule out a leak, and remember that a larger machine does not repair unbounded growth.
- **C — analytics reader:** Storage-optimized local-NVMe capacity is a candidate only if it matches the measured I/O pattern and the data can be rebuilt or replicated safely. EBS-optimized compute with the right EBS volume/performance may be a better alternative when persistence or shared durability dominates. Benchmark read latency, warm-up and EBS/instance limits; the word “storage” alone is insufficient.
- **D — image classifier:** Accelerated computing is a candidate only after its exact GPU/runtime/model support is verified. Compute-optimized CPU remains the alternative if batching is low, data transfer dominates or accelerator utilization is poor. Include artifact compatibility and input/output movement in the test.

The instance type name can change, a family can add a new generation, and Region offerings differ. A technically sound answer can cite family categories (C/R/I/P, for example) while postponing the exact generation/type until current specifications and requirements are checked. Graviton is Arm architecture; a family choice cannot bypass an x86-only binary or driver. T families suit appropriate burst patterns, not sustained high CPU merely because the average looks low. Check CPU-credit behavior and surplus cost before treating them as cheap.

## Common errors

| Error | Why it fails | Correction |
| --- | --- | --- |
| Choose the family from one average CPU percentage | Peak duration, memory pressure, waits, I/O and customer completion are missing | Collect representative time-series and end-to-end evidence for the constrained stage |
| Call every disk bottleneck “storage optimized” | The bottleneck may be EBS volume throughput, queue depth, network, file layout or local cache behavior | Measure the actual storage interface and choose between local ephemeral and persistent options deliberately |
| Pick GPU because the workload contains images or AI | The algorithm may not support it, transfers may dominate, and the accelerator may sit idle | Verify runtime compatibility and utilization in a bounded benchmark |
| Move to Arm because a price chart looks lower | Native libraries, licenses, agents and deployment artifacts may be architecture-specific | Verify all runtime and operational dependencies on the target architecture |
| Size up to cure a software leak or serial algorithm | Larger capacity can only delay the same failure or leave added resources unused | Fix or partition the problem, then retest before buying capacity |

## Assessment boundary

No family was queried in the learner's selected Region, priced, launched or benchmarked. The learner's answer is a provisional hypothesis, not production approval. An independent review should ask for the original evidence, the changed case and the test capable of falsifying the choice.
