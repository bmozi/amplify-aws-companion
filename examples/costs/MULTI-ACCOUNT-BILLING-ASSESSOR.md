# Assessor notes — Multi-account billing

- In AWS Organizations consolidated billing, the management account is responsible for member-account charges and can inspect aggregated cost data with appropriate permissions. The accounts retain separate sign-ins and resources; an Organization is not a guarantee that every access path is isolated. Verify current organization and policy behavior before implementation.
- Tags can support allocation for supported tagged resources after cost-allocation activation, but missing, unsupported, shared or untagged charges can remain outside a division-tagged view. Tags describe and group eligible cost records; they do not enforce resource permissions.
- The central network and logging cost need an explicit allocation rule, such as measured use, a documented proportional split or a centrally funded shared-service budget. State the chosen rule and its limitations. Do not claim the billing feature knows the business value received by each division.
- Review cost-data access, management-account security and recovery, credits and discount allocation, member-account onboarding/offboarding, and service constraints. A unified invoice can create a concentration of payment responsibility even while workloads remain separated.
- A useful answer distinguishes combined billing, account resource boundaries, identity/policy boundaries and internal chargeback. The exercise contains no actual AWS billing or permission evidence.

Ask Codex to identify any statement in your diagram that assumes one of those boundaries implies another. Verify its challenge against current AWS documentation; do not turn the answer into an Organization setup without a separately approved design and cost review.
