# Plan a migration portfolio before scheduling a wave

This fictional paper lab uses no AWS account, real records or current prices. Read the [migration lesson](../../reader/BOOK-LOCATORS.md#book-9fb6047993bd4d40) and write your own decision before opening [assessor notes](ASSESSOR.md). The point is to distinguish an application inventory, a seven-R decision, a cost comparison and a cutover schedule.

## The repair-school portfolio

Maya's company runs training and repairs from two sites. Its annual planning window is 12 months. The team can rehearse **one customer-facing change per month** and can support **one major cutover per month**. A $500/month legacy identity service is shared by the booking portal and the reporting job; nobody has confirmed how the portal authenticates when that service is unavailable. The school closes for five days in July; bookings still arrive online then. All numbers below are invented dollars, not AWS rates.

| Workload | Business promise and source evidence | Dependencies and known constraints | Current monthly cost | Candidate monthly cost | One-time move/test | Overlap |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| A. Booking portal | Appointments and payment references; owner confirms 30-minute recovery and at most 5-minute interruption | Uses identity service; payment webhook; identity fallback **unknown**; busiest in August | 1,000 | 650 | 2,000 | 1 month at current cost |
| B. Nightly report | Finance receives prior-day totals; owner confirms next-day recovery | Reads booking database; data contract documented; can be paused for two days | 280 | 180 | 600 | 1 month at current cost |
| C. Drawing archive | Staff must read old repair plans for seven years; last write date is observed | 4 TiB file share; retention owner confirmed; no new writes; retrieval deadline unknown | 240 | 110 | 900 | 1 month at current cost |
| D. Label printer controller | Prints physical safety labels on site | Vendor says current interface requires on-premises hardware; vendor support ends in 10 months | 120 | unknown | unknown | unknown |

The identity service is shared cost and **is not included** in the workload rows. Candidate costs are placeholders that omit request, network, backup, monitoring, support, tax and labor until investigated. The archive candidate also omits retrieval charges. No quote or utilization measurements have been obtained.

## Your decision record

1. For each row, name the business owner, evidence you would seek next, a provisional seven-R strategy, and a reason to keep or change it. Say which facts are observed, owner-confirmed or unknown. Do not assume a server list is an application inventory.
2. Draw dependency arrows among A, B, the identity service and the payment webhook. Mark the link that has not been tested. Select a tracking tool or record, say which source data it would ingest, who maintains it and which decision it supports. Distinguish progress tracking from business acceptance.
3. Propose the **earliest defensible** migration wave for each workload or mark it blocked/retained. State the team's capacity, change window, dependency group, owner, rehearsal, rollback boundary and acceptance check. Explain whether B can move before A, and what would have to be tested.
4. Calculate a provisional 12-month comparison for A, B and C separately: `current = current monthly × 12`; `candidate = candidate monthly × 12 + move/test + overlap`. Do **not** allocate the $500 shared identity cost without an explicit rule. List the omitted categories and say whether the arithmetic supports a purchase or only discovery.
5. Give the decision owner a one-page recommendation: what can be investigated now, what may be scheduled after evidence, what remains retained, and which cost and recovery promises can actually be supported.

## Change card: a fact changes the route

The portal owner now reports that the payment webhook retries for only 90 seconds, and the identity service must be decommissioned before August. The July closure no longer provides a quiet window because online bookings continue. A tester finds that B's report reads an undocumented table that the proposed target schema omits. The archive owner changes its retrieval promise from “within a day” to “within 15 minutes.” Revise the strategy, sequence, tests and cost inputs. Which earlier green-looking assumptions are invalid? What would you tell the business before naming a date?

Ask Codex: “Find one unknown that could reverse my wave order, one cost I counted twice or omitted, and one acceptance test that would fail after a technically successful copy. Mark every unverified assertion.” Check any AWS service claim against current AWS documentation. A convincing answer is still a hypothesis until the owners and evidence support it.
