# Deploy the code; preserve the data

This design-only exercise completes two DOP-C02 task 1.4 knowledge mappings: application storage patterns and tools/services for distributing code. It connects those ideas to the already-reviewed mutable/immutable and deployment-methodology material. No AWS commands are provided. Do not create or delete instances, volumes, file systems, buckets, clusters, functions or images for this worksheet.

Before reading the assessor, draw two paths for each case:

1. **Release path:** source/recipe -> artifact -> platform-specific delivery owner -> candidate -> traffic/recovery decision.
2. **Data path:** application read/write -> storage interface -> lifetime/sharing/backup owner.

Record the customer invariant, permissions, failure boundary, replacement behavior, cost sources and cleanup owner. Preserve your first response before asking Codex to critique it. Use the [learning record](../../curriculum/LEARNING-RECORD.md) to separate your answer from AI assistance.

## Cases

1. **The missing consent file.** An EC2 appointment service stores an exported consent CSV on the root disk and some working files on instance store. A new AMI replaces the instance during a patch. Which data is scratch, which data must be retained, and what must be checked about the EBS root-volume termination setting? Choose a storage/reconciliation design for the authoritative consent records. Explain why an AMI is not the backup.
2. **The shared uploads folder.** A web application now runs as several ECS tasks. Each container writes customer-uploaded attachments to its writable layer. One user uploads to task A; a later read reaches task B. Design the data path. Decide whether the requirement is shared files or object retrieval, name a fitting storage interface, and include access, retention, lifecycle and cost questions.
3. **A Kubernetes move.** The service moves to EKS. A database pod must retain state as its pod is replaced; another set of stateless web pods only needs static configuration and scratch space. Compare a block-backed persistent volume with a shared file or object design. State which add-on/driver, Availability Zone, access mode and pod placement facts you would verify for the selected pattern. Do not assume that a capability on ECS is automatically supported the same way on EKS/Fargate.
4. **Lambda's `/tmp`.** A Lambda function downloads a document, converts it and writes a temporary result to `/tmp`. A teammate proposes storing the only copy of an invoice there because it survived their warm test invocation. Identify the valid temporary use and the invalid durability conclusion. Choose the separate durable record path and name the required authorization and cleanup/retry evidence.
5. **Pick the delivery tool.** A team wants all four things: (a) patch and test a reusable EC2 base image, (b) install an application revision to an EC2 fleet, (c) shift an ECS blue/green release, and (d) publish a Git-connected frontend. Match Image Builder, CodeDeploy, ECS/Kubernetes platform control and Amplify Hosting to their actual jobs. Explain why CodeDeploy does not mean “deploy anything to any AWS compute.”

For any proposed cloud follow-up, estimate the entire run against the account owner's chosen spending limit and credit reserve, identify the scoped non-root identity, restrict test data, set a stop condition and name how every created resource and retained volume/image will be found and cleaned up. Organization-based image sharing or multi-account release routes stay design-only here.

After you finish, compare with [assessor notes](ASSESSOR.md). Recheck all current service details against AWS documentation before implementation. These cases are not calibrated certification questions.
