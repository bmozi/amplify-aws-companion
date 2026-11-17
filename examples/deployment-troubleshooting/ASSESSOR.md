# Assessor notes: find the first failed deployment boundary

The packet is synthetic and intentionally small. Good answers lead with evidence, say what has not been established and select one bounded next check. A retry can be appropriate after identifying a transient failure; it is not a substitute for diagnosis.

### A. The new fix never ran

The first failure is the `ApplicationStop` event from v17, the previous successful revision. v18's corrected file cannot fix an event that fails before v18's install hooks run. Inspect v17's deployed files and the deployment/instance log; verify how the stop script is located and whether the application exists in that target path. A temporary choice to ignore the failed stop hook is consequential: only after assessing prior side effects, customer traffic and service state should an operator decide whether to bypass it and use v18's corrected hooks. Granting `s3:*` does not address the missing old local script. Do not teach `--ignore-application-stop-failures` as a reflex.

### B. The package did not arrive

Two evidence-based leads are a cross-Region revision bucket and the instance profile's uninspected read permission. Verify the actual instance identity, bucket/object ARN and Region rules, repository/bucket policy, any encryption key policy, agent log and outbound endpoint path. The event is a download failure, so inbound SSH is not the first fix. Avoid expanding permission until the actual denied request and resource are known. The packet does not prove which lead caused the failure; it lists both as hypotheses.

### C. Tasks never became healthy

The first failure precedes target health: ECS could not pull the image because the named repository tag is absent. Verify immutable image digest/tag, registry/repository/Region, execution-role pull permission, network path and task/service events. Only after tasks run should you examine container startup, health checks, target groups and the deployment wait. All-at-once changes exposure; it does not repair a nonexistent image and may make the blast radius larger.

### D. The alias is still split

The packet states two weighted versions remain on alias `live`; the stop did not restore one version. Inspect CodeDeploy/Lambda deployment events and the alias's current version weights. Determine the intended stable version and use the documented recovery procedure with rollback configuration considered. Do not launch another deployment against an unexplained alias state. No traffic or request behavior is shown here, so verify actual invocations after a state repair.

### E. “Succeeded” but requests fail

The deployment status and desired/running task counts say nothing about target health or business correctness. Current evidence shows zero healthy targets and HTTP 503s after an all-at-once shift. Protect customers first by using the established traffic/rollback procedure and confirming the currently serving task set, listener and database compatibility; do not speculate about the cause of every 503. Then inspect target health reason codes, service events, application logs and requests. Compare the actual previous and new task set. The expanded schema permits both versions according to the packet, but does not prove data correctness or safe rollback.

### F. The stop is pending

`Pending` means the stop has not completed; lifecycle events may still be running and files/scripts may already have changed. We do not know whether traffic has moved or a migration committed. Inspect deployment and per-target events, current traffic/health, database migration state and business records before terminating hosts or claiming rollback. Emergency termination may prevent cleanup or leave mixed versions and data state. Resolve customer safety and preserve evidence while following the approved incident authority path.

A complete answer distinguishes a failed deployment from a reverted system. CodeDeploy can roll back by deploying a previous revision as a new deployment. That does not reverse database changes, external calls or already completed scripts. Verify a representative customer operation and reconcile business records after platform health recovers.

The evidence packets do not emulate CodeDeploy and were not tested against AWS. They are teaching cases.
