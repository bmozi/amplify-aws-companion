# Dashboard review: assessor notes

Use these explanations to compare your reasoning; they do not test a cloud deployment.

1. Separate metadata/catalog, query execution and presentation. Athena can support ad hoc SQL investigation; recurring manager exploration can justify Quick Sight or another suitable presentation system. The answer must retain query provenance, permitted data and refresh ownership rather than merely name three services.
2. A nightly aggregate cannot establish current order status. Use an authorized operational application path with an explicit freshness requirement. A website login alone does not prove permission to read the requested order.
3. Opening at 09:00 proves neither import refresh nor source completeness. The imported copy predates the stated source completion. Direct query can read the available source but cannot repair upstream omissions. Require successful stage timestamps and a stated data window; distinguish failed refresh from zero activity.
4. Mean shop percentage: (90 + 1) / 2 = 45.5%. Order-level fraction: 10 / 110 = about 9.09%. Empty denominator is undefined, not evidence of perfect or failed delivery. Accept a clearly stated cancellation policy consistent with the business question; reject silently changing denominators between shops.
5. A filter is not authorization evidence. Owner access differs from restricted reader access. Test authorized A rows, denied B rows, an unknown reader, rule changes and direct-source paths with suitable synthetic data. Empty restriction fields can broaden access under the documented rule semantics. Do not assume a removed permission recalls exports.
6. A static report may meet a small, infrequent need with less ongoing administration. Managed analytics can justify its recurring responsibilities when exploration or updates matter. Compare audience charges or capacity, import storage/refresh work, source queries, data retention and operator effort using current applicable pricing before selecting or deploying. No price or winner is universal.

For the transfer case, require time-zone and daylight-saving boundaries, event-time versus arrival-time meaning, revision labeling and reconciliation. Reject a polished chart as a substitute for those definitions. Have the learner revise a deficient answer, then explain how that revision affects the full decision path.
