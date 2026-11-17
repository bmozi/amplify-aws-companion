# Recovery clock: assessor reasoning

This answer applies only to the fictional [local clock](TIMELINE-LAB.md) and its fixture. The HTTP observations are local, not AWS evidence.

1. A healthy candidate endpoint is insufficient while confirmed booking `111` is absent. The customer promise names a correct record, so a 200 health response does not end the clock.
2. For the stated read promise, the first correct read of booking `111` after route change is the local endpoint. The new booking check separately tests whether writes can resume. A different business promise could require both and additional clients or capacity. The measured start is the first observed failed customer request, which may be later than the true failure onset.
3. The old writer must be fenced before the selected route changes in this exercise. The changed case correctly returns `HOLD` after reconciliation, with no measured recovery duration. A cooperative Boolean is not a distributed fence; a real design must demonstrate an effective denial of old writes.
4. The 404 for booking `112` on the returned old path disproves a claim that every client sees the new confirmed work. One pinned request does not measure the size of the affected population or prove every other path safe.

For the changed amount, hold the route and reconcile the authoritative value. A matching booking ID with a different amount is a correctness conflict, not a harmless replication delay. For old clients, collect representative DNS/cache/connection behavior, exact request and response histories, counts by client group and a bounded transition plan. Do not label the loopback interval an AWS RTO, the journal comparison a live RPO, or a green route as business recovery.

**Assessment standard.** A learner distinguishes first failure, health, reconciliation, switch and first correct customer observation; explains why the held run has no recovery endpoint; identifies the stale old-path population; and states the fixture's single-host and cooperative-control limits. A correct written answer is not an independently observed learner result.
