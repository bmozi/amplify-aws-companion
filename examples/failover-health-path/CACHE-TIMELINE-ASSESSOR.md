# Timed DNS cache: assessor notes

Attempt the questions in the [exercise](README.md#follow-three-resolver-clocks) before reading these notes.

1. At second 110, the authoritative answer has changed to standby. A and B still return primary from their caches: A's entry expires at 300, B's at 380. C has no prior entry and asks the authority, so it receives standby. These are three resolver observations, not a measured share of customers.
2. Lowering the response TTL at 120 does not change the expiry carried by A or B's earlier 300-second responses. A refreshes at 300 and its new 30-second standby answer expires at 330. B returns primary at 379 and refreshes to standby at 380. A team that changes TTL only after an incident cannot infer an immediate migration of previously cached clients.
3. If the **old** TTL had been 30 seconds when B fetched primary at 80, that entry would expire at 110. A lookup at 110 could then receive standby under the supplied authoritative switch. The model would still not prove health-check detection time, all resolver behavior, persistent connections or a successful booking.
4. At 380, the three named resolvers' model observations no longer include an old primary answer. That is not a license to claim every customer has moved. Unknown resolver caches, client caches and established connections are outside the model. Even a standby response says nothing about a customer's authorized read, correct writer or preserved booking.

An AI tutor can generate another timeline, but make it state each resolver's **fetch time, TTL and expiry** before it predicts an answer. Challenge a response that equates a new authoritative answer with every client's next request. These notes explain a fictional ideal-TTL model, not observed AWS DNS or customer recovery.
