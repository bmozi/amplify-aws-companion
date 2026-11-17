# Assessor: the three independent cost questions

Read this after recording your own decision. The exercise checks reasoning on supplied numbers; it does not authorize an AWS run.

**A:** The run is below the chosen per-run limit. USD 82 would remain in invented credits, above the USD 75 reserve. Gross headroom after the run and USD 2 margin is `50 − 46 − 3 − 2 = −1`, so the decision is **hold**. The credit balance does not make the gross budget row pass.

**B:** The estimate is below the per-run limit; invented credits would be USD 77, above the USD 75 reserve; and gross headroom after the run and margin is `50 − 40 − 3 − 2 = 5`. The output is **review candidate**. A human still needs current identity, plan, credit applicability, service prices, whole-path quantities, competing work, stop conditions and cleanup evidence.

For two USD 3 runs in B, USD 80 − USD 6 = USD 74, below the chosen USD 75 reserve. Two isolated reads of the same USD 80 can each appear to pass. The [commitment lab](../credit-commitments/README.md) demonstrates a local coordinating register, while explaining why that register does not coordinate real AWS jobs on other hosts.

A false applicability or freshness flag holds even if the dollar fields would pass. If both are false, the result lists both missing evidence items; fixing only one leaves the other hold. A true flag is still a **supplied assertion**, not a verified AWS read. If the estimate omits a log group or retained storage, the calculation is internally consistent but incomplete. The operator must inventory the actual path, stop the trigger, verify resource removal and review delayed gross usage and credits. None of the three arithmetic gates constrains a charge after launch.
