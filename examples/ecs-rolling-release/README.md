# ECS rolling-release design cases

Design-only companion to [unit 15](../../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5), researched October 18, 2026. No CLI, account, container engine or paid service is needed. Read the rolling-release subsection first. These fictional observations are exercise inputs, not AWS evidence.

For each case, write a prediction, calculation where relevant, competing explanations, next evidence to inspect and customer consequence. Separate a proposed correction from a verified outcome. Record assistance in the [learning record](../../curriculum/LEARNING-RECORD.md). Compare with [assessor notes](ASSESSOR.md) only after attempting the cases.

## 1. Percentages that leave no whole slot

A rolling replica service has three desired tasks, all old tasks healthy, minimum 75% and maximum 125%. Desired count stays fixed. The team expects a quarter of the capacity to change at a time. Calculate the integer floor and ceiling. Can the first new task start or a healthy old task stop? Compare a start-first setting with a stop-first setting and explain the cost/availability tradeoff. Do not interpret task percentages as percentages of customers.

## 2. Permission without capacity

Two healthy old tasks remain. Minimum is 100%, maximum 150%. The candidate has not started. The operator says, “The arithmetic permits three tasks, so ECS must be ignoring us.” What does the arithmetic establish? Name observations that distinguish placement/capacity, image startup and a wrong service/revision selection. Do not prescribe administrator access as a diagnostic shortcut.

## 3. One green light is insufficient

The candidate container's health check passes, but the configured target group reports unhealthy. This service uses both checks. The operator proposes stopping an old task because the new process is running. Explain which evidence is missing. Give two different investigations that could explain the target failure without assuming the image is defective.

## 4. A green release with wrong invoices

Candidate requests return HTTP 200, yet a known discount is omitted. The team's only alarm measures server errors. Separately, a proposed deployment alarm is already in ALARM before the next release begins. Explain why these are two different weaknesses. Design a bounded business probe and a pre-release alarm check; identify what still requires a real integration test.

## 5. A short drain for a long upload

A forty-second upload is in progress when its old task is retired. The team selected a five-second deregistration delay from a short-request example. A process later exits zero. Is the upload proved complete? Specify evidence for the client, stored data and shutdown sequence. Then change the requirement: uploads can last several minutes. What application behavior might need to change beyond the timeout values?

## 6. Recovery without a usable destination

A first deployment fails; there is no completed predecessor. A colleague expects rollback to create a working version. In another environment a predecessor exists, but its image was removed and new code changed stored invoice meaning. Explain why these are different missing recovery prerequisites. Identify what should be retained and tested before promotion, and what completed effects require reconciliation.

## Transfer: scale changes the calculation

Repeat case 1 after the desired count changes from three to four, with the same percentages. Then assume all four existing tasks are healthy but the workload cannot tolerate fewer than four. State which arithmetic permission conflicts with that business requirement. Your answer must name a feasible design to investigate, its extra evidence and overlap cost, not merely a different percentage.

This exercise does not simulate ECS, establish production timing or prove certification mastery. A later implementation needs scoped access, a complete estimate, owner-chosen spending and reserve limits, and cleanup evidence.
