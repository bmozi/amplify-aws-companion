# Plan the busiest address window

Read [the address-growth lesson](../../reader/BOOK-LOCATORS.md#book-aea48e45d74e17e3), then save an answer before opening the [separate reasoning](PRACTICE-ASSESSOR.md). These fictional address counts assume ordinary private IPv4 subnets with five reserved addresses each. They do not establish actual AWS allocation, quotas or migration feasibility.

A VPC's planning range is `10.44.0.0/24`. Zone A uses `10.44.0.0/26`; zone B uses `10.44.0.64/26`. In each subnet, ordinary work occupies 25 addresses and other components occupy 12. A release adds 20 replacement addresses before retiring the old workers. Keep six addresses free as a required reserve.

1. Calculate assignable addresses, free space in normal operation, and the release margin after reserve in each subnet. Does an immediately possible allocation satisfy the reserve?
2. During that release, a zone fails and the surviving subnet needs 25 additional addresses for recovery. Calculate the shortfall, both before and after the reserve. Does unused space elsewhere in the VPC automatically enlarge this subnet?
3. Compare limiting release overlap, preparing another supported subnet, and redesigning subnet sizes. A proposal expands A to `10.44.0.0/25` without moving B. Identify the conflict. State what service placement, route, dependency and migration evidence each alternative needs.
4. Change the assumption: the replacement needs two addresses per worker instead of one, so its 20 workers require 40 addresses. Recompute. Explain why worker count and address count cannot be silently interchanged and why address headroom alone cannot prove bandwidth or failure capacity.

No resource creation, route changes, or paid service is needed. Retain first reasoning and assisted revisions separately.
