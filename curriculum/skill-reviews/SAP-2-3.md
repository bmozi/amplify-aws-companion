# SAP-C02 task 2.3 skill review

The six skills in the transitional [official security-control task](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain2.html#solutions-architect-professional-02-domain2-task3) have **partial design-focused mappings**, checked October 19, 2026. Configuration and implementation are still unproved.

| Skill | Teaching and changed-case evidence | Still needed |
| --- | --- | --- |
| 1. Least privilege | Unit 06's effective-authority lesson and exact object/role/key cases name positive and adjacent denials. | Selected effective policies and real allow/deny observations. |
| 2. Network flows | Unit 31's layered path and custom-ACL return case separate subnet and resource rules. | Selected route/SG/ACL configuration and packet-path test. |
| 3. Web attack mitigation | Unit 05's WAF/Shield boundary and bypass/shared-IP case test scope and legitimate impact. | Effective selected WAF/origin/capacity behavior and cost. |
| 4. Encryption | Unit 19's TLS/storage/key separation and decrypt-denial case specify independent gates. | Actual certificate, object/key path, backup and recovery checks. |
| 5. Endpoints | The endpoint-path case rejects the idea that an endpoint policy grants IAM or controls alternate routing. | Supported selected endpoint, DNS, route and policy observations. |
| 6. Patch management | Unit 31 and the EC2 import-node case separate host compliance, next image and application dependencies. | Selected node/image/dependency coverage, replacement test and rollback. |

The [packet](../../examples/professional-control-path/README.md) and [assessor](../../examples/professional-control-path/ASSESSOR.md) have no independent learner result. No AWS account was changed.
