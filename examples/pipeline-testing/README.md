# Test the requirement at the stage that can see it

This free, local-only lab demonstrates why a pipeline uses different test layers. It creates a temporary SQLite database and starts a real HTTP server on loopback; it sends no message and creates no AWS resource. It needs Python 3 and permission to open a local loopback port.

Run the normal pipeline:

```sh
python3 examples/pipeline-testing/lab.py
```

Three gates run in order: a pure unit test for the consent rule, an integration test that combines the service with a real local SQLite outbox, and an acceptance test that sends HTTP requests and checks the customer-facing result and persisted record. Each stage uses a different boundary. If a gate fails, later stages do not run.

## Inject defects to check the checks

```sh
python3 examples/pipeline-testing/lab.py --fault consent-bypass
python3 examples/pipeline-testing/lab.py --fault wrong-message
```

These are intentional negative controls. Both commands should exit with status 1. The consent bypass passes the isolated policy unit tests, then fails integration because the actual service queues a message without consent. The wrong-message fault passes the unit and integration checks, then fails acceptance because the customer receives a generic time instead of the appointment they booked. A failed gate is the correct outcome for these commands.

The oracle is explicit: no-consent customers must have zero outbox records; a consenting customer must have exactly one record for the correct customer and appointment, with the expected message. The positive case prevents “send nothing” from passing as safe. The database uses parameterized SQL and the tests inspect stored values as well as HTTP status.

## Questions to answer

1. Which requirement is answered by the unit test? Why does that test pass when the service bypasses the rule?
2. Which actual boundary becomes visible to the integration test?
3. Why does checking only `202 Accepted` miss the wrong-message defect?
4. Which layer is cheap and fast, and which provides more confidence at greater setup/runtime cost?
5. Where would SAST, DAST, UI, load and resilience testing belong for Maya's real application? Which ones should be approved and isolated before running?
6. Which evidence is real in this lab, and which AWS evidence would still be needed for a deployed application?

Ask Codex to review the tests for a missing positive case and a false-confidence gap. Preserve its suggestions, inspect whether each test reaches the relevant code and data, and reject any cloud command. These fixtures use invented customers and appointments. The fixtures do not test AWS behavior.
