# Estimate storage size from growth and headroom

This is a paper calculation with fictional workload values. It provisions no volume and does not read AWS metrics. Show your inputs and units before calculating.

## The repair database

A database currently uses 650 GiB on its data volume. The measured trend adds 40 GiB each month. The team wants a six-month planning horizon and wants at least 20% of the provisioned volume free at the end of that horizon. Assume the trend is steady only for this first estimate.

Calculate the projected data, the provisioned size implied by the free-space goal, and a whole-GiB provisional size. State which additional space may share this volume and which assumptions require measurement. Do not confuse GiB with GB or volume capacity with throughput, IOPS or snapshot storage.

## Change one assumption at a time

1. Growth doubles to 80 GiB per month. Recalculate the same six-month horizon and explain why today's 650 GiB observation is no longer a sufficient size.
2. The database rebuild requires a temporary 150 GiB index file at month six. Include it in the live-volume estimate only if it resides on that same volume.
3. Procurement now takes twelve months, while monthly growth stays at 40 GiB. Recalculate the horizon and explain what makes this forecast less certain.
4. A dashboard says the volume has enough free bytes, but the application's latency target fails during peak writes. Explain why the size calculation cannot settle that performance issue.

Before using the estimate for a real volume, identify the measurement period, forecast owner, free-space warning threshold, backup/recovery requirements, supported volume-size constraints, performance needs, quota and current regional price.
