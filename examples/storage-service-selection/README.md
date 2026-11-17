# Select a cost-effective storage service

This paper case compares object, file and block storage for three workloads. It creates no AWS resources and uses no live metrics or prices. Begin with what the application must do, cross out services that cannot meet the interface or recovery promise, then compare the costs of the remaining candidates.

Check current [S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html), [EFS](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html) and [EBS](https://docs.aws.amazon.com/ebs/latest/userguide/what-is-ebs.html) documentation and their live [S3 pricing](https://aws.amazon.com/s3/pricing/), [EFS pricing](https://aws.amazon.com/efs/pricing/) and [EBS pricing](https://aws.amazon.com/ebs/pricing/) pages before recommending a real workload. This comparison is deliberately bounded; other file services may fit requirements beyond its Linux/NFS scope.

## Workload portfolio

A digital studio has three independent products:

1. A customer photo library stores original uploads and thumbnails. Applications retrieve each image by a stable ID; users do not mount or edit a shared directory.
2. A rendering service has 20 Linux workers that must read and update files in one shared NFS namespace while a job is running. The team has no safe mechanism to coordinate duplicate edits to the same file yet.
3. A single EC2 analytics machine writes a scratch database that uses random reads/writes and a conventional operating-system file system. The working data must persist when the EC2 instance is stopped; snapshots are required for the recovery design.

For each workload, recommend a service to evaluate, explain why the other two interfaces are poor fits, and list evidence that could overturn the choice. Include capacity, object/file size and count, reads/writes, concurrency, latency/throughput, failure boundary, recovery test and monthly cost inputs.

| Workload | Your candidate and rejected alternative | Whole-cost inputs and missing evidence |
| --- | --- | --- |
| Customer photo library | | |
| Shared Linux NFS workspace | | |
| One-machine random-I/O disk | | |

Save your first comparison before opening the [assessor notes](ASSESSOR.md). Keep service eligibility, measured application behavior and the complete cost estimate as separate decisions.

## Change the workload

- Photo editors now require concurrent in-place edits and POSIX-style locking. Can the S3 object contract still meet the requirement? Identify which file services and coordination semantics need investigation.
- The render workers now run on Windows and require SMB with Windows ACLs. The Linux/NFS EFS candidate is no longer enough; identify the next service family to evaluate and the directory/identity requirements.
- The database machine is replaced with 40 independent readers that need a shared, read-only corpus. Explain why attaching one block device or multiplying EBS volumes does not create a shared file/object catalog by itself.
- Half the shared workspace is rarely touched but must remain mounted. Compare EFS lifecycle/storage classes with a separate archive workflow; include restore and file visibility requirements.

## The same data through two doors

This is a new, fictional decision. Do not use the assessor until you have saved your first answer. Maya already has photographs and annotation JSON in an S3 bucket. A Linux editor needs an NFS path to annotations; a customer app still reads the corresponding objects through the S3 API. Both applications can change an annotation. No measured file size distribution, write rate, rename frequency, acceptable synchronization delay or price has been supplied. The business promises that a customer sees an approved annotation, not an unreviewed intermediate edit.

Compare three bounded candidates: **A**, modify the editor to publish reviewed objects directly; **B**, keep a separate shared file system and copy approved versions into S3; **C**, evaluate S3 Files on the existing bucket. For each, name the authoritative version, who resolves conflicting writes, one security check, one recovery check and the main cost meters. Choose only a provisional path and state the missing fact that could reverse it. Do not claim that any candidate has been tested here.

Preserve that answer. Then work these changed facts one at a time:

1. The mounted file's POSIX mode denies Ben, but Ben's automation role can call `s3:GetObject` on the corresponding key. Can Maya claim the annotation is private from Ben? Name the permission path that must change and the forbidden read to observe.
2. Maya saves an edit on the NFS mount. Before it has appeared as the intended object version, the customer app writes a different version through the S3 API. The mounted file later contains the API version; a lost-and-found file contains Maya's edit. Which version is authoritative for the bucket, where is Maya's work, and what approval/reconciliation step is still needed? Do not call a mounted save proof of customer publication.
3. The editor renames a directory containing many annotations. The NFS command returns, but the S3 API temporarily lists objects under both prefixes. A downstream job reads the bucket at that moment. Which atomicity claim fails, and what application-level publishing boundary could keep customers on one approved set?
4. A colleague says the bridge is cheaper because the bucket already exists. Name the metered file-system work, the continuing S3 charges and retained copies that a full estimate must include. State which workload counts and selected Region are missing. Do not insert a current rate from memory.
5. Change the Linux editor to a Windows desktop tool that requires SMB, Active Directory identity and NTFS ACLs. Does the earlier NFS bridge satisfy this contract? Name a service family to investigate, plus the identity, migration, backup, network and whole-price checks before a choice. This case is design-only; it does not create a directory or file server.

After saving the independent answer, ask Codex for one unsupported assumption in your preferred path. Check any service-specific answer against the current [S3 Files synchronization](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-synchronization.html), [two-path permissions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-posix-permissions.html), [metering](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-files-metering.html) or [FSx for Windows access](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/using-file-shares.html) guidance. Keep its critique separate from your first answer. No AWS account, spending or real customer data is needed.

Ask Codex to challenge each recommendation: “Which interface requirement disqualifies the cheapest-looking candidate? Which cost input is missing? Which failure boundary is hidden in my choice?” Check product behavior against AWS primary docs and prices against the selected Region. No price winner, benchmark or production readiness follows from this fictional case.
