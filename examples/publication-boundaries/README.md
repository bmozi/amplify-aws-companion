# Publication boundaries: stop the delivery without losing the shop

This original fictional exercise follows the [GitHub publishing lesson](../../reader/GITHUB-TO-AMPLIFY-FIELD-LESSON.md). No AWS account, commands or spending are required. These packets describe an invented setup, not our account. Write an answer to each packet before opening the assessor notes.

## Start with the owner's request

Maya keeps three repositories: a customer notebook, a Python calculator and a training book. Only the notebook should publish to Amplify. She says: “Pause releases while I review a change, keep the current notebook available, and do not publish the other projects.”

Draw four boxes: source repository, release trigger, publishing identity and destination. An arrow needs both a reason to start and permission to act. Label each arrow with the evidence you would inspect. Keeping a recipe on a shelf is different from giving a delivery worker permission to serve it.

## Packet 1: one switch looks reassuring

The supplied fictional inspection finds:

- Native automatic builds are disabled on the notebook's connected branch.
- A GitHub Actions workflow also publishes that branch after a push.
- An already-started deployment job is still running.
- The calculator and book have no configured deployment route in the supplied inventory.
- The current notebook website and its backend remain available.

Can Maya safely say that new publication has stopped? Identify the remaining routes and the separate decision about the active job. Explain why deleting the app would contradict her request. State the limit of the supplied inventory rather than claiming to have audited her entire GitHub account.

Fill in this record for every release route:

| Source and event | Controller | Identity and destination | Pause action | Read-back and behavior evidence |
| --- | --- | --- | --- | --- |
| Your answer | Your answer | Your answer | Your answer | Your answer |

## Packet 2: the badge is called “publisher”

The workflow uses temporary credentials for a role named `NotebookPublisher`. Its supplied permissions include publishing to any hosting app and passing a broad infrastructure execution role. A local publishing script rejects root. The trust configuration and any other permission boundaries have not been supplied.

Explain why the name, temporary credentials and local root guard do not prove that this workflow is restricted to the notebook. Separate who may obtain the role from what a session can do. Specify the policy evidence and allowed/denied operation checks needed before expanding deployment. Keep frontend publication separate from backend infrastructure changes. Do not invent an exact IAM policy from these incomplete facts.

## Packet 3: restart and retire are different requests

During the pause, five commits accumulate. Three edit lessons, one changes application code and one changes backend configuration. Maya now wants to resume publication of the reviewed application change. No build result or approved release revision is supplied.

Write a restart plan that identifies the intended source revision, build configuration, backend implications, destination and verification. Explain why selecting an application subfolder does not by itself prove that lesson-only commits cannot trigger builds. Do not assume that re-enabling a switch identifies the version eventually served.

Then change the request: Maya wants to retire the notebook and stop its resource use while keeping its source. List the hosting, backend, stored-data and log inventories you need, the removal verification and the later billing reconciliation. Account credits and prices are unknown. Any future live exercise needs a whole-run estimate and credit reserve chosen for the account in use. Deleting resources does not instantly produce a zero bill.

## Transfer and AI review

Move the application and training book into different folders of one repository. Would repository selection alone preserve the desired release behavior? Explain the build-root versus trigger-filter distinction and propose evidence for any chosen filter. Your answer must still identify the publisher's authority and the off switch.

Save your first answers. Ask Codex: “Find an uninspected release path or an unsupported permission claim in my record. Explain which evidence would settle it. Do not change cloud settings.” Keep the critique and revision separate in the [learning record](../../curriculum/LEARNING-RECORD.md), then consult [assessor notes](ASSESSOR.md).

Completion means a reasoned initial answer, evidence-driven revision and changed-case answer. It does not mean a pipeline was installed, a pause was tested in AWS, or independent learner mastery was established.
