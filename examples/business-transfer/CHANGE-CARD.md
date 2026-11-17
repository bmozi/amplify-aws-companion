# Change card: the machine moves, but its promises remain

Read this after saving your first submission. Preserve that version so a reviewer can see what the new facts changed.

The business now allows a cleaner to return to the other branch. Transport between branches takes 90 minutes after inspection. The receiving branch must acknowledge physical receipt before handover. A transport departure event alone does not prove arrival. Customers can still have existing future reservations specifying the original pickup branch.

Staff sometimes work offline for 30 minutes. A device can submit duplicate or delayed return/inspection records after reconnecting. The business has not authorized offline confirmation of new reservations or offline handover. A cleaner may also be recalled for inspection while in transit.

Revise the design to answer these questions:

- Which earlier assumptions are invalid, and which foundations remain useful?
- Who may record return, inspection, transport departure, receipt and recall? How does authority follow the asset without granting every branch access to every customer?
- How will you distinguish event identity from business order? Explain why accepting a delayed old “inspection passed” event must not automatically clear a newer recall.
- What does the system do with an already-confirmed pickup at branch A when the asset is returned to branch B? Compare reassignment, transport and an explicit customer exception without assuming any can always meet the deadline.
- What gets reconciled after an outage or restore: database state, device events, physical custody and existing customer promises?
- What additional tests, cost drivers and operator procedures are needed? What must remain unavailable while the facts are uncertain?

Draw the changed flow and write a short decision amendment. Identify one rejected alternative and the condition under which it could become appropriate. Do not solve the change by merely increasing the 60-minute turnaround setting: transport and acknowledged custody introduce new states and authority rules.

This remains a design exercise. There are no real devices, transportation events or measured recovery results in the repository.
