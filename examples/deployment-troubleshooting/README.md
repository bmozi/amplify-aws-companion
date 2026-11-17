# Find the first failed deployment boundary

This design-only exercise supports the third implementation skill in current DOP-C02 task 1.4: troubleshoot deployment issues. Use [the Unit 03 lesson](../../reader/BOOK-LOCATORS.md#book-f820fa6db990b27a) and draw a timeline before you read the [assessor notes](ASSESSOR.md). All service names and observations below are fictional training evidence. They are not AWS logs and authorize no account change.

For each case, record: deployment ID and revision; platform and target; first failed event; exact evidence source; what is already changed; one safe next read-only check; the smallest proposed repair; rollback/data risk; and what observation would prove recovery. Do not infer “nothing changed” from a failed deployment.

## Case files

### A. The new fix never ran

An EC2/On-Premises deployment fails at `ApplicationStop` on every instance. The candidate revision contains a corrected stop script, but the event log names the old script path. A deployment engineer proposes granting the instance profile `s3:*` and retrying.

**Packet:**

```text
deployment=d-0817  platform=EC2/On-Premises  revision=v18  status=Failed
instance=i-EXAMPLE-4  event=ApplicationStop  hook-source=previous-successful-revision:v17
result=script exited 1  last-message="/srv/shop/current/stop.sh not found"
candidate=v18  contains=/srv/shop/current/stop.sh (fixed)
```

Find the evidence that disproves the proposed permission fix. Name the least disruptive next check and the bounded recovery decision.

### B. The package did not arrive

One EC2 target fails at `DownloadBundle`; other instances have not started their lifecycle hooks. The team suggests opening inbound SSH and increasing the deployment timeout.

**Packet:**

```text
deployment=d-0922  platform=EC2/On-Premises  revision=s3://release-east/rev-18.zip
instance=i-EXAMPLE-8  event=DownloadBundle  result=UnknownError
agent-log="not opened for reading"  bucket-region=us-east-1  instance-region=us-east-2
instance-profile=role/ReleaseReader  access-review=not collected
```

State the two concrete leads in the packet, the actual principal/resource evidence still needed, and why inbound SSH is not the next fix.

### C. Tasks never became healthy

An ECS blue/green replacement task set remains unhealthy. The CodeDeploy deployment is approaching its configured wait limit. Someone proposes switching future releases to all-at-once so the load balancer will stop delaying the deployment.

**Packet:**

```text
deployment=d-1041  platform=ECS  revision=container@sha256:APPROVED-DIGEST
event=Install  replacement-task-set=created  desired=2  running=0
ECS-service-event="unable to pull image: repository tag not found"
target-group=green  healthy=0  traffic-shift=not started
```

Find the first failed boundary. Explain which service events and image/repository permissions to inspect before changing a traffic strategy.

### D. The alias is still split

A Lambda CodeDeploy deployment is manually stopped. The deployment group had no automatic rollback configured. A later deployment fails before shifting traffic.

**Packet:**

```text
deployment=d-1110  platform=Lambda  status=Stopped
rollback=not configured  alias=live  primary-version=41  additional-version=42
additional-weight=0.15  next-deployment=d-1111  status=Failed
```

Describe the state that needs to be understood before the next deployment. Explain why “the stop request succeeded” does not prove the alias returned to one version.

### E. “Succeeded” but requests fail

An ECS all-at-once deployment is marked `Succeeded`. Minutes later, customer requests fail. The replacement task set is now failing load-balancer health checks.

**Packet:**

```text
deployment=d-1204  platform=ECS  status=Succeeded  traffic-policy=AllAtOnce
replacement-task-set=green  service-desired=4  running=4
target-group=green  healthy=0  customer-probe=HTTP 503
database-schema=expanded for new field; old task set still compatible
```

Explain why task count and deployment status are insufficient. Identify immediate customer-safety checks, then name the observations required before shifting back or forward.

### F. The stop is pending

A deployment stop request returns `Pending`. The team wants to terminate all targets immediately and report the release as rolled back.

**Packet:**

```text
deployment=d-1320  stop-request=Pending
instances=5  BeforeInstall=complete  AfterInstall=running on 2 targets
traffic=not yet observed  database-migration=unknown
latest-successful-revision=v15  candidate-revision=v16
```

State what the pending response does and does not establish. Name the next read-only observations and the conditions that would make emergency termination unsafe.

For every case, ask Codex to challenge the order of your checks: “What is the first failed boundary? Which evidence supports it? What was already changed? What would disprove my diagnosis? Cite current AWS primary docs. Do not issue cloud commands, expand permissions, stop deployments or roll back.”

These cases are not calibrated certification questions. The cases use no cloud resources.
