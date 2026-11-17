# Assessor guide — throttling strategy

## Reasoning boundaries

- **Public search:** API Gateway stage/method throttling can target a steady rate and burst for the API. Protect the downstream service separately with a bounded queue or shared admission control if that is the scarce resource. Per-IP WAF limiting risks combining legitimate users behind the carrier IP. Use bounded client retries only when repeated search is safe, and measure both `429`s and downstream saturation.
- **Login abuse:** A scoped AWS WAF rate-based rule can group relevant web requests and slow repeated traffic before it reaches the origin. Select aggregation keys and scope carefully: IP rotation can defeat only-IP grouping, while overly broad keys can throttle legitimate users. Authentication, account lockout, bot controls and safe credential handling remain separate controls. WAF's estimate and mitigation timing are not exact.
- **Shared export database:** A process-local concurrency limit is not a global limit. If each of eight replicas admits two exports, as many as sixteen can be admitted. Use a shared semaphore/queue or another control whose boundary matches the shared database capacity; bound waiting work and define reject/defer behavior. WAF or API Gateway limits can reduce ingress but do not by themselves express database capacity.
- **Paid image API:** AWS Budgets can notify on an estimate or actual-spend threshold; it does not reject paid requests or guarantee a maximum bill. If the product needs a hard business allowance, enforce a ledger-based customer/account quota before accepting chargeable work, handle races and retries, and set a separate bounded infrastructure admission control. Model costs and verify budget notifications independently.

Good answers name rate, burst, time window, aggregation key and shared boundary, explain `429`/queue/retry behavior, account for legitimate batch use, and measure both protected-resource health and customer harm. A control is not successful merely because its counter increased.

The exercise has no deployed API, web ACL, database, budget, cost estimate or observed learner result. AWS documentation checked October 18, 2026 describes API Gateway and WAF throttling as approximate/best-effort controls; verify current service details and limits for any real design.
