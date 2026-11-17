# SAP-C02 task 2.3 knowledge review

The six knowledge points in the transitional [official security-control task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task3) have **partial** teaching and assessment mappings, checked October 19, 2026. This does not establish SAP-C03 coverage or selected cloud protection.

| Point | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. IAM | Unit 06 explains effective authority; the packet changes exact object, role, key and endpoint permissions. | Selected policy/request-context evaluation and allow/deny evidence. |
| 2. Routes, groups, ACLs | Units 05 and 31 separate route, stateful security group and stateless subnet ACL; the one-way and bypass cases require a return path. | Actual selected topology and observed traffic/failure. |
| 3. Encryption | Unit 19 distinguishes TLS, stored bytes and key access; the readable-ciphertext case tests that separation. | Actual certificate, resource/key policy, data and restore evidence. |
| 4. Service endpoints | Unit 31 explains endpoint policy limits; the packet supplies an alternate route. | Current selected endpoint support, DNS, route and effective permission tests. |
| 5. Credential management | Unit 06 teaches secret/target/consumer rotation; the stale worker case changes all three. | Selected store, supplier and worker rehearsal. |
| 6. Managed security services | Unit 05 separates WAF and Shield; Unit 31 describes scoped security findings and controls. The web-bypass case changes rule scope and legitimate-client grouping. | Selected service scope, actual traffic and current cost review. |

The [seven-case packet](../../examples/professional-control-path/README.md) and [assessor](../../examples/professional-control-path/ASSESSOR.md) are fictional. Existing local drills do not evaluate AWS policy, packet flow or protection services. Independent technical and learner review remains pending.
