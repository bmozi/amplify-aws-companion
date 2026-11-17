# Reliability experiment review

These six fictional cases require written decisions. They execute no failure injection and authorize no cloud changes. Read [the lesson](../../reader/BOOK-LOCATORS.md#book-56c900b7f81568d4), make your predictions, then use [the assessor notes](ASSESSOR.md). The rubric is an internal teaching aid, not a validated certification score.

For each case state: proceed/hold/stop, the exact evidence supporting the choice, the next observation or recovery action, and the limit of your conclusion.

## Work through one question at a time

Begin with a customer promise, such as “a retried booking must not create another appointment.” Do not try to run every lab simply because it appears in the repository. Each exercise below answers a different question; choose the executable that matches your proposed failure.

1. **Make the decision on paper.** Attempt the six cases below without opening the assessor notes. For an example with explicit times and acceptance windows, use the [bounded resilience tabletop](../resilience-exercise/README.md). Write separately when the fault stops and when useful service is accepted. Its clock is authored scenario data, not a measurement.
2. **Observe one mechanism.** Choose a drill from the table below. Before running, record the expected result and one result that would contradict it. Run only its documented local command with its prerequisites, keep the complete output and source revision, and compare the observation with your prediction.
3. **Challenge the evidence.** Explain how the drill could fail to detect the defect you care about. Use a documented negative control where one exists. An intentionally failing control is useful only when it fails for the intended reason; a missing dependency or syntax error does not validate the assertion.
4. **Transfer the reasoning.** Attempt the new supplier case below without copying an answer. Keep your first response, then ask Codex one question at a time about missing evidence. Record which parts you changed after assistance. Use the assessor only after that attempt.

| Your question | Local exercise | Evidence it can supply | Boundary it leaves open |
| --- | --- | --- | --- |
| Does a bad business result trigger a return to the stable version? | [HTTP canary](../canary-release/README.md) | Sequential loopback requests reveal the candidate's wrong quote and subsequent stable replies | Real traffic distribution, AWS routing and production confidence |
| Can a retry recover a result after its worker exits? | [Lost booking response](../network-selection/README.md#observe-a-committed-booking-with-no-response) | A committed local booking survives the worker; a fresh process returns its original ID | HTTP failures, regional replication and shared authority |
| Does the restored data match confirmed work? | [Recovery reconciliation](../recovery-reconciliation/README.md) | Local restored records are checked against a complete synthetic ledger | Whether a real ledger survives and is trustworthy; cloud cutover |
| Does work already in progress finish during replacement? | [Container replacement](../container-release/README.md) | A bounded local in-flight request and shutdown ordering | ECS behavior and deployment-scale availability; Docker is an additional prerequisite |

These drills are alternatives for a first focused experiment, not interchangeable evidence. Later, combine their conclusions only when the integration itself has been designed and tested. A canary that restores correct new responses has not established that a previous payment was reversed.

### Supplier transfer case

A worker sends a supplier a reservation request. The supplier commits it, but the reply is lost. The worker is replaced. The new worker can read the local queue but cannot query the supplier's result yet. A proposal retries with a new request ID and marks the old item failed after thirty seconds.

Write a short decision record: what is known; what is unknown; whether another reservation may be requested; what identity must survive replacement; what authority can resolve the result; and what the customer should be told meanwhile. The business has not specified how long uncertainty is tolerable. Identify that missing requirement instead of selecting an arbitrary deadline. Then change the case: the supplier can return the outcome for the original request ID. Explain exactly which decision changes and what still needs verification.

No cloud run is required to finish this path. A next live experiment needs its own scoped identity, target, observations, stop/recovery access, whole-run estimate and cleanup proof. Choose whole-run spending and reserve limits for the account you will use. Completing a worksheet or a local drill does not satisfy those prerequisites.

## Six decision cases

1. **A quiet canary.** The candidate has served no requests. The ten-minute waiting period ended and the dashboard shows zero errors. The proposed controller promotes it.
2. **A failed observer.** You block a dependency's network path. The business probe writes its results through the same path. Its last successful result is now four minutes old. The system dashboard still displays that old green value.
3. **A wider target.** The plan says to stop one synthetic worker. The resolved tag selection lists three lab workers and one worker used by a different application. All four are in the same account.
4. **The failure stops; the harm continues.** Dependency access has been restored. The experiment controller says stopped, but 800 accepted jobs remain queued and retries continue. Some completed jobs may have sent duplicate notifications.
5. **A control that contradicts the test.** Removing the drain implementation still leaves the shutdown test green. The test sends its request only after the old server has already exited.
6. **Credits and duration.** Fictional estimates are USD 3.20 for the planned run plus USD 2.10 for the recovery observation and retained resources until cleanup. Fictional available credits are USD 104.80; the reserve is USD 100 and the run limit is USD 5. The proposal counts only injection time and labels itself affordable. No actual prices or account balance are supplied.

After reviewing, choose the canary or retry fixture and write a five-part experiment record: baseline, injected condition, hypothesis, stop rule, and verified recovery/cleanup. Cite actual output if you execute it. A predicted result is not an observation. Ask Codex to challenge one omitted failure mode, then explain whether the existing fixture can test it.
