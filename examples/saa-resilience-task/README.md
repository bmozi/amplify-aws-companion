# Eight ways a resilient design can still fail

This is a reader assessment for [SAA-C03 task 2.2](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03-domain2.html#solutions-architect-associate-03-domain2-task2). AWS names eight applied skills under that task. These eight original cards practice one skill each; they are neither AWS exam questions nor a calibrated mock exam. Read [Chapter 7](../../reader/BOOK-LOCATORS.md#book-20703bba15f79b2d) and [Chapter 8](../../reader/BOOK-LOCATORS.md#book-f72a70eb301cb115) first. Keep the [assessor notes](ASSESSOR.md) closed until you have written your own answers.

Maya's repair company accepts bookings and photos. A confirmed booking must remain correct after one Availability Zone fails. Photo processing may wait up to 30 minutes. The figures below are **fictional inputs**, not measured AWS capacity or account quotas. For every card, write the customer promise, selected design, first observation that could reject it, cost or operating consequence, and what would still need an authorized cloud test. Draw both the serving path and the path an operator needs to recover it. Mark an unknown as unknown.

## 1. Repair the recipe before the next replacement

During an incident, an operator changes a network rule in the console. The next infrastructure plan would remove that change and replace a database policy. The team cannot yet tell whether the console change was an emergency fix or an unsafe shortcut. Decide how to compare desired, recorded and running state before any apply. Name the person who may approve the outcome and the evidence needed to recover from a partly completed apply. **Changed fact:** the recorded state belongs to another environment.

## 2. Count what survives one location loss

Peak demand is 600 confirmed-booking attempts per second. Two application zones can each serve 400; a shared database path can serve 700. One zone fails. Calculate the resulting ceiling and explain what can be promised at peak. Compare a third 400-capacity zone with two 700-capacity zones. **Changed fact:** the shared database path now fails independently. What part of your earlier comparison no longer settles the customer outcome?

## 3. Measure the booking, not the server light

During one minute, 600 booking attempts reach the application. Four hundred complete correctly, 100 receive a definite refusal and 100 have no known result before the customer deadline. Every application target reports healthy. Define the denominator and at least two distinct business measures you would report, including how uncertain attempts appear. **Changed fact:** the next minute has zero attempts. Decide whether that is a healthy result or missing evidence, and how you would tell.

## 4. Find the shared recovery dependency

Two serving fleets are in different zones. Their recovery instructions, operator login and last-confirmed-booking journal all depend on one office server. An office power loss blocks those tools while the fleets remain reachable. Draw the two paths and propose a bounded change that removes the relevant single point. **Changed fact:** independent operator login works, but the journal still cannot be read. Decide what you may safely reopen.

## 5. Restore the right business facts

A new backup restores with the expected row count, but booking 111 has the wrong amount. An older backup has the correct amount and is missing a later confirmed booking 112. Decide what evidence is needed before choosing a recovery point, replaying work and reopening writes. **Changed fact:** the older backup's decryption key is unavailable in the recovery location. What does a green copy-job receipt establish now?

## 6. Put the whole recovery under the clock

The business target is useful booking service within 30 minutes and no more than five minutes of confirmed-work loss. A pilot-light plan spends 4 minutes detecting and approving, 17 preparing workers, 7 reconciling data and 5 checking a real customer path. Assume these stages are sequential. Calculate the total, then compare a warm standby that cuts preparation to 3 minutes while adding recurring cost. **Changed fact:** a wrong booking amount was replicated into the standby. Revisit the data-loss and reopening decision.

## 7. Respect the old application's state

The vendor-supported application keeps sessions and uploaded files on its local machine and cannot be changed this quarter. A second instance passes `/health`; the first dies after accepting an upload. Predict what a returning customer can actually retrieve through the second instance. Compare a sticky load-balancer policy, a supported shared-state mode if the vendor offers one, and an honest narrower promise. **Changed fact:** every registered target reports unhealthy. Decide whether the load balancer is guaranteed to stop traffic.

## 8. Choose the managed part for its actual job

The team proposes writing its own health-based DNS switch and backup scheduler. A colleague proposes managed routing, managed backups and a database proxy instead. The booking application may still issue a duplicate confirmation after a lost database reply, and an old writer may remain reachable. Choose which responsibilities a suitable managed service could take, which business rules stay with the application, and what operating and cost evidence would decide between the proposals. **Changed fact:** photo analysis can wait, but booking confirmation cannot. Explain whether the same recovery policy should govern both.

## Preserve your first answer

Use four columns: **case**, **my first decision**, **observation that would reject it**, **revision after the changed fact**. Record whether you used Codex and exactly what it supplied. Ask it to challenge one missing dependency or unsupported AWS claim, then verify any service claim against the cited chapter sources. Only after recording the revision, open the [separate assessor](ASSESSOR.md). A correct answer to these authored cases is practice evidence, not independent learner validation, live AWS behavior or certification readiness.

This packet uses no AWS account and creates no resource. A multi-zone or regional implementation must remain a design exercise until its identity, workload, complete cost, spending limit, stop and cleanup plan are reviewed for the actual account. Choose limits from your own account and purpose rather than copying someone else's lab budget.
