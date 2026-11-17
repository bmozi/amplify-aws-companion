# Practice with a stand-in API

Maya's team is building a booking page, but the scheduling service is not ready. The frontend team still needs to learn what to display when an appointment is available or a request fails. A stand-in can return prepared responses while both teams agree on the contract. It cannot prove that a real booking was saved.

For an **API Gateway REST API**, a mock integration can return responses from API Gateway without contacting an integration backend. The method's integration request and integration response determine the configured behavior; the method response describes the response exposed by the method. A deployed method also needs its changes available in the intended stage. This is a paper design exercise: no API is deployed or invoked. Read the [AWS mock integration guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-mock-integration.html) and [console configuration guide](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-mock-integration-console.html) for the current details.

## Predict before checking

1. **Happy picture.** The stand-in returns a prepared `200` body saying a fictional appointment is available. The browser renders it. Which frontend claim is supported, and what remains unknown about saving a booking?
2. **Selector and response.** A request mapping produces `{ "statusCode": 200 }`. A teammate assumes that this object alone is the complete customer response. Identify the other configured response and the stage that must be checked. How would you distinguish a response-selection issue from an incorrect response body?
3. **Failure path.** The team only configures and tests a success. A dependency outage later needs an error screen. Specify a controlled failure response, what the client must display and a negative assertion that catches a false success message. Do not infer the exact status selection or template behavior without checking the configured REST API.
4. **Wrong door.** A teammate calls the mock URL from a browser and receives a cross-origin error. What evidence would distinguish browser CORS response/header configuration from a healthy backend? What must still be verified after changing a method or integration response?
5. **Changed contract.** The live scheduler later changes `appointmentId` from a string to a number, but the mock still returns a string. What agreement and checks keep the stand-in from hiding the mismatch? What evidence is needed from an integration test against the real scheduler?

Write the request, expected HTTP status, headers and body, the customer-visible behavior, and what counts as a false positive for each case. Then compare [assessor notes](ASSESSOR.md). The scope is REST API mock integrations; do not assume that a different API Gateway product exposes identical controls.

## Run the local contract check

After predicting case 5, run this Python-only fixture from the repository root:

```sh
python3 examples/api-gateway-mock-review/lab.py
python3 -m unittest discover -s examples/api-gateway-mock-review -p 'test_*.py'
```

The prepared response passes. A second **fictional** response changes `appointmentId` to a number and is rejected; a 503 is reported as a service error, distinct from a valid response saying no appointment is available. This runs local parsing and assertions, not an API Gateway mock, a browser, a deployed provider or a booking. It only catches changes the written contract checks. An actual provider contract test still needs the selected service, authorization, input and result evidence.

## Ask Codex to challenge the test

Provide only the fictional contract and ask: “What client defect could pass this mock test but fail against the real service? Give a negative test and identify the evidence it can and cannot provide.” Review proposed mapping templates, status selection and CORS claims against the AWS guide and the actual selected API configuration. Never paste an actual signed URL, credential, customer record or private endpoint into the prompt.

If you later choose a cloud exercise, first agree on the scoped account and identity, Region, whole-run estimate, spending limit and reserve, stop conditions, and who verifies cleanup. Include requests, logs and any other selected services in the estimate. The paper exercise and local fixture create no AWS resources and use no AWS credits.
