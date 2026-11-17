# Stage one reasoning: a page loads and a lookup is denied

Use this after writing your own answer to the [first stage checkpoint](LEARNING-ROUTES.md#after-chapters-15-trace-the-promise). The facts are fictional. They describe a page load and a separate 403 response; they do not show the upload result, a named AWS service, or any logs.

## Separate what happened from what you suspect

The page load shows that the browser obtained enough page content to display something. It does not show that the status API, an upload destination, or the application backend worked: the page could have been served from a cache or a different route. A 403 shows that a responder returned a refusal to the status request. It does not, on its own, identify that responder or explain the denial. The upload was attempted; the case gives no receipt, stored-object check or other result proving it succeeded.

An edge filter, an API gateway, a proxy or application code could be candidates in an architecture that contains them. They are hypotheses, not facts supplied by the case. Correlate a sanitized request identifier and time with the actual configured request path and its available access, security and application records. Check that the compared records cover the right request and time; missing logs do not prove a layer was bypassed. Verify how the relevant service reports a denial before interpreting an entry. Do not paste credentials, private photo contents or another customer's data into a report or an AI prompt.

If the request reaches the component making the access decision, ask who the caller is, which action and record were requested, and which rule applies to that caller and record. A correctly authenticated person can still lack permission. Conversely, do not call a 403 proof of a correct owner rule until the intended owner's allowed read and a different user's denied read have been checked in the authorized environment. A 403 alone does not identify the cause or show the rule works for all users.

## Change one fact

Suppose a correlated application record shows the status handler received this exact request and returned 403 after evaluating the caller's access. What can you now conclude? What is still unknown?

You can attribute this response to the application handler for that request, assuming the correlation and record are trustworthy. The new fact does not establish that the caller's identity was genuine, that the access rule was correct, that the upload succeeded, or that other requests cannot be denied earlier in the path. Next compare the sanitized identity and requested record against the intended policy and test an allowed owner and a forbidden nonowner. If the correlation is uncertain, keep attribution uncertain too.

## Cost and stopping decision

An estimate needs a selected design, Region, quantities, duration and current applicable rates. For each proposed resource, record when it starts and stops, possible request, storage and transfer use, and anything that may remain after the main app stops. Add a contingency and compare the whole estimate with limits chosen for the account. If the necessary prices or quantities are missing, write **estimate incomplete**, not zero. A budget alert can be useful but is not an instantaneous spending cap.

Before an authorized run, identify the account, scoped identity, operator and cleanup owner. State a stop condition and how to check that resources were removed; reconcile later usage separately because billing observations may arrive after cleanup. This is a planning exercise. It creates no AWS resource, checks no account balance and proves no cloud outcome.

## Try explaining it back

Without looking above, explain to a new teammate why “the page loaded” and “the upload succeeded” are different claims. Then ask Codex to challenge one assumption in your answer without supplying the solution. Record your original answer and the assistance separately. This authored guide has not been calibrated against independent learner attempts.
