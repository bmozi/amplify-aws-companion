# Multi-account billing: one bill, several boundaries

This design exercise uses invented companies and amounts. It creates no AWS Organization or account, reads no bill, and changes no account setting. Answer before reading [assessor notes](MULTI-ACCOUNT-BILLING-ASSESSOR.md).

## Scenario

Three divisions run separate workloads. Each division should control its own application resources and day-to-day access. The finance team wants one payment relationship and a combined monthly cost view. A central logging bucket and shared network are used by all three divisions. One team asks whether setting `Division=North` on every resource is enough to guarantee both isolation and complete cost attribution.

Draw or describe the account and billing boundaries. Then answer:

1. Which account pays the consolidated bill, and what account relationship makes that possible?
2. Does a combined bill put all workloads into one account or grant every division access to every other division's resources?
3. How would you allocate the shared network and logging costs, and which part of that allocation is a business rule rather than an automatic tag result?
4. Which costs or resources could remain outside a division-tagged view?
5. What must be decided about access to billing data, payer-account protection, credits, discounts and member-account exit before implementation?

Do not propose joining the personal learning account to an Organization. Keep this as a paper design until there is an approved multi-account boundary and a separate cost review.
