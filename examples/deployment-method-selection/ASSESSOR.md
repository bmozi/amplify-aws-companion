# Assessor notes: deployment-method selection

Look for a defensible match among business promise, controller, exposure unit, capacity, observations, data compatibility and recovery. More gradual traffic movement is not automatically safer. The learner should name missing evidence rather than fill gaps with assumptions.

### A. Appointment API on EC2

CodeDeploy EC2/On-Premises supports in-place and blue/green deployment types. In-place updates the existing tagged/Auto Scaling instances; its deployment configuration determines how many instances receive the revision concurrently. Blue/green introduces a replacement fleet and load-balancer switch, so it needs temporary fleet capacity and health checks before rerouting. An instance-count rollout is not a request-weight canary: a selected host may serve a non-representative share or all of a particular customer cohort. The near-capacity constraint makes blue/green overlap a cost/capacity risk; in-place has a greater mixed-version interval. The one-day schema compatibility is required for either method. Require instance health plus correct appointment validation, a bounded stop threshold, and verified prior-version serving after rollback.

### B. Customer pricing Lambda

A canary or linear alias shift can limit initial exposure, but a low-volume cohort may not produce enough observations during the configured interval. Hold or use a synthetic/targeted validation that represents discount behavior; do not promote merely because time passed. Use alias/version and deployment events plus alarms, then confirm invocation behavior after rollback. A version rollback does not reverse charges: identify affected requests and run a separate reconciliation/compensation process. All-at-once may be defensible only with strong pre-release validation and accepted impact, but the stated high-impact pricing defect argues for staged exposure.

### C. ECS CodeDeploy blue/green

CodeDeploy ECS requires a load balancer, production listener, two target groups, and an ECS service configured for the CodeDeploy controller. A test listener can send validation traffic to the replacement task set before production traffic moves. It proves only the tested request path and checks; it does not prove every customer segment or sustained peak behavior. Confirm task and target health, application/business metrics and compatible data. Keep the old task set until the agreed bake/observation window passes. Rollback redirects traffic to the original task set; verify actual responses and reconcile any completed side effects. Include the 30-minute duplicate task capacity in the estimate.

### D. Native ECS rolling

With desired count 6, at most 8 running tasks requires `maximumPercent` of at least 134: floor(6 * 1.34) = 8 (ECS rounds down). At least 5 healthy tasks permits `minimumHealthyPercent` of 83: ceil(6 * 0.83) = 5 (ECS rounds up). This configuration allows at most two additional tasks to start before the scheduler needs room, and it must keep five healthy tasks while replacing the old ones. A setting of 84% would round the minimum up to six and prevent stopping an old task until a replacement is healthy. The exact schedule still depends on placement and health readiness; percentages are bounds, not a guaranteed sequence. Circuit breaker detects task start/health failures; CloudWatch alarms can stop on application metrics. Long-running requests require graceful draining and client retry/idempotency evidence, not merely process replacement.

### E. Static internal tool

With low impact, two users, no writes and no meaningful sample, all-at-once can be proportionate. Validate the built files and route first, have the users verify the visible tool, and preserve the prior artifact/configuration for a quick redeploy. Blue/green costs for retained duplicate hosting may not buy enough risk reduction. A canary with zero or one request is misleading; missing evidence should be named, not interpreted as success.

### F. Amplify assumption

Do not infer CodeDeploy configuration support from a Git branch, preview environment or automatic deployment. Verify the current Amplify Hosting feature and the exact connected repository, branch, build settings, domain and rollback behavior. Keep frontend deployment separate from API/database migration and compatibility. If the desired weighted traffic shift is unavailable, consider a separately designed service/controller or a manual staged cutover only after documenting its limits; do not present it as an Amplify-native canary. Identify all automatic triggers and alternate routes before disabling publication.

### G. ECS controller and strategy

Rolling replacement under the ECS controller changes tasks within the `minimumHealthyPercent` and `maximumPercent` bounds; an extra task slot is not a weighted request share. The ECS controller also documents a canary strategy that runs old and new service revisions and shifts a selected share through a supported traffic route before a later full shift. CodeDeploy ECS blue/green is a different controller that uses a replacement task set and deployment configuration for the traffic shift. The answer should inspect the current service controller, strategy, listener/target groups, launch platform, Region support and rollback behavior before choosing or changing a path. Both traffic-shifting options need temporary duplicate capacity, representative candidate traffic, a business check, stop authority and a compatible old revision. Neither undoes a completed external effect or proves that accepted work finished. [ECS controllers and strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html), [ECS canary deployments](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/canary-deployment.html), [CodeDeploy ECS configurations](https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html).

## Scoring guide

Award one point for each of the following in a case answer: (1) correct controller/method distinction; (2) explicit exposure unit; (3) a health and business signal; (4) a meaningful observation window/sample limitation; (5) overlap cost/capacity; (6) compatible recovery target and irreversible-effect handling. A zero for naming a percentage without identifying what it measures. This is an editorial guide, not a calibrated certification rubric or learner result.

The cases are design-only. Current AWS behavior was checked against AWS documentation linked in the teaching unit, but no deployment was executed and no independent technical or learner review has occurred.
