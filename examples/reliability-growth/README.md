# Screen growth against a one-zone failure

Maya's repair shop has been busier each week. The team sees two application zones and calls the system resilient. This local worksheet asks a narrower question: if the busiest supported zone disappears at the next planning peak, is there enough *attempt capacity* left to complete correct bookings, including retry work? It supports [Unit 07's growth lesson](../../reader/BOOK-LOCATORS.md#book-5010ca3e7f14aced) and [professional reliability case 8](../professional-reliability-path/README.md). All inputs are invented; no AWS resource, API, price or account credit is used.

The JSON fixture keeps **observations**, a **supplied planning case**, a **retry assumption**, two **layout hypotheses**, and **launch gates** separate. The four weekly peaks are 420, 480, 540 and 600 successful bookings/s. The supplied 660 next-week case is a scenario, not a software forecast. With 10% extra attempts and an explicit one-unit-per-attempt simplification, the modeled load is `ceil(660 × 1.10) = 726` attempt units/s. One old 700-capacity zone leaves a deficit of 26 after the other fails. Three 450-capacity zones leave 900 application units after one loss, but the shared data path limits the modeled result to 750, leaving only 24 units of room. The data path's own failure is outside this arithmetic.

Run the worksheet and the changed-condition tests:

```sh
python3 examples/reliability-growth/lab.py
python3 -m unittest discover -s examples/reliability-growth -p 'test_*.py' -v
```

To try a case, copy `fixture.json` to a temporary file and pass `--fixture /path/to/copy.json`. Change only one assumption first. Reduce the candidate's shared-data capacity to 700; change the weekly history without changing the supplied planning case; or give the launch enough compatible placement while leaving its permission and ready-target checks false. Explain why a passing quota does not make the fleet ready and why even four reported ready workers cannot prove a correct booking. The script lists each failed AZ and the worst modeled margin, plus separate provisioning blockers. It never says a layout is safe or ready for production.

The [assessor](../professional-reliability-path/ASSESSOR.md) explains cases 8–9 after a first attempt. Ask Codex to find an assumption the calculation hides: retries may cost unequal work, a source may throttle, the data path may fail with the AZ, a replica may lag, or the normal sign-in route may be unavailable. Require a proposed measurement and a rollback trigger, then check the reasoning yourself.

Real use needs selected-account applied quotas, compatible capacity, permissions, target registration, customer-level probes, data/write authority, peak and fault measurements, current prices and cleanup. A future live trial also needs scoped non-root access and a whole-run estimate within spending and reserve limits chosen for its account. A multi-Region or Organization-dependent extension remains design-only in this project. Passing this local lab establishes arithmetic for its fixture, not AWS reliability or independent learner mastery.
