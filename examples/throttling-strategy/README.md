# Choose where to throttle

## The challenge

For each case below, identify the resource or customer promise that needs protection, select one primary control and any needed second layer, and explain the boundary, retry behavior, false-positive risk, measurement and rollback plan. Avoid treating every “requests per second” number as the same limit.

All organizations and observations are fictional. This is a design assessment; it uses no credentials, deploys no AWS resources and does not establish the exact behavior or cost of a service setting.

| Case | Situation | Changed fact to consider |
|---|---|---|
| Public search endpoint | A public API has bursty search traffic that can temporarily overwhelm a downstream service. | Most legitimate searches come through a shared mobile-carrier IP. |
| Login form abuse | A public login endpoint receives repeated automated attempts, while ordinary customers must still sign in. | An attacker rotates source IPs, but targets the same path. |
| Shared export database | Several application replicas submit expensive exports to a shared database. | A per-process limit looks safe until the team scales from two replicas to eight. |
| Paid image-processing API | Customers submit paid work and the owner wants the monthly charge never to exceed a budget alert. | A scheduled customer batch causes a short legitimate spike. |

Before checking the [assessor guide](ASSESSOR.md), record the answer to these questions for every case:

1. What exact resource or promise could fail?
2. What does “one request” mean, and who shares a limit?
3. Which control sees enough information to enforce that boundary?
4. What happens to accepted, rejected and retried work?
5. What metric and customer outcome will reveal over-throttling or under-protection?
6. Which setting is only a target or alert, rather than a hard ceiling?

