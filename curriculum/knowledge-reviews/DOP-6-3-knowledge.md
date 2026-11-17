# DOP-C02 task 6.3 knowledge review

This maps each current official knowledge bullet to teaching and assessment evidence. All three maps are partial. The lab uses fictional, already-normalized records; it does not establish AWS service coverage or exam readiness.

| Knowledge point | Teaching and assessment evidence | Remaining evidence |
| --- | --- | --- |
| Audit services and features such as CloudTrail, AWS Config, VPC Flow Logs and CloudFormation drift detection | Unit 31's audit-lens table explains activity, recorded configuration, network metadata and supported-property drift. E27 asks the reader to classify and scope records. | Verify the selected resource types, event categories, Region, retention, permissions and freshness in a bounded live design; compare current end-to-end costs. |
| Services that identify vulnerabilities and events, including GuardDuty, Inspector, IAM Access Analyzer and AWS Config | Unit 31 distinguishes threat detection, vulnerability coverage, policy-access analysis and configuration evaluation; prior finding lessons separate a finding from proof of exploitation. | Verify selected service coverage, analyzer trust boundary, unsupported resources, event delivery and current service/Region behavior. |
| Common threats such as insecure web traffic, exposed access keys, public S3 access and missing encryption | The new “Recognize the threat before choosing the evidence” section separates an exposed condition from observed use and customer impact; E27 requires the evidence needed to substantiate each claim. | Add independent technical and learner review; verify the specific TLS, key lifecycle, public-access and encryption paths in the selected architecture. |

Source: [official DOP-C02 Domain 6 task 6.3](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain6.html#dop-02-task-6-3), checked 2026-10-19. These are partial mappings only.
