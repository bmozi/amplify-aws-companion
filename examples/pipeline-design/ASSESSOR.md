# Pipeline design: assessor notes

These notes offer reasoning checks for the five cases. They do not prescribe one AWS product or prove a learner's competence. A sound answer names its assumptions, follows the customer change through discovery, design, implementation, checks, release and operation, and revisits earlier decisions when evidence changes.

1. **Portfolio:** A pull request can trigger CI checks without publishing. A deliberate merge/approval can gate production publication. One account keeps a personal lab simple, but the answer should still separate the publishing identity from broad account administration, consider build/log/storage charges, and identify how to disable that publication route. A successful build does not prove the public site serves the intended version.
2. **Contact form:** The new data-use discovery changes the requirements and design. Consent/purpose, recipient, retention and access need review; tests should check the actual data flow and expected rejection/acceptance. A green compile or unit test cannot establish an approved customer-data use. Stop promotion until the design and evidence fit the revised requirement.
3. **Booking service:** Distinct accounts can create stronger isolation and separate access/billing controls. The delivery design must still specify how an approved artifact is handed from build to test and production, how identities are trusted, how artifacts and keys are accessible, what approvals exist, and where logs/recovery evidence live. Separate accounts do not automatically make the pipeline safe or bookings recoverable. Include compatible schema/data recovery and cost for parallel environments.
4. **Small team:** A minimum viable pipeline can begin with version control, repeatable build, useful fast checks and one clearly controlled destination, then add staging, stronger separation or approvals as risk/operational capacity grows. Avoid both extremes: treating complexity as free and treating one account as universally safe. Document ownership and failure handling so a small team can operate it.
5. **Stop publication:** Inventory repository triggers, branch rules, connected hosting/build integrations, manual starts, queued/in-progress executions and any alternate publisher. Disable the intended route, inspect and resolve active work, then test that a harmless later commit does not publish. Decide whether already-built artifacts or the hosted app should remain available. Preserve unrelated GitHub use. A commit can accumulate while delivery is paused, so later re-enable needs review and possibly a controlled catch-up release.

## Common reasoning misses

- Describing a pipeline as the whole SDLC, rather than automation for selected repeatable steps.
- Treating phases as an inflexible waterfall, or saying Agile means no planning/design.
- Confusing continuous delivery with continuous deployment: the production-approval boundary differs.
- Rebuilding separately for every environment without recognizing the result may no longer be the artifact that passed the earlier checks.
- Assuming a second account alone grants safe cross-account delivery; access, trust, artifact, encryption and audit paths still need design.
- Calling one-account deployment inherently wrong for every lab, or multi-account inherently secure without effective-policy and operational evidence.
- Treating a paused trigger as a full stop when manual runs or another integration remain active.
- Omitting logs, parallel environment costs, clean-up owners or recovery from the comparison.
- Accepting a Codex answer as authority. Check current service-specific claims against AWS primary documentation and record uncertainty.

## Transfer question

If the organization changes from a static site to an API that stores bookings, which assumptions change? A strong answer revisits data classification, privacy, availability, database compatibility, identities, testing, deployment strategy, recovery and cost. It retains the useful lifecycle and pipeline principles while selecting new service-specific controls from current evidence.

This assessment has not been calibrated with independent learners. No AWS account, organization, role, pipeline or bill was examined or changed.
