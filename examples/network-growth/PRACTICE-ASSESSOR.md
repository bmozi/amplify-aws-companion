# Address-window reasoning

Read only after the first attempt. These are internal criteria for invented facts, not an AWS sizing approval.

1. Each /26 has 64 total and 59 assignable addresses. Normal occupancy is 37, leaving 22 free and 16 after reserve. Release occupancy is 57, leaving two free: it fits immediate allocation but misses the six-address reserve by four.
2. Combined occupancy is 82. The immediate shortfall is 23; including reserve it is 29. A free address range elsewhere needs a new supported subnet and explicit placement/routing plan; it does not resize the existing subnet.
3. The proposed /25 spans .0 through .127 and overlaps B's .64 through .127. It is not a valid plan retaining both subnets. Reducing overlap changes rollout speed and surviving capacity; moving workloads changes network/dependency and lifecycle requirements. The two unallocated /26-sized ranges in the parent are planning space, not automatically usable capacity.
4. New release occupancy is 25 + 12 + 40 = 77: shortfall 18, or 24 including reserve. With recovery's additional 25, shortfall becomes 43, or 49 including reserve. Re-establish demand from the actual service's interface/address behavior. Bandwidth, quotas, packet rate, customer correctness and recovery remain separate checks.

Source: [AWS subnet sizing](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html). BYOIP and IPv6 are outside these stipulated rules. No measured account configuration or price is implied.
