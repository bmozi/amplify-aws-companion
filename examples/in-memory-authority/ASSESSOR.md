# Assessor reasoning for the acknowledgment exercise

The local record-before-ack path preserves R17 across the modeled worker replacement because the new worker reloads the committed journal. The old R16-only snapshot cannot recover that newer confirmation by itself. The deliberately unsafe ack-before-record path returns a receipt before the journal contains R17; after volatile memory is discarded, the replacement sees no R17. This is the lost-promise counterexample, not a prediction of how an AWS service is configured.

The stable operation ID matters after a lost reply. A retry with the same intent returns the same logical R17 and the SQLite journal contains one row. A retry with changed intent is a conflict rather than a new appointment silently hidden under the old receipt. A real system must also scope the key to an authenticated caller, define retention, enforce capacity at the authoritative write, and reconcile any external side effect. Those controls are not implemented here.

Give credit for naming the exact authority, ack point, recovery source, customer readback and limits. A statement such as “Redis is fast,” “we have a backup,” or “the process restarted” does not establish any of those. The local result cannot prove AWS service durability, cost, latency, Region behavior, customer authorization or independent learner mastery.
