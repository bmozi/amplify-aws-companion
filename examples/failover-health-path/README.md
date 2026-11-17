# A route is not a recovered booking

Follow the [illustrated lesson](../../reader/BOOK-LOCATORS.md#book-caa0fef97a6b2759) and [E05](../../curriculum/EXERCISES.md#e05). Answer the six changed cases before reading the [assessor notes](ASSESSOR.md). This original paper-and-local drill makes no AWS calls.

From the repository root:

```sh
python3 examples/failover-health-path/lab.py
python3 -m unittest discover -s examples/failover-health-path -p 'test_*.py' -v
```

The model accepts a **fictional** primary/secondary Route 53 failover pair with a health check on each, one selected ALB target group, supplied healthy-target states, one known cached-primary client, and supplied booking evidence. It encodes only the documented DNS record choice and ALB all-unhealthy target choice. Its “reopen all” value is a conservative teaching gate for these supplied facts, not an AWS readiness probe or a guarantee for every client. It does not model health-check timing, alias trees, DNS TTLs/resolver policies, target weights, load balancing, RDS failover, real customer traffic, account permissions or prices.

| Case | Changed condition | Decide before reading the assessor |
| --- | --- | --- |
| 1. One location fails | Primary check is unhealthy; secondary check and one selected ALB target are healthy. Surviving useful capacity is 90 bookings/minute for 80 arrivals. Old/new booking, writer and tenant-denial checks passed. | Which location does a **new** DNS lookup receive? Which target can the ALB select? What evidence permits reopening under these supplied facts? |
| 2. Stale resolver | Same as case 1, but a known client still holds the primary DNS answer. | Can an operator claim all clients have moved? What observation and client behavior need review? |
| 3. Both DNS checks fail | Secondary check also becomes unhealthy. | Which answer can Route 53 return for this checked failover pair? Why is receiving an answer not proof of service? |
| 4. All ALB targets fail | Selected target group has two registered targets and both checks fail. | Which targets may still receive traffic? Where must unsafe booking writes be blocked? |
| 5. AZ survivor shortfall | A failed AZ leaves useful app capacity of 55 bookings/minute for 80 arrivals, though the data standby and a health URL look available. | What is the shortfall? Can routing or a Multi-AZ DB instance standby solve it? Distinguish accepted from confirmed work. |
| 6. Wrong recovery receipt | Target and data failover report success, but booking 111 was not read after the switch and a Bob-for-Alice denial test is missing. | Which customer/authorization checks prevent reopening? What could a green health URL miss? |

## Follow three resolver clocks

The separate timed model adds the missing **TTL arithmetic** to the same recovery story. It does not change the six-case failover model above. First, calculate the answer and expiry for A, B and C in the [chapter timeline](../../reader/BOOK-LOCATORS.md#book-d1aaaa6d6f31c7d1). Then run:

```sh
python3 examples/failover-health-path/cache_timeline.py
python3 -m unittest discover -s examples/failover-health-path -p 'test_cache_timeline.py' -v
```

The supplied authoritative answer switches at second 100. A fetched primary at second 0, B at 80, and C first asks at 110. The old TTL is 300 seconds. At second 120, the **TTL attached to future authoritative responses** becomes 30 seconds. The model shows a fresh C receiving standby while A and B still use primary, A refreshing at 300, and B returning primary at 379 before refreshing at 380. The program records whether each result came from the cache or a new authoritative lookup.

Before reading the [assessor](CACHE-TIMELINE-ASSESSOR.md), answer four changed cases: (1) Why do A and B disagree with C at 110? (2) Why does lowering TTL at 120 not move B at 121? (3) What changes if B's **original** response at 80 carried a 30-second TTL? (4) Can the team claim all customers have moved at 380, or only that these three idealized resolvers agree?

The source uses only Python's standard library and no network or AWS credentials. It assumes compliant resolvers, immediate knowledge of the supplied authoritative answer and integer-second lookups. It does not model Route 53 health-check detection, DNS propagation, alias TTLs, resolver overrides, application DNS caches, persistent connections, ALB or data recovery. A cache result is not proof of a successful customer booking. AWS's [TTL troubleshooting](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/troubleshooting-new-dns-settings-not-in-effect.html) and [DNS practices](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/best-practices-dns.html) support the conceptual distinction; the exact seconds and three clients are fictional.

Before any real drill, select the exact resource, account and Region. Review scoped non-root identity, current feature behavior, a complete account-specific estimate, a spending limit and reserve, a stop condition, cleanup and delayed billing reconciliation. The organization-dependent variations remain design-only. Ask Codex to challenge one missing receipt, then verify its service-specific answer against the cited AWS documentation.
