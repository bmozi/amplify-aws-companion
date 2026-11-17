# Movement-service assessor notes

Use after the first answer and changed-constraint revision. These are internal reasoning criteria, not cloud or learner evidence.

| Workstream | Starting hypothesis | Evidence that could change it |
| --- | --- | --- |
| One-time NAS move and retirement | DataSync, if the source/target pair and change/cutover plan are supported | Dataset size/count, metadata and permissions, source writes during copy, available bandwidth, supported mode, integrity/manifest scope, errors and final reconciliation |
| Recurring supplier SFTP delivery | Transfer Family endpoint backed by S3 or EFS, if identity, protocol and partner controls fit | Whether supplier can change protocol, identity-provider design, network exposure, per-user path isolation, upload completion, malware/validation workflow, endpoint and data-volume cost |
| Ongoing SMB application access to S3-held files | S3 File Gateway, if application file operations and cache/outage behavior fit | SMB semantics, authoritative writer, cache and bandwidth, upload backlog, uncached reads, identity/permissions, multiple-writer risk and ongoing host/service cost |

## Assessment criteria

- DataSync is a transfer task over supported source and destination locations; confirm the exact pair, whether an agent is needed and the task configuration. It can move files/objects and support repeat runs, but a task alone does not establish a sound business inventory, transactional database migration or final cutover.
- Transfer Family is a managed protocol endpoint for exchanging files with people or partner systems. It is not simply a bulk inventory-and-copy engine for the NAS, and it does not provide an SMB mount for the lab application. Design the identity, user isolation, protocol, workflow, destination and endpoint lifecycle.
- File Gateway preserves a compatible NFS/SMB access path into S3 with transparent local caching; it is not just a one-time transfer job. Treat cache capacity, WAN loss, writes not yet uploaded, uncached reads, metadata refresh and shared-writer behavior as operational design questions.
- A portfolio can combine services because its workstreams have different needs. A single named migration service need not cover every row.
- Compare all relevant costs: service/task or endpoint usage, underlying S3/EFS requests and storage, file counts, network, gateway hosting and cache, operations, verification, retries, overlap, security and cleanup. Do not choose a low-cost option that fails a protocol or cutover requirement. No current price, regional eligibility or configuration is supplied.
- Before retiring the NAS, compare an independently approved source inventory with included, skipped and failed items; rehearse final change capture; read representative files through the target identity and application; reconcile business records; and preserve rollback evidence until the owner accepts cutover.

