# Diagnostic assessor — open only after first submission

Original item reasoning, internally reviewed only. An AWS-qualified independent reviewer has not approved these items. Accept a documented ambiguity report and repair the item; do not mark a learner wrong for a defensible reading of insufficient facts. No raw percentage maps to the AWS scaled score.

## SAA-D01 — task 1.1

Expected selection: **B**.

- **A:** A shared key loses individual attribution and does not meet the temporary-credential requirement.
- **B:** Federation with scoped account access meets the stated workforce and temporary-access needs; permissions and session controls still require configuration.
- **C:** Application sign-in alone does not grant or govern administrative access to the target AWS accounts.
- **D:** Individual keys improve attribution over a shared user but still violate the stated requirement to avoid distributing long-lived keys.

Remediation: [task 1.1 work card](../tasks/1-1.md). Technical references: [source 1](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html), [source 2](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).

## SAA-D02 — task 1.1

Expected selection: **C**.

- **A:** A boundary does not override an applicable SCP explicit deny.
- **B:** An applicable explicit deny is not overridden by an identity allow.
- **C:** The stated explicit deny controls this case. A legitimate policy change requires the responsible administrator, not an extra allow.
- **D:** A broader identity policy still cannot override the stipulated applicable explicit deny.

Remediation: [task 1.1 work card](../tasks/1-1.md). Technical references: [source 1](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html), [source 2](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html).

## SAA-D03 — task 1.2

Expected selection: **A**.

- **A:** The security-group reference restricts the network source for the specified port; application authorization remains separate.
- **B:** A VPC-wide source permits more sources than the required ALB-only boundary.
- **C:** Subnet ranges include other possible callers and do not express the specific ALB security-group boundary.
- **D:** An outbound rule does not authorize the ALB to initiate the required inbound connection.

Remediation: [task 1.2 work card](../tasks/1-2.md). Technical references: [source 1](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-update-security-groups.html), [source 2](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html).

## SAA-D04 — task 1.2

Expected selection: **A, D**.

- **A:** WAF addresses selected HTTP request patterns; rule tuning and application security are still needed.
- **B:** A security group filters network traffic by its supported attributes; opening HTTPS does not inspect malicious HTTP payload patterns.
- **C:** DNS health checks observe endpoint health; they do not filter each application request body.
- **D:** Secrets Manager addresses secret storage and controlled retrieval; rotation must be integrated with consumers.
- **E:** Repository privacy does not satisfy the requirement to keep credentials out of source.

Remediation: [task 1.2 work card](../tasks/1-2.md). Technical references: [source 1](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-update-security-groups.html), [source 2](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html), [source 3](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html).

## SAA-D05 — task 1.3

Expected selection: **D**.

- **A:** Default bucket encryption controls new writes; changing it does not re-encrypt this existing object or supply its missing decrypt permission.
- **B:** Permission to encrypt does not supply permission to decrypt the existing ciphertext.
- **C:** A presigned request uses the signing principal's authorization; the stipulated signer also lacks the decrypt authority needed for this object.
- **D:** The stated missing gate is KMS decrypt authorization. Review the applicable key and identity permissions, retain the approved scope and verify the actual allowed and denied paths.

Remediation: [task 1.3 work card](../tasks/1-3.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html), [source 2](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html), [source 3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html).

## SAA-D06 — task 1.3

Expected selection: **B, C**.

- **A:** Lower lag can improve freshness and some failover outcomes, but the replica has already copied this deletion. It does not supply the required earlier state.
- **B:** Recovering the specified earlier state requires usable history covering the detection window, including authority and key dependencies.
- **C:** A separate restore, reconciliation and customer check test recoverability and correct use before changing the serving destination.
- **D:** Faster promotion addresses availability of the current copy, not restoration of the historical records that are already deleted from that copy.
- **E:** Replacing the only daily snapshot during the detection interval can remove the needed pre-deletion history; a recent snapshot is not necessarily the required one.

Remediation: [task 1.3 work card](../tasks/1-3.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html), [source 2](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html).

## SAA-D07 — task 2.1

Expected selection: **C**.

- **A:** This couples acceptance to worker availability and repeats potentially completed effects without a durable identity contract.
- **B:** Process-local memory is not durable buffering and can lose acknowledged work when an instance is replaced.
- **C:** The queue separates rates, while idempotent effect handling addresses duplicate delivery; acceptance and dispatch must still be made reliable.
- **D:** Broker deduplication does not establish exactly-once external effects across every consumer crash and retry boundary.

Remediation: [task 2.1 work card](../tasks/2-1.md). Technical references: [source 1](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html), [source 2](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html).

## SAA-D08 — task 2.1

Expected selection: **A, E**.

- **A:** Separate subscriptions and queues allow independent consumption and retained backlog; configure permissions and retention for the case.
- **B:** Competing consumers divide messages; they do not implement the required copy for each consumer.
- **C:** The requirement explicitly tolerates consumer outages, so discarding events violates it.
- **D:** More web capacity does not supply fanout or durable event retention.
- **E:** Independent failure handling and reconciliation address failures beyond mere publication.

Remediation: [task 2.1 work card](../tasks/2-1.md). Technical references: [source 1](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues.html), [source 2](https://docs.aws.amazon.com/sns/latest/dg/sns-sqs-as-subscriber.html).

## SAA-D09 — task 2.2

Expected selection: **B**.

- **A:** This confuses the single-standby DB instance topology with other readable replica or cluster arrangements.
- **B:** This is the documented boundary for the topology explicitly named in the question.
- **C:** Multi-AZ and multi-Region describe different failure scopes.
- **D:** Clients still need appropriate reconnection and uncertain-operation handling.

Remediation: [task 2.2 work card](../tasks/2-2.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html).

## SAA-D10 — task 2.2

Expected selection: **D**.

- **A:** The supplied times violate both limits regardless of price.
- **B:** Possessing a backup does not meet the stated time and loss bounds.
- **C:** The supplied warm-standby result meets both limits; active-active is not a universal requirement.
- **D:** Twelve is within twenty and three is within five; representativeness remains a real-world qualification.

Remediation: [task 2.2 work card](../tasks/2-2.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html).

## SAA-D11 — task 3.1

Expected selection: **C**.

- **A:** Matching path names on separate volumes do not create a shared namespace.
- **B:** EBS Multi-Attach is constrained to eligible instances in the same AZ and is not the required cross-AZ managed NFS service.
- **C:** EFS matches the interface and regional shared-access need; throughput, access and client behavior must still be checked.
- **D:** Object APIs and filesystem semantics are not interchangeable without a compatible access layer and workload assessment.

Remediation: [task 3.1 work card](../tasks/3-1.md). Technical references: [source 1](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html), [source 2](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html), [source 3](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes-multi.html).

## SAA-D12 — task 3.1

Expected selection: **A**.

- **A:** The object interface and failure requirement guide the class choice; retrieval and lifecycle still matter.
- **B:** One ephemeral local copy does not meet the stated persistence and failure requirement.
- **C:** Single-AZ and multi-AZ classes have materially different location-loss boundaries.
- **D:** A connection proxy is not an object storage system.

Remediation: [task 3.1 work card](../tasks/3-1.md). Technical references: [source 1](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html), [source 2](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html).

## SAA-D13 — task 3.2

Expected selection: **B**.

- **A:** Unbounded consumers can overload the existing downstream limit.
- **B:** Backlog and service rate describe the demand; concurrency limits preserve the constrained downstream path.
- **C:** An instance size alone does not establish end-to-end sustainable capacity.
- **D:** Connections consume resources and do not guarantee more database work can complete.

Remediation: [task 3.2 work card](../tasks/3-2.md). Technical references: [source 1](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), [source 2](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html).

## SAA-D14 — task 3.2

Expected selection: **D**.

- **A:** The standard event-function timeout is at most 900 seconds. Managed Instances has a different documented limit for selected invocation modes; neither fact permits the proposed two-hour standard invocation.
- **B:** A cache policy does not execute a two-hour container job.
- **C:** An identity does not supply compute.
- **D:** A managed container task is a suitable candidate for the given execution shape; failure and cost remain design inputs.

Remediation: [task 3.2 work card](../tasks/3-2.md). Technical references: [source 1](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html), [source 2](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html).

## SAA-D15 — task 3.3

Expected selection: **A**.

- **A:** The paths have different freshness and correctness promises; replica suitability depends on observed lag and routing.
- **B:** Asynchronous replication does not guarantee an immediately current decision.
- **C:** A stale cached display cannot enforce the last-item invariant.
- **D:** Read replicas can offload eligible reads but do not automatically multiply writer capacity.

Remediation: [task 3.3 work card](../tasks/3-3.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html), [source 2](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html).

## SAA-D16 — task 3.3

Expected selection: **C, D**.

- **A:** Connection management does not guarantee query-plan improvement.
- **B:** An uncertain write remains an application correctness concern.
- **C:** Pooling is the relevant benefit; compatibility and session pinning must be evaluated.
- **D:** These are distinct responsibilities that remain after adding a proxy.
- **E:** A connection proxy is not a backup archive.

Remediation: [task 3.3 work card](../tasks/3-3.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html), [source 2](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html).

## SAA-D17 — task 3.4

Expected selection: **B**.

- **A:** Listener ports do not implement the requested application path-based target-group rules.
- **B:** ALB supports application-layer routing matching this requirement.
- **C:** Transport-layer balancing alone does not implement the required HTTP path decision.
- **D:** Port-based separation is not selection by HTTP URL path.

Remediation: [task 3.4 work card](../tasks/3-4.md). Technical references: [source 1](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html), [source 2](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html).

## SAA-D18 — task 3.4

Expected selection: **A, B**.

- **A:** Client VPN addresses remote client access; routes, authorization and authentication must be configured.
- **B:** Site-to-Site VPN connects networks; redundancy and routing must meet the branch requirement.
- **C:** A routing hub alone does not create the requested remote-client VPN termination and authentication.
- **D:** VPC peering connects VPCs; it is not the office-to-AWS VPN tunnel.
- **E:** The stated laptop client use fits Client VPN; Site-to-Site VPN connects networks through a customer gateway.

Remediation: [task 3.4 work card](../tasks/3-4.md). Technical references: [source 1](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html), [source 2](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/what-is.html), [source 3](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html).

## SAA-D19 — task 3.5

Expected selection: **C**.

- **A:** Compression may reduce bytes but does not supply columnar projection or date partition pruning.
- **B:** More frequent scans do not remove unnecessary columns or date ranges from each query.
- **C:** Columnar storage and useful partitioning can reduce scan work; correctness and actual query behavior must be verified.
- **D:** Concurrency changes scheduling, not which columns and partitions each query needs to read.

Remediation: [task 3.5 work card](../tasks/3-5.md). Technical references: [source 1](https://docs.aws.amazon.com/athena/latest/ug/columnar-storage.html), [source 2](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html), [source 3](https://docs.aws.amazon.com/athena/latest/ug/performance-tuning-data-optimization-techniques.html).

## SAA-D20 — task 3.5

Expected selection: **D**.

- **A:** Kinesis has its own APIs; retaining Kafka clients unchanged is not the supplied compatibility path.
- **B:** RabbitMQ protocols and behavior are not interchangeable with the required Kafka broker interface.
- **C:** SQS queue APIs do not expose the required Kafka broker protocol.
- **D:** MSK is the managed Kafka candidate; capacity, security, compatibility and cost still need design.

Remediation: [task 3.5 work card](../tasks/3-5.md). Technical references: [source 1](https://docs.aws.amazon.com/athena/latest/ug/columnar-storage.html), [source 2](https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html).

## SAA-D21 — task 4.1

Expected selection: **B**.

- **A:** The mandatory access requirement must be met before comparing prices.
- **B:** First establish feasible classes; then compare complete cost for the actual access pattern.
- **C:** A design cannot silently discard the supplied requirement.
- **D:** The exact class matters; branding alone is not a retrieval guarantee.

Remediation: [task 4.1 work card](../tasks/4-1.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html).

## SAA-D22 — task 4.1

Expected selection: **A, E**.

- **A:** These meters can materially change the cost of small and frequently accessed objects.
- **B:** Early movement or deletion does not universally erase minimum-duration charges.
- **C:** Retained bytes remain part of the workload.
- **D:** Actual encryption and transfer paths must be evaluated rather than universally omitted.
- **E:** The storage policy and copy topology determine more than the current-object byte count.

Remediation: [task 4.1 work card](../tasks/4-1.md). Technical references: [source 1](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html).

## SAA-D23 — task 4.2

Expected selection: **A**.

- **A:** The stated restart and deadline flexibility make interruptible capacity a candidate; availability and fallback remain relevant.
- **B:** A commitment to an unverified peak can leave paid capacity unused and is not justified by flexible interruptible work alone.
- **C:** On-Demand can be a useful fallback but does not eliminate failures or the need for recovery.
- **D:** The cost opportunity depends on tolerating interruptions; removing the stated recovery mechanism weakens that suitability.

Remediation: [task 4.2 work card](../tasks/4-2.md). Technical references: [source 1](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html), [source 2](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html).

## SAA-D24 — task 4.2

Expected selection: **C**.

- **A:** Unused committed spend remains a risk.
- **B:** Billing discounts and capacity reservations are different mechanisms.
- **C:** The evidence supports the baseline more strongly than the unknown peak; eligibility, term and break-even still need checking.
- **D:** Commitment scope and flexibility depend on the specific purchasing instrument.

Remediation: [task 4.2 work card](../tasks/4-2.md). Technical references: [source 1](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html), [source 2](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html).

## SAA-D25 — task 4.3

Expected selection: **D**.

- **A:** A lower rate does not establish that required engine-specific behavior can migrate unchanged.
- **B:** Matching counts do not test stored procedures, extensions or business-result parity.
- **C:** Managed operation does not eliminate conversion, compatibility, testing or cutover work.
- **D:** The cheaper engine could create a larger conversion and correctness burden; compare feasible total-cost options.

Remediation: [task 4.3 work card](../tasks/4-3.md). Technical references: [source 1](https://docs.aws.amazon.com/decision-guides/latest/decision-guides/databases-on-aws-how-to-choose.html).

## SAA-D26 — task 4.3

Expected selection: **B, C**.

- **A:** Each selected service and feature has its own relevant pricing scope.
- **B:** The complete topology must be represented in the estimate.
- **C:** Capacity and billing depend on how the actual workload uses the selected database.
- **D:** Cost optimization must retain the required recovery promise.
- **E:** An average can hide the peak and other constrained resources.

Remediation: [task 4.3 work card](../tasks/4-3.md). Technical references: [source 1](https://docs.aws.amazon.com/decision-guides/latest/decision-guides/databases-on-aws-how-to-choose.html).

## SAA-D27 — task 4.4

Expected selection: **C**.

- **A:** This may address cross-AZ traffic but retains NAT processing for the S3 path.
- **B:** An interface endpoint has its own pricing; this comparison omits relevant endpoint and traffic meters when a gateway endpoint is permitted.
- **C:** The gateway endpoint provides the supported S3 route without NAT; service charges and access policy still apply.
- **D:** An access policy alone does not create the gateway endpoint path or redirect the traffic.

Remediation: [task 4.4 work card](../tasks/4-4.md). Technical references: [source 1](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html), [source 2](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-basics.html).

## SAA-D28 — task 4.4

Expected selection: **B**.

- **A:** Fixed price is only one term and does not establish availability.
- **B:** The shared design may introduce a common failure dependency and different transfer costs; compare it against the actual service promise.
- **C:** Route-table count does not measure the end-to-end cost or failure behavior.
- **D:** The design must account for the resource placement and failure scope rather than assume it away.

Remediation: [task 4.4 work card](../tasks/4-4.md). Technical references: [source 1](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html), [source 2](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-basics.html).
