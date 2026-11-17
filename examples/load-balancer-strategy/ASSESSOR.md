# Assessor notes: load-balancer strategy

These notes show defensible reasoning, not a unique bill or exam answer.

## Expected starting choices

- **HTTP path routing:** ALB can inspect HTTP host/path conditions and route to target groups. NLB's transport-flow selection does not inspect URL paths. GWLB's purpose is network-appliance insertion, which this workload did not request.
- **Proprietary UDP plus stable zonal addresses:** NLB is the candidate. Verify protocol/port support, address allocation, target compatibility, health checks, Availability Zone design and the partner's exact allowlist behavior. ALB's application-aware HTTP routing does not fit UDP. GWLB does not replace the application's transport entry point.
- **Inline virtual firewall fleet:** GWLB supports transparent network-layer appliance distribution and flow stickiness. The answer must include appliance targets, GENEVE compatibility, endpoint and route-table placement, return-path symmetry/flow behavior, health, scaling, patching, licensing and cross-zone/data-transfer cost. ALB or NLB alone do not insert the required firewall fleet.

## Cost reasoning

Start with eligibility, then estimate each eligible design using the intended Region and measured or explicitly labeled assumed workload. Separate hourly load-balancer charges from the applicable usage unit (LCU, NLCU or GLCU). For GWLB, count each endpoint and its traffic charges separately, then include appliance compute/software, target capacity, transfer, logs and operational work. Consider how Availability Zone count, cross-zone settings, connection lifetime, bytes, rules and peak versus average load affect the estimate. Confirm current AWS pricing; do not paste an old sample rate into a current business case.

The cost-optimal design can change when a required feature changes. Removing path-based routing may change the ALB decision. Removing inline inspection may remove GWLB and appliance costs, but only after security owners accept an alternative and evidence its coverage. Adding more VPC consumers changes endpoint and traffic counts. A fixed entry address alone does not automatically justify stacking load balancers: articulate the interface and partner constraint, test the proposed chain, and account for both services.

## Evidence boundary

This paper case assesses conceptual selection and complete-cost inputs. It does not validate a real protocol, packet path, appliance, Terraform plan, route table, availability outcome, exact price or customer requirement. No AWS resources were created. Independent learner answers and technical review remain necessary before treating the lesson as effective or complete.
