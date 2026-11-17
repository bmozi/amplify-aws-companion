# Assessor: what the local cluster actually established

Use this after writing predictions and changed-case answers. The expected booking value is an invented fixture, not customer data.

1. Two of two ready Pods and an available Deployment show that Kubernetes could place and route to both local processes. The deliberate first request returns HTTP 200 with 900 cents, so the 2,300-cent customer requirement fails. A rollout status alone cannot certify the booking answer.
2. The environment change creates a new ReplicaSet. A completed local rollout plus the Service request returning 2,300 cents supports this one corrected synthetic path. It does not prove all clients, data versions or persistent state are correct.
3. The worker's Pod stays Pending. Its scheduler condition reports `Unschedulable` and insufficient local CPU. The manifest requested capacity; it did not supply capacity. The exact message and time are observations from the local machine, not a portable EKS result.

For the changed cases: a single correct response can miss a mixed rollout; inspect Pod/ReplicaSet revisions and repeatedly exercise the selected path under a stated sample boundary. Readiness may stop traffic when a necessary dependency is unavailable while liveness still reports that the process can run; restarting every Pod for a shared dependency outage can worsen recovery. An oversized CPU request should be compared with measured CPU demand, node allocatable resources, workload limits and the customer latency promise before adjustment. A cross-tenant booking leak is an authorization failure even if every probe and booking amount is correct. This fixture has no authentication or tenant model, so that denial cannot be performed here.

The local run is an implementation observation for A23's scheduler/readiness/customer distinction. It is not an EKS deployment, a priced AWS experiment, a learner result or a production acceptance test.
