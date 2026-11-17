# Individual-skill review: SAA-C03 task 3.1

Internal editorial review, October 18, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain3.html#solutions-architect-associate-03-domain3-task1) lists two skills. Our IDs are editorial positions and labels are paraphrases. Both remain partial. The new [storage lesson](../../reader/BOOK-LOCATORS.md#book-316ad1ab1452bb2f) expands the previous introductory comparisons.

## Skill 01 — Match storage to performance requirements

Maya has photographs accessed by key, a Linux application needing a shared directory and a machine workload expecting a disk. Compare suitable interfaces before naming services. Then change the workload to many small operations rather than large sequential reads, and explain what must be measured.

Look for: interface/update semantics, latency versus IOPS versus throughput, clients, concurrency, network/instance ceilings, failure behavior and whole cost. The lesson explains S3/EFS/EBS candidates and caveats using primary references. Its 4 KiB and 256 KiB examples are arithmetic, not benchmarks. No comparative S3/EFS/EBS performance run, complete configuration package or independent learner response exists.

## Skill 02 — Plan storage growth

The same total byte count changes from a few large objects to millions of small ones. Separately, the shared file application doubles its clients and an EBS volume grows without a visible file-system increase. Explain three different scaling problems and the evidence needed for each. Add an office-disconnection requirement.

Look for: object count/request overhead, concurrency and throughput, cloud-volume versus operating-system capacity, growth thresholds, quotas, recovery time and offline data semantics. Unit 20 provides the decision structure. It does not implement hybrid caching, workload-specific growth automation or real expansion/recovery tests.

## Knowledge review and findings

The task contains three knowledge areas: hybrid storage, storage-service fit and interface characteristics. Service fit and interface explanation are now substantive for a bounded S3/EFS/EBS comparison. Hybrid selection now includes a bounded File Gateway versus managed local-copy/transfer comparison, outage dependencies, pending-upload arithmetic and writer ownership; no service implementation is verified. Specialized file systems and multi-interface services require separate comparisons when their workloads apply; this is not a complete service catalog.

The later [two-door storage study](../../examples/storage-service-selection/README.md#the-same-data-through-two-doors) adds one such bounded comparison: an existing S3 collection with an NFS editor and S3 API reader. Unit 20 and the separate assessor address S3 Files synchronization, mount-versus-API permissions, conflict and rename behavior, cost meters, and a changed Windows/SMB contract that points toward an FSx evaluation. AWS primary S3 Files and FSx documentation was checked October 26, 2026. This is an authored paper exercise; no service was created, no selected client or cost was measured, and no learner response was observed.

The previous manuscript named object/file/block storage but did not develop their access semantics, performance units or growth failure cases. Added unit 20, source references, a decision table and flow diagram, security/cost responsibilities and transfer questions. Both skill reviews remain partial. For assessment, give prompts without rationales and record actual unaided reasoning plus assistance; no reader result is inferred.

## Archive retrieval exercise — design only

A customer needs an archived photograph within 120 minutes. Assume sequential investigation, preparation, transfer and validation take 10, 80, 20 and 15 minutes. The catalog shows the object. A teammate proposes declaring recovery complete as soon as restoration is requested.

Before reading the assessor notes, explain: Does the design meet the deadline? What should the customer see while waiting? Which identity and content checks must precede delivery? What changes when the temporary copy expires? Compare keeping an immediately readable copy with changing the delivery promise. Then change transfer time to 10 minutes and add one 12-minute retry; recalculate the outcome.

### Assessor notes

The original journey takes 125 minutes and misses by five. Reducing transfer to 10 gives 115, but the added retry makes 127 and misses by seven. The catalog entry and accepted restore request do not establish read readiness. Expect completion/status evidence, the intended version, authorized access, a successful read and content validation. Temporary-copy expiry and underlying record retention are separate; the class-specific restoration path matters. The comparison must include customer tolerance, access frequency, full cost and cleanup rather than choosing only by stored-byte price.

Transfer question: the same customer now needs the photograph within ten minutes. A strong answer revisits the architecture or promise instead of presenting the fictional 80-minute preparation as an AWS guarantee. This is an authored assessment with worked arithmetic, not a timed restore, cloud permission test or independent learner result. Both skill entries remain partial.

## Individual knowledge evidence review

On October 18, 2026, checked each of task 3.1's three knowledge bullets against the current official Markdown and the inventory's accepted SHA-256 digest. All three matched. The [knowledge ledger](../knowledge-evidence.csv) now records separate partial mappings for hybrid storage, service selection and object/file/block characteristics. These editorial IDs are inventory positions, not AWS-issued objective identifiers.

The evidence differs by objective: hybrid storage has five authored outage cases; service selection has workload/growth and archive-deadline prompts; interface characteristics have explanations and changed-workload questions. None has an independently observed learner response or a comparative cloud implementation. A diagram and correct arithmetic cannot establish NFS compatibility, concurrent-write correctness or a measured recovery time. Record those gaps separately rather than treating the three mappings as completed certification coverage.
