# Choose a managed service by the job it does

Use this worksheet with [Unit 02](../../reader/BOOK-LOCATORS.md#book-43b448edc6798adc). The examples are fictional. No transfer endpoint, queue, secret or credential is created.

For each case, identify the business operation, service responsibility, data/permission boundary, failure behavior and complete cost inputs. Compare the managed candidate with one credible alternative. A managed service takes on specified infrastructure work; it does not automatically make the application correct or secure.

1. **Partner file exchange:** A supplier needs to upload price files through SFTP. The company wants files in S3 and per-partner access. Compare AWS Transfer Family with a self-managed SFTP server. Include identity, protocol, file validation, malware/publication stages, endpoint/networking and retained-file costs.
2. **Background work:** An API should accept a photo quickly and let a worker process it later. Compare SQS with putting a custom queue table or a server process between the API and worker. Include duplicates, retry, visibility timeout, poison work, status and the capacity of storage/processing dependencies.
3. **Database credential:** A worker needs a database password that operators can rotate without baking it into an image. Compare Secrets Manager with a static image/environment value. Include runtime access, secret rotation compatibility, logs, permissions and service charges.
4. **A familiar product name:** A developer proposes Transfer Family for background compute because both involve “transferring” work. Explain which business operation the service is designed to provide and choose the actual queue or compute mechanism.

Record unknowns as unknown. Ask Codex to find a responsibility the managed service does not take over. Verify the exact service mode, permissions, Region and cost before any real design. This exercise is not a recommendation for an account or production workload.

## Photo P-42: choose the whole waiting line

Maya's shop accepts a photo request and promises to show its status within one minute. The supplier may take twenty minutes to process it. During busy periods, forty requests arrive per minute for ten minutes; the supplier can process ten per minute. These numbers are fictional. The API and worker already use one relational database. The team proposes three paths: **A**: SQS Standard plus an acceptance outbox and workers; **B**: a database queue table with polling workers; **C**: a broker the team operates. Choose a starting path and write the customer promise before reading the [assessor](ASSESSOR.md).

1. Calculate the ten-minute backlog if the supplier starts with an empty queue and no extra capacity. Which part of the path limits completion? What status can the API truthfully show at minute one?
2. Draw the first durable fact after customer acceptance. For A, B and C, name who owns message durability, retry leases, worker duplicate safety, poison-work review, backup/recovery, permissions and maintenance. Identify an observation that would disprove your preferred path's fitness.
3. The database accepted **P-42**, but the dispatcher's SQS send response was lost. It cannot tell whether SQS got the message. What must it do, and what ID must survive? Now suppose a worker called the supplier and lost the supplier's reply. What may the worker truthfully claim? What evidence would resolve the ambiguity before another external effect?
4. Change one fact at a time: **(a)** the supplier requires an existing broker protocol that SQS cannot provide; **(b)** finance reports that queue traffic is slowing booking writes; **(c)** the product now requires replaying the last month of ordered events for several independent consumers. Revisit the choice each time. Do not claim that switching a queue mode alone supplies arbitrary replay or exactly-once supplier effects.
5. List the cost meters and an upper-bound load for the selected path. Include idle and peak worker cost, queue/API or database/broker use, retention, encryption, monitoring and operator work. State what must be measured before production approval. Include a criterion for switching away.

For a runnable, cloud-free check of the duplicate-effect boundary, do the [queue-recovery lab](../queue-recovery/README.md). Record the unsafe and safe traces and explain which parts of this packet the lab cannot prove. Then read the [assessor](ASSESSOR.md). Codex may challenge your arithmetic and decision, but save your original answer first so its explanation does not substitute for your own reasoning.
