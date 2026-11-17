# Assessor notes — network route cost

The local result is an intentionally bounded comparison, not a real quote.

- Same-Region VPC-to-S3 traffic can use an S3 gateway endpoint with no endpoint fee if route-table, DNS and policy details suit the workload. That statement does not claim that every associated service or transfer component is free.
- The sample S3 NAT path totals 68.850 invented teaching points (32.850 fixed plus 36.000 processed-data points). The gateway endpoint's endpoint-specific total is zero in this simple comparison. A real bill can contain other transfer and service components.
- At 100 GiB, the sample NAT path is 37.350 points and the two-AZ interface endpoint is 44.800 points. At 500 GiB, the sample NAT path is 55.350 points and the interface endpoint path is 48.800 points. The crossover follows the sample rates only. It is not a universal volume threshold or measured AWS observation.
- The engineer must show eligibility before price: destination service and Region, route target, endpoint support, DNS, permissions, security groups, availability design and caller path. A private endpoint is not a cheaper substitute for every public service or arbitrary internet destination.
- A cross-AZ reduction does not justify removing a failure zone from a workload that requires it. Use actual AZ placement, byte counts, service-specific rates and recovery constraints.
- VPC peering is direct and non-transitive. A Transit Gateway may simplify many-to-many routing or segmentation but adds attachment-hour and processing charges. Count who pays when the network is shared.
- The exercise is successful when a learner can explain path eligibility, fixed and variable billing, missing components and the business constraint that might reverse a cheaper-looking answer. It is not a calibrated certification item and no learner response has been collected.
