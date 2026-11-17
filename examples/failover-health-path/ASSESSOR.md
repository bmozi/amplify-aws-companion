# Assessor reasoning for the failover health path

Read after an independent first attempt. The model is a teaching simplification and creates no AWS evidence.

1. **One location:** New DNS lookups receive secondary. The selected ALB routes to target 1. Under the supplied fictional facts, the local gate permits reopening. In a real run, observe DNS/client populations and complete booking behavior rather than promoting a local Boolean result to a service guarantee.
2. **Stale resolver:** The known client can still use its primary answer, so “all clients moved” is unsupported. Inspect TTL, resolver and actual client retry/reconnect behavior; route controls do not force an old connection to change.
3. **Both DNS checks fail:** For this checked primary/secondary failover pair, Route 53 returns primary as its last-resort answer. An address can lead to an unhealthy service. Review the record hierarchy and health check configuration before assuming a particular real response.
4. **All ALB targets fail:** ALB can fail open and route to both registered unhealthy targets. Authorization and safe booking admission belong in the application/data path, not in an ALB health check.
5. **AZ shortfall:** 80 − 55 = 25 bookings/minute lack supplied immediate capacity. A DNS answer cannot create workers; an RDS Multi-AZ DB instance standby is for data failover, not an app worker or ordinary read replica. Bound, reject or durably defer work according to its acceptance contract and observe queue age and completions.
6. **Wrong receipt:** Verify the prior confirmed booking and a new booking after the switch, writer authority and cross-tenant denial. A green target path can still write to the wrong data authority or disclose another tenant's record.

The tests cover the two documented all-unhealthy selection cases, survivor shortfall, cached-primary client and missing customer/authorization evidence. They do not configure DNS, ELB or RDS; run health checks; measure RTO/RPO; establish current cost; or validate a learner independently.
