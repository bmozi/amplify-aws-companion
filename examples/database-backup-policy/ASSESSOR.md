# Assessor notes — database backup and retention policy

Reward answers that begin with failure modes and owner-approved objectives, not a generic daily schedule. The learner should distinguish RPO from retention, RTO from backup completion, operational recovery from long-term records retention, and a restore test from an integrity check. A policy must account for how long corruption may go undetected and identify independent write/reconciliation evidence when restoration would lose valid work.

Case 1: The 5-minute loss and 45-minute recovery promises need a mechanism and measured restore process capable of meeting them. The notice time is 15 minutes after deletion, so restoring the latest valid point requires finding the actual deletion time and preserving valid writes after it. A service feature's advertised point granularity is not a measured RTO.

The exercise starts its recovery clock at discovery: 12:20 plus 45 minutes gives a **13:05** service-restoration deadline. If the clock instead started at the 12:05 deletion, the deadline would be **12:50**, leaving only 30 minutes after discovery. A restore operation finishing by the deadline is insufficient if validation and redirecting customers to the recovered service happen later. As an illustrative plan, a decision at 12:25, restore completion at 12:45, validation through 12:55 and customer cutover at 13:00 meets the discovery-based clock, but misses the deletion-based clock. These are invented times, not observed recovery results. The five-minute data-loss target still needs a separately demonstrated recoverable point and reconciliation of valid changes; the elapsed recovery timeline alone cannot establish it.

Case 2: A 35-day continuous recovery window does not reach 42 days. Look for older independent recovery points, detection evidence, transaction records for reconciliation and explicit treatment of valid activity since corruption. Do not claim a backup within the window can restore before an older defect.

Case 3: Keep the operational recovery window and the seven-year approved record policy separate. Long-term copies may have different retrieval speed, cost and legal controls. A seven-year archive does not by itself meet the operational RPO/RTO. Do not offer legal conclusions; request counsel/owner requirements.

Case 4: Identify the compromised administration boundary. An extra backup in the same account with the same delete authority may not satisfy the stated failure assumption. Evaluate a separately controlled account/Region/copy path, access restrictions and tested recovery credentials. A copy is not shown independent merely by its location label.

RDS and DynamoDB mechanisms have different retention and restore semantics. Verify current limits for the exact resource and Region. AWS Backup support is resource-specific. All answers must include restore behavior, application-level acceptance, recurring and restore cost, key/access dependencies and cleanup. Never imply that backup policy alone guarantees immutable copies, security, regulatory compliance or a particular recovery time.

This is an authored paper assessment. No AWS account, backup configuration, price, legal requirement, restore or independent learner response was observed.
