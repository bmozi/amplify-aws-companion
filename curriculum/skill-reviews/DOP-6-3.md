# DOP-C02 task 6.3 skill review

Each official skill now has individual teaching and assessment evidence. Coverage remains partial because the companion is synthetic/local, no service is configured, and no independent review is recorded.

| Skill | Teaching and assessment evidence | Remaining evidence |
| --- | --- | --- |
| Implement robust security auditing | Unit 31 compares audit sources and their boundaries; E27 requires exact account, Region, resource, event time, observation time and source coverage. The local join has negative controls for mismatched scope and time. | Verify actual recorder and detector configuration, selected event categories, retention, permissions, delivery and evidence integrity in a separately authorized bounded run. |
| Configure alerts for unexpected or anomalous security events | Unit 31 teaches condition, owner, target, positive/near-match tests, delivery failure and the next read-only step. E27 and the local fictional predicate exercise severity/category/environment/account/Region matching and rejection. | No AWS alert exists. Test a selected service's real event shape, rule, destination permissions, retries/failure path, current price and owner response. |
| Configure service and application logging, including CloudTrail and CloudWatch Logs | Unit 08 explains collection routes, CloudWatch Logs, metric filters, retention and cost; Unit 31 adds audit event categories and safe selector changes. E27 requires a design, but no logging configuration was made. | Verify selected categories, application coverage, access, retention, completeness, delivery and current cost. |
| Analyze logs, metrics and security findings | Unit 08 teaches cross-source signal interpretation; Unit 31 adds artifact, finding, detector and incident boundaries. The lab joins exact synthetic account/Region/resource/time/source records, reports exclusions and preserves incomplete coverage as unknown. | Analyze selected live records and metrics with verified schema, query scope, missing-data behavior, permissions and price; obtain independent technical and learner review. |

Source: [official DOP-C02 Domain 6 task 6.3](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain6.html#dop-02-task-6-3), checked 2026-10-19. No organization or multi-account lab was created.
