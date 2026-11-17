# Choose the data movement service for the job

These are design cases only. They create no AWS resources and use no real customer files. Start with the outcome and operating pattern, then check the current supported source/target pair, security requirements, region and complete price.

AWS describes three different tools that can appear in a migration discussion: [DataSync](https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html) copies data between supported storage systems; [Transfer Family](https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html) gives users and partners managed file-transfer endpoints such as SFTP into S3 or EFS; and [S3 File Gateway](https://docs.aws.amazon.com/filegateway/latest/files3/what-is-file-s3.html) keeps a supported NFS/SMB file-access path to S3 with a local cache. They solve different operating problems.

## Portfolio case

A manufacturer has three workstreams: retire a 12-year-old NAS after a checked move of its project files to S3; receive a signed daily invoice from a supplier that only supports SFTP; and keep a laboratory application using an SMB share while its files are stored in S3. The migration manager proposes one DataSync task as the answer to all three.

For each workstream, choose a primary service to investigate and explain why the other two do not meet the stated operating need by themselves. Then write the key design questions, transition/retirement evidence and ongoing cost drivers.

Save a decision for each workstream before consulting the [separate assessor](ASSESSOR.md).

## Change the constraints

The SFTP supplier now offers HTTPS object upload but requires a private network path. The lab app is retired, but the business needs weekly copies of a changing archive from its NFS source. Re-evaluate the candidates. State which source pair and endpoint options need current documentation checks and which cost assumptions must be replaced with quotes or measurements.

Ask Codex to act as a skeptical migration reviewer: “Which of my three workloads actually needs recurring user-facing file access? Which one is a copy task? What data or permission could be omitted from my success criteria? What evidence lets us retire the source?” Verify its current service claims from AWS primary documentation. An AI recommendation is a hypothesis until the owner and technical evidence support it.
