# SAA-C03 delayed transfer cases

Attempt these original fictional cases after studying the relevant task and allowing time away from its worked answer. Preserve the first answer before reading the separate assessor. They are open-response learning assessments, not official questions or a pass prediction. For each case give a choice, the controlling requirement, a mechanism, one rejected alternative and the effect of the changed fact. Cite sources only in a later open-book revision.

## SAA-T01 — task 1.1

A supplier needs read-only access to one export prefix in your account. Your employees already use workforce federation. Compare supplier role assumption with copying an employee key. Specify who may assume the role, what the resulting session may read, and which denial you would test. Now the supplier serves several customers and uses the same integration software: what additional trust-boundary question must you resolve?

## SAA-T02 — task 1.2

A private API can be reached only through an approved network path. Two signed-in tenants nevertheless see each other’s records when they change an identifier. Explain the defect and the first correction to the design. Now an approved user sends malicious HTTP input: which additional control might reduce that attack class, and what must remain in application code?

## SAA-T03 — task 1.3

An encrypted backup is retained for 30 days. The only permitted restoration role is deleted, and the key is scheduled for deletion before retention expires. Explain why the retention label is insufficient and give an acceptance test for the recovery design. Now retention is required for seven years: which assumptions must be revisited beyond multiplying the storage estimate?

## SAA-T04 — task 2.1

A worker commits a payment record, crashes before acknowledging its message, and receives the message again. The queue is healthy. Explain why changing only the visibility timeout does not prove safety. Now the external provider accepts an idempotency key: describe the durable identity and reconciliation information you would keep.

## SAA-T05 — task 2.2

A standby application has replicated data but no approved KMS decrypt path and insufficient regional quota for peak capacity. Its DNS failover is configured. Can a ten-minute RTO be accepted? Name the missing observations. Now a rehearsal succeeds for ten requests but production peaks at ten thousand: explain what that result does and does not establish.

## SAA-T06 — task 3.1

A Windows application requires SMB and existing directory integration; another process only writes immutable photo objects. Compare the storage choices without assuming both need one filesystem. Now the application requires a particular filesystem feature or throughput: how do you turn a service-name choice into an acceptance decision?

## SAA-T07 — task 3.2

A queue grows although worker CPU is low. Traces show most time waiting for a throttled downstream API. The team wants to double workers. Explain the likely effect and choose useful measurements. Now the downstream limit is raised and profiling shows CPU-bound work: how might the scaling decision change?

## SAA-T08 — task 3.3

A report reads a replica and can tolerate two minutes of lag. An order-confirmation screen reuses that report query and sometimes says a committed order does not exist. Explain the mismatch and a possible read-path repair. Now a large reporting query overloads the writer after failover: what capacity and fallback issue appears?

## SAA-T09 — task 3.4

A global application has non-cacheable TCP traffic and needs a stable entry address with endpoint health-based routing. A second application serves cacheable HTTP images. Compare Global Accelerator and CloudFront for these different needs. Now a policy requires encrypted hybrid traffic: why is the name Direct Connect not sufficient evidence?

## SAA-T10 — task 3.5

A marketing team needs daily supported SaaS exports, a Kafka application requires replayable topics, and a dashboard queries curated S3 tables. Assign acquisition, stream, transformation/catalog, query and presentation responsibilities. Now a record arrives late and a schema changes: what correctness checks must precede refreshing the dashboard?

## SAA-T11 — task 4.1

Two eligible object classes meet durability needs. In this fictional estimate A costs 120 units for storage plus 5 for reads. B costs 65 for storage plus 80 for retrieval and 10 for transitions. Both meet the stated retrieval deadline. Choose on these supplied costs, then change B retrieval to 10. What other terms must be checked before using this arithmetic for AWS?

## SAA-T12 — task 4.2

An eligible baseline would cost 100 fictional units per month on demand. A commitment costs 70 per month even when unused. Expected use is ten months of the twelve-month term. Compare these simplified annual totals. Now use falls to six months. Explain what changed and what the model omits.

## SAA-T13 — task 4.3

A new database design is cheaper at the assumed average rate but needs an index for each important query, a replica for reporting and a migration rewrite. Explain how you would compare it with the existing database. Now queries become ad hoc and relational joins matter: what earlier assumption has changed?

## SAA-T14 — task 4.4

A service pays for S3 traffic through a zonal NAT gateway and for unrelated external API traffic. An engineer proposes an S3 gateway endpoint and deleting all NAT capacity. Explain which traffic changes and which does not. Now one AZ fails: what must the remaining outbound topology demonstrate?
