# Individual-skill review: SAA-C03 task 1.2

Internal editorial review, October 18, 2026. The [official task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain1.html#solutions-architect-associate-03-domain1-task2) lists four skills. IDs below are our positional identifiers. The labels are paraphrases, not a reproduction of the exam guide. All four remain partial; no learner assessment has occurred.

## Four changed-case prompts

### Skill 01 — Combine network controls

The application connection times out after a subnet ACL change, although the security group allows the service port. Draw both directions and identify the next read-only check. Then explain why a more permissive security group might not fix the failure.

Look for: actual route association, destination, listener and return traffic; distinction between stateful resource rules and stateless subnet rules. Unit 5 explains these boundaries. The loopback exercise performs actual HTTP requests but its routing component is a model. No VPC rule deployment or AWS return-path experiment is evidenced.

### Skill 02 — Segment by required communication

A team calls a subnet private while requiring its workers to download supplier data. Propose the necessary paths and explain how database access differs from worker egress. Change the constraint: only one supported AWS service is needed.

Look for: actual routes and endpoint capabilities rather than names; source/destination/port requirements, DNS and cost; no automatic NAT gateway prescription. Unit 5 now walks a customer through public ALB → private application → private database and separates the worker's S3 gateway-endpoint path from its public supplier egress. The [segmentation contract](../../examples/segmentation-contract/README.md) has a narrow original figure, first-answer prompts and seven executable local cases: one required/forbidden baseline, missing supplier route, missing ACL return, three distinct S3 permission removals and an unwanted worker-to-DB opening. The [assessor](../../examples/segmentation-contract/ASSESSOR.md) challenges rule widening and route-versus-permission conclusions. This is stronger **partial** teaching and symbolic negative-control evidence, not a deployed multi-tier VPC, endpoint or effective AWS policy. The local model omits CIDR route priority, ephemeral port/rule ordering, IAM evaluation and actual network packets. Selected account/Region cost, positive and negative real requests and independent learner review remain open.

### Skill 03 — Combine application protections

A firewall accepts a request for another customer's invoice. Separately, half the workers fail after a supplier credential changes. Identify the enforcing component for each problem and the observations needed to resolve it. Explain what a WAF Count rule does during evaluation.

Look for: record authorization distinct from request filtering; stored secret versus target credential versus cached consumer value; safe diagnostics and bounded recovery. Units 5 and 6 explain these gaps. Unit 6's federation section supplies a separate workforce context. The [credential lifecycle lab](../../examples/credential-rotation/README.md) demonstrates sequential local retrieval and target authentication, including rejection and bounded recovery. The [layered request lab](../../examples/layered-request-boundary/README.md) makes Count, Block, early Allow and record ownership observable as separate local decisions. Neither lab implements AWS secret rotation, WAF or an integrated AWS security-service path. Unit 31 adds service distinctions, evidence scope and seven finding-review cases; actual service coverage and investigation evidence remain pending.

### Skill 04 — Secure the external path

A company proposes Direct Connect and assumes its traffic is encrypted. Its two VPN tunnels also share one office router. Explain confidentiality and availability separately, then add overlapping address ranges and private DNS to the design.

Look for: explicit encryption requirements, shared failure dependencies, request and return routes, address planning and resolver paths. Unit 18 and the hybrid design exercise support the discussion; no physical circuit, VPN configuration, failover measurement or DNS integration has been demonstrated.

## Knowledge-list check and disposition

The task's six knowledge areas now have individual partial evidence records in the [knowledge review](../knowledge-reviews/SAA-1-2-knowledge.md). It links the existing credential/configuration, endpoint, traffic, application-access, security-service and threat teaching to a five-case [learner route](../../examples/application-security-foundations/README.md). The service-selection objective retains its earlier record. External attack-specific defenses, selected feature configuration and actual detection/discovery evidence remain incomplete; learner results are pending. This is not a completed task or knowledge objective.

The task-level map previously hid the absence of substantive secret-rotation and layered web-protection teaching. Added those explanations and diagrams, while preserving the distinction between design, local behavior and AWS evidence. The four skill records remain partial. For assessment, supply prompts without these rationales and record an unaided answer plus a changed constraint. No independent participant results exist.
