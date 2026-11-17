# Assessor notes: security audit evidence join

Expected reasoning:

- A record matches only when its account, Region and full resource identifier match, its source is expected by the finding, and its event timestamp is within the finding's stated interval. An observation timestamp inside the window does not make an earlier event contemporaneous.
- A same-name resource with another account, another Region, a different identifier, an unexpected source or an out-of-window timestamp must not be silently joined.
- A `partial`, `not_configured` or missing coverage row keeps the relevant source unknown even when another source has evidence. An empty expected-source list is also unknown, not complete. Coverage is keyed by exact source, account, Region and resource. A complete synthetic coverage row only describes the fixture's assertion; it does not prove an AWS recorder or detector was configured.
- The synthetic alert candidate matches only when severity meets the threshold and category, environment, account and Region match. The near-matches demonstrate which one condition rejected them. The owner, next check and delivery-failure route are design fields; no EventBridge rule, CloudWatch alarm, notification or actual delivery is tested.
- A matching audit record is corroboration to inspect, not proof that the action caused the finding, exposed data or compromised an account. Contradictory evidence should remain visible.
- A useful alert names the condition, owner, exact target, source, event time, delivery failure path and next read-only check. A near-match should not alert. Automated remediation needs a separate authority and recovery review.

The fixture is authored canonical data, not an AWS event parser, alert-rule emulator, integration test, service emulator or security assessment. Independent review, learner performance and live behavior remain untested.
