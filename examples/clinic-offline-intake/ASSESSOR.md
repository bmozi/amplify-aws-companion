# Assessor notes for the clinic outage

Read after the unaided attempt. The fixture tests a precise local contract, not a real clinic, human escalation, compliance claim or AWS architecture.

The first question is **who receives the request at minute 0**. Under the lab's chosen contract, the clinic device accepts it locally. The central service does not receive it until minute 120. A screen that calls the first event a server acceptance lies. If the business instead starts its 30-minute clock only at server receipt, it must tell staff what urgent offline work to do and must not imply a central escalation during the outage. A safety-critical machine may require a separate staffed local route even when the server clock has not started.

The restart proves three rows survived reopening the **same device file**. It cannot prove survival after loss, corruption, battery failure or theft. The server's same-ID replay proves a narrow SQLite idempotency rule for unchanged fixture content. A photo token or critical-status change under that ID is a conflict; it cannot be silently substituted. An external dispatcher would need its own stable operation ID, receipt lookup and unknown-outcome reconciliation after a lost reply.

The minute-20 log is only a stored assertion. There is no trusted clock, staff identity, phone route, delivery receipt or human acknowledgement. The missing log at minute 120 exposes a breach of the fixture's *local* 30-minute rule; late synchronization cannot repair it. The actual business must define who monitors missing logs during the outage and how an operator follows up.

The static mapping is a teaching boundary: `device-a` belongs to clinic A and `device-b` to clinic B. It denies the tested cross-clinic sync/read. A real service needs authenticated device/staff identity, current clinic membership, revocation, per-request authorization and protected transport. The invented photo token is not a file, image scan, encryption, retention or deletion test.

A defensible architecture comparison keeps both candidates alive until the business specifies the receipt and outage promise. Offline queue plus local escalation adds device protection, sync/replay handling, staffed coverage and evidence. Connected intake plus manual fallback avoids that queue but needs a reliable manual route and honest UI status. For either, include photos, requests, transfer, notifications, device support, logs, backups, cleanup and recovery in a selected whole-run estimate. No price or account state was observed here.

The 24-hour clinic changes coverage and alert routing for that clinic. It need not force all three clinics into separate accounts or identical schedules. Ask for a forbidden-neighbor read and a missed-escalation test after the change. Treat the local tests as code-path evidence only; independent learner and live integration results remain open.
