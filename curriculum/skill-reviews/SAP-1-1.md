# SAP-C02 task 1.1 skill review

All five current official skills have **partial design-focused evidence**, not deployed or learner-validated performance. This is the transitional [SAP-C02 task 1.1](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain1.html#solutions-architect-professional-02-domain1-task1), checked 2026-10-19. SAP-C03 requires a separate remapping.

| Skill | Teaching and assessment evidence | Remaining evidence |
| --- | --- | --- |
| 1. Evaluate multiple-VPC connectivity | Unit 18 compares direct non-transitive peering with a segmented transit hub; the topology packet asks for a two-VPC decision and a changed third-VPC case. | No peering, hub attachment, route propagation, traffic or failure test was run. |
| 2. Evaluate on-premises, co-location and cloud integration | Unit 18 compares public HTTPS, VPN, Direct Connect and service-scoped access. The co-location case asks which path actually reaches a private endpoint. | No provider circuit, tunnel, endpoint, regional quote or measured capacity/failover result exists. |
| 3. Select Regions and AZs from network and latency needs | Unit 18 names customer/office paths, data-location requirements and zonal failure scope. The East/West packet requires evidence before a location decision. | No measured end-to-end latency, service availability check, approved data-location constraint or zonal failure test. |
| 4. Troubleshoot traffic flows with AWS tools | The evidence ladder and network-evidence case distinguish modeled reachability, DNS, Flow Logs and application result, rejecting unsupported inferences from `ACCEPT` or absent records. | No live Flow Logs, Resolver logs, Reachability Analyzer or Transit Gateway route analysis was run. |
| 5. Use service endpoints for integrations | Unit 18 explains the interface endpoint/service pattern, its connection permission versus API authorization and the office-to-endpoint missing path. The connection and co-location cases change client location. | No endpoint service, private DNS, permissions, protocol integration or application call was tested. |

The authored assessor notes permit justified alternatives while requiring the complete path, permission boundary and cost inventory. Independent technical assessment and learner transfer remain pending.
