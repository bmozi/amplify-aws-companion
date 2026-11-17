# Distributed and hybrid compute placement

Design-only cases for [Unit 02](../../reader/BOOK-LOCATORS.md#book-da9067d59d69025b). They compare regional processing, CloudFront edge functions, special AWS locations and Outposts. No distribution, function, Local Zone, Wavelength Zone, network link or Outpost is created.

For each case, draw where the request, decision and authoritative data live. State what happens when the closest service, customer network or AWS Region is unavailable. “Closer” is not an availability or offline guarantee.

## Cases

1. **Normalize a web request:** The application needs a small header rewrite and consistent query-string ordering before cache lookup. Does a CloudFront edge function fit? What must the team check about cache keys, authorization and test coverage?
2. **Use a library and external policy service:** A request needs a supported runtime/library and a network call to a regional policy service. Compare CloudFront Functions, Lambda@Edge and regional compute. Where is the authorization decision authoritative, and what happens if the regional call times out?
3. **Factory equipment path:** A machine must transform sensor data locally because round trips to a Region miss the response deadline. Some actions must continue during short WAN loss. Compare a regional worker, a local edge service and Outposts. Identify the real disconnected-mode requirement, local data boundary, service-link dependency, site constraints and recovery behavior that must be proven.
4. **5G city sensor:** A sensor gateway needs low-latency processing near a carrier's 5G network. Compare ordinary regional processing with Wavelength Zone placement. What provider/geography, supported service and network availability questions must be answered first?
5. **Region recovery:** A team proposes two Regions because its users are worldwide. Separate user latency from disaster recovery, identify which data and dependencies must be copied, and state how the application selects and validates the recovery Region.

## Decision record

| Question | Answer |
|---|---|
| User, equipment or data location that matters | |
| Latency or disconnected-operation requirement | |
| Candidate placement and supported service/runtime | |
| Authoritative business decision and data | |
| Regional, AZ, local network and service-link dependencies | |
| Behavior when that dependency is unavailable | |
| Current Region/feature/capacity/cost evidence | |
| Reversal signal and next safe test | |

Use current AWS product documentation for the exact service form, supported runtime, account access, Region and network conditions. This worksheet does not establish AWS service behavior or quote a price.
