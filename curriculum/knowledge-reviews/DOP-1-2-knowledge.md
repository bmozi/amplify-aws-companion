# Individual knowledge review for DOP-C02 task 1.2

Internal editorial review, October 19, 2026. The two official knowledge entries for test types and test placement now have separate partial teaching and assessment mappings. The implementation skills in this task are outside this review. [Official task source](https://docs.aws.amazon.com/aws-certification/latest/devops-engineer-professional-02/devops-engineer-professional-02-domain1.html).

Task 1.2 asks for knowledge of different test types (including unit, integration, acceptance, UI and security scans) and reasonable use of test types at different pipeline stages. The retained Domain 1 digest is `04b66f2cbe775bf3d16eb987eb145863dd7d124675ca812597e3a24de457513d`. Inventory bullet digests are `5aa0f71b8ea10e5bed4d325775dd6fe403a1b1dec4d7c2713d8eed9998f06f4a` and `a187b8b028c48a7ae23fca7f53f129f9281f2d65d251697d329e33b62e775339`.

## Test types

Unit 03 distinguishes unit, integration, acceptance/functional, UI, SAST, DAST, performance/load, resilience and synthetic/post-release tests using ordinary language and names what each cannot establish. It says the list is a menu, not a requirement to run every test on every change. The official AWS exam guide supports the task-level type examples; AWS Prescriptive Guidance adds the broader test categories and cautions about differing roles.

The new [pipeline-testing local lab](../../examples/pipeline-testing/README.md) executes unit, integration and acceptance checks against a real local service, SQLite store and HTTP endpoint. Two injected defects exercise gaps between layers. Normal execution passes all three gates. The consent-bypass defect passes unit checks then fails integration. The wrong-message defect passes unit and integration then fails acceptance. A negative-control failure must be recognized as the intended result, not a failed lab run.

## Test placement

Unit 03 maps quick, deterministic checks to early feedback, integration/acceptance to an isolated test environment, promotion approval to the release boundary and synthetic checks to operation. It connects test choice to the requirement, oracle, runtime/cost, environment fidelity, isolation, identity, cleanup and stop conditions. The [assessor notes](../../examples/pipeline-testing/ASSESSOR.md) check these tradeoffs and require test evidence to stay within its real scope.

## Remaining evidence

Mappings remain partial. The lab runs only local code with a temporary SQLite file and loopback HTTP server. It does not execute a browser/UI test, SAST or DAST analyzer, AWS service integration, load/performance test, resilience experiment or production pipeline. The two task skills (triggering tests on pull requests/merges and testing at scale) are not claimed as covered. Independent technical review, learner assessment, selected cloud implementation, failure/timeout/cleanup behavior and measured costs remain open.
