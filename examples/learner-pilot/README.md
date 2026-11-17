# Try one lesson and explain a changed case

This packet prepares a small reader trial of AMPLIFY AWS. It is not a record that anyone has completed the trial. It requires no AWS account, cloud spending or customer information. Use a participant pseudonym and obtain agreement before retaining notes; screen/audio recording is unnecessary for these tasks.

The facilitator gives each participant only their task below and the linked teaching source. Keep [assessor notes](ASSESSOR.md) out of the independent attempt. Save answers privately outside tracked source. Record the exact Git revision or archive hash before beginning, and retain that same packet for the trial. Do not silently replace the lesson halfway through an attempt.

A facilitator can prepare separate assessor-free reading packets from the private book source. This lab packet contains the tasks and book locators, but not the chapter text or the packaging tool needed to freeze those readings. Keep assessor notes out of each independent attempt, record the exact packet hash, and inspect each packet before delivery. Optional execution needs a separately checked source archive. Package construction is not a learner result.

## Beginner task: what is actually in the release

Read “Build the parcel from the intended contents” and the **first paragraph only** under “Keep the tested package attached to its evidence” in [the delivery lesson](../../reader/BOOK-LOCATORS.md#book-e638a42a6a7bf5d6). That next paragraph defines an artifact digest, the kind of byte fingerprint this task calls a checksum. Stop before the subsection's diagram and further instructions. Explain any unfamiliar word in your own words or mark it unclear. You do not need to install tools to answer this task.

A team has these observations:

- Current source contains `index.html` and `hours.txt`.
- The released ZIP contains those two files and `old-discount.html`.
- The homepage displays the current title.
- The team recorded the ZIP's checksum and calls it ready.

Write a decision on whether that evidence is enough for release. Name the additional check you would request and explain what the checksum does establish. Describe one way the extra file could have entered the package without claiming that your explanation has been proved.

Now change the case. The team uses a fresh output directory. The ZIP contains exactly `index.html` and `hours.txt`, and its checksum matches the recorded value. The owner approved Saturday opening hours of 9 a.m. to 1 p.m., but `hours.txt` says “Closed Saturday.” Explain whether the filename and checksum checks justify release. Write a positive check for the requirement that is still unmet, and explain which earlier checks could remain true.

Finally, change one more fact: the new ZIP contains exactly the intended files, but an old public URL still serves the discount page. State what this evidence can and cannot tell you about the new build. Name the next serving location or stored copy you would investigate. You do not need to select an AWS product.

## Experienced task: an uncertain supplier outcome

Read the A21 extension in [network selection](../network-selection/README.md#a21-extension-the-guide-loads-but-the-booking-is-uncertain), stopping before its executable walkthrough. Do not read the assessor yet.

A reservation service sends request `r-17` to a supplier. The supplier's durable log records acceptance, but the service receives no reply. A replacement worker sees the local queue item and proposes retrying with a new ID. Its own database does not contain a supplier receipt. The customer-facing page currently says “failed.”

Write the next operating decision, the evidence supporting it, the unresolved facts and the customer-facing wording you would use. Identify which authority can establish the supplier outcome and what must persist across worker replacement. Explain why a locally absent receipt differs from a supplier rejection.

Change the case: the supplier exposes a result lookup, but the replacement worker has no verified permission to use it and the lookup's consistency behavior is undocumented. State what evidence is needed before trusting “not found,” and how your plan handles unresolved work without indefinite retries. Do not invent successful authorization or a business deadline.

## Architecture-transfer task: a food-bank pickup promise

Read [the architecture-decision lesson](../../reader/BOOK-LOCATORS.md#book-549c004b6b1d082d) from “Begin with promises” through “Reuse the questions,” including its three-context diagram, before answering. The frozen packet calls this excerpt `READING.md`. Do not open the assessor notes. This is a written design exercise with fictional facts; no AWS account or code is needed.

A food bank has eight depots. Partner organizations submit a pickup request for a food box. A submitted request must receive a durable receipt, but it must **not** claim a box is reserved until the depot confirms inventory. Repeating the same partner's request after a lost reply must not reserve a second box. A partner may see its own requests; another partner may not see those requests through an ID guess, file link or status cache. A confirmed pickup must be ready within 90 minutes. The busiest 15-minute arrival count, inventory-update delay, retained data volume and acceptable recovery time are unknown. No prices have been supplied.

Write the common path from actor to observed customer result. Then name the **business fact** that makes this different from the repair-shop receipt in the reading. Compare two bounded designs: (A) try to reserve inventory synchronously before returning any receipt, and (B) durably accept a private request, return a pending receipt and let a separate allocator confirm or refuse a box. Choose provisionally under the stated facts. For each design, give one advantage, one failure or recovery risk, and an observation that could reject it. State what the 90-minute promise measures and what missing peak and cost facts you would need before deploying either design. Do not invent an AWS result or price.

Change the case after preserving your first answer: one partner now operates two depots and should see requests for both, but no other partner's requests. A depot loses today's request records and asks to restore yesterday's shared database backup. Explain the authorization rule and a forbidden-neighbor test. State what that restore could damage for other depots, which record/file/workflow facts must be reconciled, and what result would make you reconsider your first design. Keep an unresolved fact unresolved when the packet supplies no evidence.

Draw one small diagram showing the partner boundary, receipt, inventory decision and customer-visible status. Label each arrow with the fact it carries. Your diagram is a proposal, not proof of implementation. Record your own answer before asking Codex for critique; in a separate assisted phase, ask it for one missing assumption and check its claim against the packet. Do not use the assistant's answer as the independent result.

## Amplify-privacy task: the empty first page

Read [the two-user notebook lesson](../../reader/BOOK-LOCATORS.md#book-7ca24cf76a59aaa1) and its diagram. Use only the fictional observations below. No AWS account, test users, installation or spending is needed.

A school club gives each member a private progress note and one small attachment. Ana can sign in, save her note and file, sign out, sign back in and read both. Ben signs in with a separate club account. Ben's direct read of Ana's note ID fails, his update fails, and his file download fails. A list request returns an empty first page **with a next-page token**. Ben's file overwrite request reports success. Ana later downloads her file and sees Ben's replacement bytes. The test operator has not yet checked another list page or removed the test note and file.

Write a short evidence table with the actor, operation, observed result and claim it does or does not support. Decide whether the club may tell members their notes and files are private. Name the next list check, the most serious observed failure, and the cleanup evidence still needed. Distinguish a failed read from a failed write, and a working sign-in from ownership enforcement. Do not propose changing all notes to public access to make the check pass.

Preserve your first answer. Now change the facts: Ben's overwrite is denied; every returned list page has been checked and omits Ana's note; Ben cannot list, download or delete her file. The operator's cleanup attempt removes the note but fails to remove Ana's temporary file. State what the tested authorization paths support, what remains unverified, and how to handle the leftover file without inventing a successful deletion. Explain why a local fake-service test would still be weaker than the same requests observed against a deployed backend.

Only after saving your independent answer, ask Codex to challenge one unsupported claim in it. Save its prompt and response and your revised answer separately. The assistant's critique is help, not proof that the first answer was correct.

## Operations task: which customer is still waiting?

Read “Name the observation precisely” through “Give asynchronous work time to finish” in [the customer-outcome lesson](../../reader/BOOK-LOCATORS.md#book-5bad0b580d7f13fa). The frozen packet calls this `READING.md`. Then use only the new fictional [case](operations-case.json), called `CASE.json` in the packet. Do not open Unit 33's worked incident, the checker, or any assessor material before saving your first answer. No AWS account, code execution or customer data is needed.

The service promises to finish an assignment within 50 seconds after accepting a job. A snapshot at second *t* includes every completion stamped *t* or earlier; if a job is still unfinished after that snapshot and its deadline is *t*, it has missed the promise. At second 100 a customer says their request disappeared. The homepage returns 200, a frontend button-label release occurred, two worker attempts and a separate supplier probe returned 503, and someone proposes increasing worker concurrency tenfold. Use the six accepted jobs and timestamps in `CASE.json`.

Write the **exact job IDs**, not only totals, for work still unfinished at second 100 and for jobs whose 50-second promise has already been missed. Give the mature cohort and on-time fraction. Explain why the two lists can have the same length but different members. Name one fact supporting a supplier-path investigation and one observation that would still be needed before blaming that supplier as the root cause. Decide whether the homepage probe establishes that assignments work. Propose one bounded next action with an owner, stop condition and customer-facing sentence; do not invent an executed recovery or a numeric worker limit.

Preserve that answer before reading these changed facts. For the changed case, p3 completes at second 103; p4 and p5 are still unfinished through the snapshot at second 110. At second 105, list unfinished and missed-promise IDs again. At second 110, decide whether p5 has reached its deadline. A later completion can clear unfinished work; state whether it can repair an earlier missed promise. Record which follow-up facts were unavailable to the operator at second 100. Do not silently use future timestamps in the first answer.

In a separate assisted phase, ask Codex to find one unsupported causal or recovery claim in your saved answer. Keep its prompt and response, your revision and your own explanation of the change separate from the first attempt. The facilitator's criteria remain separate from the participant packet.

## Certification-to-application task: recover a real booking

Read the opening and “Extract the contract before comparing the options” in [the scenario-reasoning lesson](../../reader/BOOK-LOCATORS.md#book-526d1ca77264f256). Stop before its worked example. The frozen packet calls this excerpt `READING.md`. This original exercise practices part of [SAA-C03 Task 2.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task2), including choosing a recovery approach from business requirements. It is neither an official question nor a prediction of exam performance. No AWS account, code or spending is needed.

At 09:02 a repair shop loses its primary Region. Booking **b241** was confirmed at 08:59 with a customer attachment. The stated promise is to restore the *whole* booking path within **20 minutes of the outage** without losing any confirmed booking or its attachment. Only the booking's owner may read either one. The business asks for the lowest recurring cost among candidates that meet those limits. A rehearsal has these **stipulated** results:

| Candidate | Rehearsal observation | Recurring cost |
| --- | --- | --- |
| A | Homepage responds at 09:10. Its restored records stop at 08:55; b241 and its attachment are absent. | Lowest |
| B | At 09:19, an authorized customer can read b241 and its attachment and create a new booking. Reconciliation includes every confirmed booking and its attachment through the outage. A different customer is denied both b241 and its attachment. | Higher, within budget |
| C | API responds at 09:14 and b241 is present. The authorized customer cannot open its attachment. | Between A and B |

**First attempt, without an answer key:** choose the supported candidate. Write the requested decision, hard constraints, elapsed time, and one precise reason for rejecting each alternative. Mark any fact you used that the case did not supply. State what this paper decision can establish and what it cannot prove about a future outage.

**Application plan:** before proposing a real recovery test, name the records and timestamps you would capture, the owner and forbidden-neighbor reads of both booking and attachment, the new-booking check, and the exact start and stop events for the 20-minute clock. Name one permission or key prerequisite, one cost category beyond the running standby, an off switch and the cleanup receipt. You may leave actual prices, permissions and behavior unknown. Explain what a local selective-restore exercise could check and which AWS/customer claims it could not establish.

Save that answer. **Changed case:** a second, independent rehearsal now confirms A has every booking and attachment through 09:02, an authorized owner read and forbidden-neighbor denial for both b241 and its attachment, and a new booking at 09:18. Its 09:10 homepage result is unchanged. All three candidates retain their stated recurring cost order and the same 20-minute limit. Choose again and explain whether your first answer was an error or a response to different evidence. State the clock time you use for A, not merely when its homepage loaded. Do not pretend this second rehearsal retroactively repaired the first one.

Only after retaining both answers, ask Codex to identify one unsupported claim in your application plan without giving you a replacement design. Save its prompt, response and your revision separately. A model critique is assisted work. The facilitator keeps the assessor notes separate from this packet.

## Separate independent and assisted work

First retain the participant's own answer, uncertainties and help requests. During this portion, the facilitator may resolve navigation or explain where to write, but must record any technical hint and stop labeling the affected answer unaided. A missing prerequisite is useful evidence about the route, not a reason to supply the solution invisibly.

Then allow assistance. A participant may ask Codex: “Ask one question about a missing assumption in my answer. Do not supply the solution or execute anything.” Retain the actual prompt and response, plus the participant's revision and explanation of what changed. If Codex supplies an answer despite the request, record that assistance honestly. The assisted revision is a separate result.

An optional execution follows the written decision only when Python and trusted source are already available: use the selected build-input or lost-response walkthrough. Record the command, working folder, source identity, complete result and any help. Skipping execution does not invalidate the written response; it leaves the execution dimension unassessed. Do not install tools or connect AWS merely to finish a reader pilot.

## What the facilitator retains

Use [the learning record](../../curriculum/LEARNING-RECORD.md), leaving all result fields blank until observed. Also record which words or links caused friction, whether the participant could find the requested subsection, which fact changed their decision, and whether the final explanation preserves the exercise's limits. Ask for a brief account of the reasoning, not just a satisfaction rating.

Pause if the participant wants to stop, the packet requires an unexpected prerequisite, or the task drifts into real account/customer work. A partial attempt is a valid observation. Report what happened without converting missing answers into failures of knowledge.
