# Assessor notes: protective-control coverage

Open these notes after recording a first-pass design and running the local matrix checker.

## Expected reading of the fixture

- Production / `us-west-2` / `web_request_protection` is explicitly missing. Identify the public endpoint and select a supported enforcement point before proposing a WAF web ACL. Check what traffic reaches that resource and preserve an application authorization check behind the edge.
- Production / `us-west-2` / `s3_sensitive_data_review` is stale at 190 hours against the fixture's invented 72-hour threshold. The correct conclusion is “the supplied observation is outside this exercise's freshness window,” not “the bucket is exposed” or “Macie is broken.” Check actual object, key and coverage scope before a real conclusion.
- Development / `us-east-1` / `patch_management` is an exception with a compensating control and 14 days remaining. It is not an ordinary pass. Name its approver, owner, expiry action and evidence that the short-lived fleet really rebuilds from a reviewed image.
- `not_applicable` is not a universal exemption. The fixture provides reasons; a real design should check that the account, Region and resource inventory make those reasons true.

## Reasonable design choices

At the web edge, choose WAF rules where the selected application resource is supported, test new rules in count mode when suitable, and keep Shield's standard and paid Advanced options distinct. At the VPC boundary, follow routes and inspection paths; security groups and network ACLs have different attachment points and state behavior. Use Network Firewall only when the network inspection requirement and traffic path justify its ongoing resource and processing costs.

For multi-account governance, separate the Organizations management account from delegated administrators and workload accounts. Decide whether Control Tower is needed for the landing-zone lifecycle, which preventive/detective/proactive controls apply, which accounts are excluded and how drift is found. If Security Hub CSPM uses central configuration, record its home and linked Regions, policy associations, self-managed exceptions and coverage status. Systems Manager targets supported managed nodes; it does not patch every resource type.

For sensitive data, first identify where it may live, classify it, narrow access and retention, and decide which S3 buckets Macie should inspect. Treat automated discovery as sampled and scope-limited. Estimate bucket monitoring, object monitoring, analyzed bytes and related KMS/S3 usage before activation. For encryption, specify transit endpoints, certificate type and renewal owner, at-rest service/key choice, key policy, backup and restore. CloudHSM's added custody control brings cluster availability, connectivity, scaling, backup and cost duties.

## Review boundary

This is instructor guidance for a fictional paper exercise. The script checks declarations, not AWS service semantics or live control effectiveness. The output does not establish certification readiness or learner performance. Confirm current AWS behavior, supported resources, service quotas and regional cost before designing an implementation.
