# Select the migration mechanism, then test the business switch

This is a fictional, cloud-free assessment. Read the [mechanism lesson](../../reader/BOOK-LOCATORS.md#book-efc16ad43148d6e0), run `python3 examples/migration-mechanisms/lab.py` from the repository root, record your choices, and only then read the [assessor notes](ASSESSOR.md). The Python drill calculates an **ideal transfer lower bound**, not an AWS service benchmark. The earlier [portfolio packet](../migration-portfolio/README.md) decides which workloads deserve a wave; this packet tests how their parts could move.

## The proposed five-day cutover

Maya's repair company has approved a possible AWS target Region but has not approved a target design, cost or cutover date. Its current application includes a Linux booking VM, a PostgreSQL database still accepting appointments, an 8 TiB NFS drawing archive, nightly SFTP files from a supplier, a staff Active Directory, and an on-site payment webhook. The booking VM authenticates staff against the existing directory. The archive's approved inventory and final-change method have not been signed off. The office can spare at most 80 Mbit/s for migration traffic, measured only as a contractual limit, not a sustained throughput test. Management asks for the whole move in five days with at most five minutes of interrupted bookings.

An architect proposes one DataSync task for the archive and database, S3 Transfer Acceleration to meet the five-day deadline, AWS Transform MGN for the VM, a new IAM Identity Center source on cutover morning, and a Control Tower landing zone in a single-account Free-plan learning sandbox. The proposal says “rollback by switching DNS back.” No current prices or production credentials are provided.

## Your first decision

1. Draw six lanes: bulk archive, continuing SFTP exchange, VM, database, hybrid network/DNS, and staff identity. For each, choose a candidate mechanism or **hold for evidence**. Name the source/target support, owner, current service eligibility and acceptance check. A candidate is not approval to provision it.
2. Run the local arithmetic drill. Show why 8 TiB over 80 Mbit/s cannot meet five days even under ideal conditions. State the minimum ideal Mbit/s and the extra work that makes a real deadline longer. Explain why an S3 edge feature cannot increase the office's outbound link capacity.
3. Decide whether MGN rehosting and DMS database migration solve the same job. Compare a same-engine native backup/restore with full load plus CDC if the chosen path supports it. State when schema conversion is needed, which data and business semantics still need validation, and what target-only bookings mean for rollback.
4. Draw the old and new request and return paths while the database and directory stay on site. Compare internet VPN with a private Direct Connect option at the level of transport, encryption, lead time, failure, capacity and recurring cost. Explain how DNS and identity assignments affect the cutover separately.
5. Replace the proposed Control Tower action with a governance model that fits the **single-account learning sandbox**. Then describe the multi-account option for a fictional enterprise as design-only. Make a security/cost register covering migration agents, roles, secret and key access, transfer endpoints, logs, replication/staging, old/new overlap, validation and cleanup.

The [AWS SAP-C02 task 4.2 guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02-domain4.html#solutions-architect-professional-02-domain4-task2) names older and current service examples. Verify live availability before using an example in a real account. In particular, [Application Discovery Service](https://docs.aws.amazon.com/application-discovery/latest/userguide/application-discovery-service-availability-change.html) and [Snow Family device ordering](https://docs.aws.amazon.com/snowball/latest/developer-guide/snowball-edge-availability-change.html) differ for new and existing customers.

## Change cards

Apply one card at a time and explain which original choice or deadline changes.

- **More bandwidth, more time:** A tested, dedicated 1 Gbit/s path becomes available for 20 days, but the archive still changes daily. Does passing the mathematical bound establish a safe archive cutover?
- **No source agent:** Policy forbids installing an agent on the booking VM. Can the proposed server rehost proceed as written? What alternative or exception evidence would you ask for?
- **Different database engine:** A team now wants MySQL for the target. Which schema, code and application comparisons appear in addition to row movement?
- **Identity cutover failure:** A test identity-source switch removes assignments needed for operator access. What must be repaired before the booking switch, and who can still recover access?
- **A real enterprise estate:** A separately funded organization has migration, security, logging and production accounts. Which organization/landing-zone questions become relevant, and what costs and control boundaries need owners? Do not apply this design to the single-account learning sandbox.

Ask Codex: “For each lane, name what the candidate service moves, what it does not move, what could keep accepting new business during cutover, and the observation that would prove or disprove my choice. Flag current-service availability and unpriced resources.” Compare its answer with official AWS documentation and the assessor. AI can challenge omissions; it cannot supply an observed throughput, owner approval or actual bill.
