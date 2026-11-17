# Leave room to deploy and recover

Run `python3 examples/network-growth/lab.py` from the repository root, without Python optimization. This standard-library exercise makes no network calls and changes no routes. It checks a fictional address plan; it is not an AWS subnet discovery or provisioning tool.

AWS ordinarily reserves five IPv4 addresses per subnet and supports IPv4 subnet prefixes from `/16` through `/28`. This exercise deliberately accepts only canonical RFC 1918 private ranges. It excludes BYOIP and IPv6, which require their own rules. [AWS subnet sizing](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html).

## Predict the pressure before running

A fictional application has one `/25` subnet in each of two zones. Each subnet has 128 total addresses and 123 ordinarily assignable addresses. The fixture assumes 50 active-workload addresses, 20 fixed addresses for other components and a desired reserve of 10. Those are address counts supplied by the exercise, not universal instance, pod, function or endpoint ratios.

| State of one subnet | Active | Replacement | Fixed | Free after occupancy | Margin after 10-address reserve |
| --- | --- | --- | --- | --- | --- |
| Normal | 50 | 0 | 20 | 53 | 43 |
| New version overlaps old version | 50 | 50 | 20 | 3 | -7 |
| Surviving zone takes the other zone's work | 100 | 0 | 20 | 3 | -7 |
| Recovery while 50 replacement addresses remain allocated | 100 | 50 | 20 | -47 | -57 |

A negative free count is unmet demand, not an observed AWS allocation. A negative reserve margin means the stated planning requirement fails even if the immediate addresses fit. The recovery counts assume a particular fictional workload movement; a real service may scale or allocate differently.

The lab also verifies that two adjacent `/25` ranges fill a `/24`. Their combined assignable count is 246, not 251: each subnet pays its own five-address reservation. A `/23` containing those same two subnets leaves 256 addresses of unallocated range. That does not yet mean 256 assignable future addresses; future subnet boundaries bring their own reservations.

```text
Fictional 10.20.0.0/24 parent range
├── 10.20.0.0/25   zone A: 128 total, 123 assignable
└── 10.20.0.128/25 zone B: 128 total, 123 assignable
No unallocated range remains inside this parent.
```

The parent is only an address-planning boundary here. The program does not validate all AWS VPC association rules or the availability of these ranges in an account or connected network.

## Explain the changed case

1. A reviewer sees three free addresses during deployment and approves it. Explain the difference between immediate fit and the stated reserve. **Expected:** immediate occupancy fits, but the ten-address reserve is short by seven.
2. The team proposes expanding the first `/25` to `/24` while retaining the second `/25`. **Expected:** the ranges overlap. The checker rejects that proposed address plan; it is not an in-place AWS subnet resize procedure.
3. Another team counts the other zone's spare addresses as a shared pool. **Expected:** addresses belong to their subnet allocation. A different placement needs an explicit resource and connectivity plan; a failed zone's allocation does not automatically enlarge a surviving subnet.
4. A proposed larger subnet has 251 assignable addresses. **Expected:** this fixture's combined recovery/deployment demand plus reserve is 180, leaving a margin of 71. That arithmetic alone does not authorize a migration or establish throughput, availability, quota or cost suitability.
5. The next version uses extra network interfaces or secondary addresses. **Expected:** rederive address demand from the actual service allocation model. Do not substitute a count of application processes for occupied addresses.

Invalid fixtures cover overlapping, duplicate and out-of-parent ranges, host bits in a CIDR, unsupported address families/prefixes, and negative/non-integer demand. The strict host-bit rejection is an intentional teaching choice; AWS APIs can normalize a supplied IPv4 CIDR. The checker avoids silently changing the reader's intended plan.

Ask Codex to identify peak simultaneous allocations, then challenge it with deployment overlapping a zone failure. Verify every assumed allocation ratio against the chosen service before live use. A later AWS exercise needs reviewed identity, exact resource inventory and performance/quota checks. Choose whole-run spending and reserve limits for the account you will use.
