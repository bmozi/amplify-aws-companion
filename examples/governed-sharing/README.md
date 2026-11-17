# Review a governed analytical dataset

This is a design-only exercise using fictional observations. Read [the sharing lesson](../../reader/BOOK-LOCATORS.md#book-b3810ca13d4ae805). No AWS account, credentials or paid query is required.

For each case, write the decision, the enforcing component, the evidence missing and one test that could contradict your conclusion. Answer before reading [the assessor notes](ASSESSOR.md).

## Six cases

1. **Catalog success.** A crawler creates a table and the query runs. A source ID `001` appears as `1`; the total dollars match. Is the dataset ready to publish? Name the contract check that the total missed.
2. **Two writers.** Athena and another engine both advertise Iceberg support. The second uses a different locking implementation. The team proposes concurrent updates because both can read the table. What compatibility evidence is required before writing?
3. **Denied through one door.** A fictional analyst is denied a sensitive query but can download the corresponding raw object directly. The team calls the data protected because the query denial worked. Which conclusion is actually supported, and what access path needs repair?
4. **Permission with a promising name.** A principal receives `DATA_LOCATION_ACCESS` and expects to read every table at that location. Explain what that permission concerns and why the read decision still needs investigation.
5. **Ten purchases, one person.** The fictional sharing policy requires at least five distinct customers per output group. A campaign group has ten sales from one customer. Another has five customers with one sale each. Decide which satisfies this one condition. Do not infer that satisfying it proves overall privacy or query eligibility.
6. **A grant is withdrawn.** Yesterday's permitted report was exported to a partner's storage. Today the table permission is removed. What can be claimed about yesterday's copy? Add ownership, retention and evidence requirements for outputs to the design.

## Build the review packet

Draw the chosen internal query path, direct-object path and output path. Add a separate collaboration path only if the partner's needs justify it. Compare a reviewed static export, governed internal querying and constrained partner analysis against freshness, authority, retained copies, operator effort and cost. State which business constraint would change your selection.

List allowed and forbidden identities, exact data fixtures and expected outcomes for each path. Separate metadata discovery, table commit behavior and authorization tests. Name selected engine versions and writer coordination as unknown until checked. Explain how a failed write, late correction or maintenance operation might affect the published report and what evidence would resolve that uncertainty.

Ask Codex to find a claim your proposed evidence does not establish. Keep the original answer and your correction. This exercise does not deploy a policy, certify privacy or test Iceberg concurrency.
