# Assessor notes — storage size

- Projected data after six months: `650 + (40 × 6) = 890 GiB`.
- The used share is `1 - 0.20 = 0.80`. Provisional capacity is `890 / 0.80 = 1,112.5 GiB`; round upward to at least 1,113 GiB if the chosen service permits that size. This is an estimate from stipulated values, not a recommended production volume.
- At 80 GiB growth per month: projected data is `650 + 480 = 1,130 GiB`; with 20% free-space target, capacity is `1,130 / 0.8 = 1,412.5 GiB`, so at least 1,413 GiB under the same assumption.
- If an additional 150 GiB temporary index file resides on the volume at month six, projected occupancy becomes 1,040 GiB, and capacity at the 20% free target becomes 1,300 GiB. If it resides elsewhere or is temporary only during a different phase, describe that distinction instead of counting it automatically.
- A 12-month growth horizon gives `650 + 480 = 1,130 GiB` projected usage and 1,412.5 GiB capacity at 20% free. The calculation is more uncertain because the forecast reaches farther; refresh it with observed growth and an explicit contingency rule.
- Free bytes do not explain latency. Measure I/O size and pattern, IOPS, throughput, latency distribution, queueing, peak concurrency, and instance/volume ceilings. Change performance only after identifying the bottleneck.
- Snapshots and backup retention need a separate storage/cost and restore plan. This example does not include them in live-volume capacity or estimate their bill.
- The estimate does not establish current prices, exact AWS service eligibility, a configured alarm, an approved threshold or a successful restore. Independent learner review remains pending.
