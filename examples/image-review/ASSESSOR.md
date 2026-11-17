# Image-review assessor reasoning

These criteria evaluate the fictional [staged exercise](README.md). They are internal editorial guidance, not an independently validated security policy or learner result.

## Stage 1

Source changes and unit tests do not establish the contents, scan state or full behavior of B. Request evidence bound to B: final-image package inventory, a completed scan with appropriate scope and current support, and the relevant application tests. The old report belongs to A even if the tag now means something else. Keep exploitation reachability unknown until investigated. A reasonable decision is to withhold release approval pending the specified evidence, without asserting that B is definitely vulnerable.

## Stage 2

The supplied inventory and report support a bounded conclusion about F-101 in B. They do not prove the absence of every defect or authorize the whole rollout. Investigate F-202's affected conditions and mitigation options; absence of a listed fix does not mean absence of risk. Do not automatically accept or reject it from severity alone when the business policy and exposure facts are missing.

Customer isolation remains an unperformed acceptance check for B. The observed serving set still includes A, so the replacement is incomplete for that scope. Inspect why it remains before choosing a bounded replacement or rollback action; do not erase a task blindly while ignoring in-flight work. A rollback target with unknown schema compatibility is not verified recovery evidence.

An exception must name the affected digest and operation, known/unknown consequence, temporary mitigation, owner and expiry or review trigger. It must not assert that an untested mitigation works. Record separately the decision, implementation and observed result. Existing evidence cannot support “all running images remediated.”

## Stage 3

Unknown scanner support invalidates the inference that zero findings means lower risk. Prefer investigating a maintained, compatible base with demonstrated coverage over optimizing a dashboard count. The correct comparison includes package provenance, scanner scope, application acceptance and denied-access checks. A new input format can change code paths and dependencies, so old exposure and compatibility conclusions need review.

A strong answer links each decision to the exact evidence available at that stage and names the observation that would change it. Do not reward confident exploit claims, invented scan results or a fixed severity rule absent from the scenario. Actual advisory interpretation, image scanning and deployment remain separate work.
