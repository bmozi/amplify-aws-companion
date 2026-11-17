# Assessor notes — EBS volume selection

- The database's small, random I/O and latency requirement point first to SSD. General Purpose SSD may fit broad transactional needs; evaluate Provisioned IOPS SSD only if measurements and latency requirements justify it. The prompt does not contain enough evidence to select an exact volume configuration.
- The frequent large sequential scan is a candidate for Throughput Optimized HDD (`st1`) when its throughput, scan deadline and instance limits fit. If the workload changes to small random I/O, reassess rather than preserving HDD because it looked cheaper.
- The infrequently accessed sequential archive is a candidate to evaluate with Cold HDD (`sc1`) if its retrieval deadline, throughput and access pattern fit. Infrequent access alone is not sufficient; a five-minute restore promise may make a slower or differently staged design unsuitable.
- `st1` and `sc1` are not boot volumes. The added boot requirement forces the learner to choose a supported boot-volume design separately or change the architecture.
- Measure I/O size, random-versus-sequential distribution, read/write mix, IOPS, throughput, latency percentiles, concurrency and workload duration. Compare the attached instance's limits with the volume's limits. A volume setting cannot compensate for an instance bottleneck.
- Estimate provisioned capacity, IOPS/throughput settings, snapshots, instance and data-transfer costs with current regional prices. The case has no price table and does not prove any price ranking.
- This lesson provides selection reasoning only. No EBS configuration, benchmark, restore or account activity occurred; independent learner review remains pending.
