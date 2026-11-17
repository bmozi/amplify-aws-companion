# Assessor notes: a stopped fault is not a recovered service

Use after the learner records decisions. These are provisional assessment criteria for fictional packets, not results from assessed learners.

## Packet 1

Do not begin. Both target isolation and observation freshness fail: two targets include a shared worker, and 35 seconds exceeds the 20-second freshness bound. Require a reviewed resolved single target and fresh baseline evidence, as well as the other stated preconditions. Merely narrowing the selector text or waiting for the old dashboard to appear green is insufficient. Accept an alternative target mechanism if it supplies equivalent scope evidence.

## Packet 2

At second 20 the duplicate confirmation requires immediate stop. At 25 only the fault-controller stop has been observed. At 40 availability has improved but the business defect persists. At 60 repaired records and capacity are supplied, but the two recovery windows are not complete. Acceptance first occurs at 100 under this exercise's stated rules.

- Detection: 20 − 10 = 10 seconds from first observed customer failure.
- Stop completion: 25 − 20 = 5 seconds after the stop request.
- Accepted recovery: 100 − 10 = 90 seconds after first observed failure; 100 seconds after fault start.

The 120-second recovery target is met by the fictional evidence. The single-booking portion of the hypothesis fails because duplicate confirmations occurred. Repair does not erase that failure. Do not label the whole experiment a reliability success or report five seconds as the service's recovery time. Learners should distinguish the tool doing its intended disruptive work from the system satisfying its business requirement.

The observation windows and ledger reconciliation are supplied facts. There is no raw telemetry, independent trusted ledger implementation or real timing measurement to validate here. A learner who identifies these limits is reasoning correctly.

## Packet 3

At second 35 the last sample is 25 seconds old, beyond the stated 20-second bound. Request stop through the available checked path; investigate the lost observer and verify stop completion. A stale green display is not a current healthy result. HTTP 200 alone cannot satisfy the reconciliation requirement. Keep recovery acceptance pending until authoritative business evidence is available.

Read-only operation is a separate business decision. Ask whether its source is current and trustworthy, whether reads leak private information, and whether users could mistake stale availability for a confirmed booking. The packet does not establish permission or safety for reopening; a conditional proposal with named missing evidence is stronger than inventing those facts.

## Transfer

Sending a confirmation is an external side effect. A redelivered message can repeat it even if the worker restarts correctly. Seek a stable business identity, an explicit duplicate-handling design at the relevant boundary, and reconciliation of delivered confirmations against accepted bookings. A database transaction alone cannot retract an already delivered message. Do not require one particular AWS product as the answer.

## Review criteria

Assess four dimensions as adequate, incomplete or unsupported: target and access boundaries; observation and stop decisions; timing and business reconciliation; transfer to a new side-effect boundary. An adequate response names the supporting packet evidence and its limits in each dimension. Unsafe start despite failed preconditions, treating stale telemetry as healthy, or equating controller stop with business recovery needs correction before a future live exercise.

This rubric is not a certification scoring model or an independently calibrated learning assessment.
