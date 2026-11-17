# DOP-C02 task 6.2 knowledge review

This review maps each current official knowledge bullet to its teaching and assessment evidence. The mappings are partial: no AWS service was enabled or inspected, no organization was created, and no independent technical or learner review is recorded.

| Knowledge point | Teaching and assessment evidence | Remaining evidence |
| --- | --- | --- |
| Network security components: security groups, network ACLs, routing, Network Firewall, WAF and Shield | Unit 31 explains where each acts, state/return behavior and service boundaries; its original figure traces a request. E26 asks for a request and failure path; the local matrix demonstrates scope bookkeeping only. | Validate a selected real path, resource support, rule order, failure behavior and current regional price in an authorized design; no packet was sent through an AWS control. |
| Certificates and PKI | Unit 31 distinguishes TLS endpoint identity, ACM certificate types/renewal, key custody and transit from storage encryption; Unit 19 teaches certificate validation and TLS boundaries. E26 adds certificate, renewal and recovery prompts. | No ACM certificate, private CA, endpoint, renewal or PKI trust chain was provisioned or tested. |
| Data management: classification, encryption, key management and access controls | Unit 31 covers classification, least privilege, Macie's S3 scope/sampling, KMS key control and CloudHSM's operational tradeoffs; Unit 19 adds encryption and recovery. E26 follows an object from intake to restored copy. | No real classification, data access review, key policy, Macie coverage or decryptable restore was observed. |

The current source is the [official DOP-C02 Domain 6 objective](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain6.html#dop-02-task-6-2), checked 2026-10-19. This documents intended partial coverage only; it does not establish exam readiness.
