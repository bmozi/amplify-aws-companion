# Fleet maintenance: observe, stage, verify

Run `python3 examples/fleet-maintenance/lab.py` from the repository root. This standard-library lesson uses invented node records and fixed outcomes. It makes no network calls, does not use the AWS CLI or SDK, and cannot patch a computer.

Imagine a repair business with six fictional servers. A target selector finds nodes by environment and job. Before any change, compare that result with an approved ID list, check that each node is managed and its inventory is recent, and confirm that every target uses an eligible operating-system family. Unknown inventory blocks the campaign; missing evidence is not a clean bill of health.

The exercise then uses one operation ID across a canary, pilot and fleet ring. The canary must finish and pass the supplied application-health check before another ring starts. A failed canary stops expansion. Replaying the same operation ID returns its recorded outcome without counting a second patch attempt. The report shows intended baseline, selected targets, per-node outcomes and explicit residual uncertainty.

The scenario's `max_errors=0` is a teaching policy: stop sending work to later targets after the first failure. It does not represent every AWS setting or imply that running work is canceled. AWS Systems Manager Automation rate controls can stop dispatching new work after an error threshold, while work already running may complete. The figure and lesson make that distinction visible.

## Try the changed cases

1. **The canary's service check fails.** The next ring must remain untouched. State whether the failed patch was reversed. It was not: the exercise only stops expansion and requests investigation.
2. **Inventory is too old.** Do not infer that an old node is compliant. Refresh evidence or investigate why it stopped reporting before including it.
3. **A new server matches the selector but is absent from the approved ID list.** Stop before patching. Widening the target from “the known list” to “whatever matches a tag” is a separate review decision.
4. **The same event is delivered again after the canary result was saved.** It must return the recorded result without applying the patch twice in this model. This is local request de-duplication, not proof that an AWS operation or OS package manager is exactly-once.
5. **The patch baseline changes between scan and install.** Bind the operation to the reviewed baseline version; otherwise the plan the operator approved may differ from the one installed.
6. **Patch compliance is green, but the application health check fails.** Report both facts. Compliance with the selected patch rule does not prove the customer workflow works.

The lab is a deterministic decision-policy check, not a Systems Manager emulator or certification predictor. A real rollout needs a supported OS and Region, current package/baseline policy, managed-node identity and network path, target proof, maintenance window, recovery evidence, workload health criteria, an authorized non-root role, a current whole-run estimate, and spending and credit-reserve limits chosen for the account. Organization-wide patch policies remain design-only unless separately authorized in a suitable environment.
