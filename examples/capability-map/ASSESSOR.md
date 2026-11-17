# E30 assessor notes: carry the map to a different business

Use these notes after making your own design. The packet tests reasoning and transfer; it is not a deployed architecture, compliance assessment or calibrated certification question.

A strong promise says what clinic staff can submit, what a **server acceptance receipt** means and who must escalate a safety-critical received request within 30 minutes. A local offline draft has not crossed that server boundary. It may still deserve a visible local status and a manual emergency route. Assignment and completed repair are later outcomes. The learner should state how a clinic learns whether synchronization succeeded after an uncertain reply; generating a new request ID for each retry can create duplicates.

| Question | What a defensible answer should expose |
| --- | --- |
| Who can act? | Clinic-scoped staff, assigned technician and deployment identity have different authority; test another clinic's denied read. |
| Where does traffic go? | Identify online entry, offline boundary and reconnection path; a reachable endpoint does not establish authorization. |
| What runs the work? | Validate submissions, durably accept the request and schedule escalation; bound retry and duplicate handling. |
| Where does data live? | Protect photos and records, define retention and restore evidence; an offline copy is another data location. |
| How do changes ship? | Identify version compatibility for offline clients and a rollback path that can read newer data. |
| Detect and recover? | Measure receipt-to-escalation time and missing synchronization; test notification delivery and a human fallback. |
| What does it cost? | Estimate storage, requests, transfer, notifications, logging, idle capacity and recovery; state uncertainty and a stop condition. |

The two interruption options trade complexity and availability differently. An offline queue can preserve drafts through local disconnection but introduces device security, conflict, duplicate and synchronization work. A connected workflow with manual fallback reduces offline software but relies on a staffed process during outages. Neither option guarantees that the 30-minute escalation clock begins during a clinic's disconnection. The business owner must define the clock and emergency process, then measure them.

The [offline clinic fixture](../clinic-offline-intake/README.md) makes one possible local-intake contract observable. Its local SQLite receipt at minute zero is separate from its server receipt at minute 120; a minute-20 log is not a verified human call. The unlogged critical request misses the fixture's local deadline. A learner may instead choose a server-receipt clock, but must then give offline staff honest status and a credible urgent manual route. Reopening the same file does not test a lost device, and the static clinic mapping is not real authentication.

The 24-hour clinic should change scheduling, on-call coverage, signal and cost assumptions. Shared identity rules, request contract and core data model may remain, provided the test shows the clinic-specific rule cannot leak across tenants. Separate AWS accounts can be a later isolation decision; the new hours alone do not prove they are required.

Ask for a bounded trial plan with current AWS eligibility/pricing, a scoped identity, a complete estimated run within the reader's chosen limit, a reader-chosen credit reserve, named cleanup and actual verification of resource removal. State the account, date, selected meters and why those limits fit the available credits and the owner's willingness to spend. A worksheet is not evidence that an account meets its limits now. Credit and budget alarms do not guarantee a hard stop. Treat any proposed AWS service or compliance claim as unverified until its current documentation and the relevant live boundary are checked.
