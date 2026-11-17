# Plan a cryptographic change from evidence

Read [the data-protection lesson](../../reader/BOOK-LOCATORS.md#book-d7e2126250da33c2). This is a design-only exercise. All organizations, lifetimes and observations below are invented. No credentials, AWS account or paid tool is needed.

## Your first decision

Maya's fictional engineering customer wants drawings kept confidential for fifteen years. Its worker calls KMS directly. The SDK and HTTP-client versions are unknown. An operator reports “HTTPS works.” An office proxy sits on a separate administrative path. A recovery utility has not been run for a year. A customer also verifies signed downloadable software using an old device.

Create an inventory with one row per distinct protection and participant pair. Mark facts, assumptions and unknowns separately. Include the device's signature verification separately from the worker's transport. Identify the first information you would collect, who could provide it, and why it affects the decision. Do not convert the fictional fifteen-year requirement into a legal rule.

## New evidence arrives

For the worker's selected direct KMS request, a fictional matched CloudTrail event records `tlsDetails.keyExchange = X25519MLKEM768`. The application result is correct. The office path fails before receiving an application response. Another event for a service calling KMS on the application's behalf has no `tlsDetails`. Nothing has been measured for the recovery utility or old device.

Write a five-sentence status report: what is supported by the worker evidence; what remains unknown; what the missing field cannot prove; what you will investigate about the failed path; and why the device needs a separate decision. Do not invent a cause for the failure.

## The proposed shortcut

A teammate suggests disabling certificate verification to make the office test pass. Another suggests calling the entire application “post-quantum protected” because the worker call succeeded. A third wants to rotate the storage key and declare all migration work finished.

Respond to each proposal with the property it changes, the claim it fails to establish and a better next observation. Then draft a bounded test plan: selected participants, configuration/version evidence, allowed and denied application behavior, negotiation evidence, error/latency observations, recovery compatibility, stop conditions and exception owner. Do not select arbitrary universal latency or risk thresholds; name who must agree them and what baseline is needed.

## Changed case: three jobs, one misleading status light

Maya's team reports a successful direct KMS call whose matched event shows hybrid TLS. At the same meeting, a supplier asks to establish a shared secret for exchanging drawings, and a customer asks whether an old tablet can verify a newly signed software download. A teammate says, “The green KMS result proves all three are post-quantum ready.”

Before reading the assessor, make a three-row decision sheet: **trip to KMS**, **partner secret**, **download signature**. For each row, name the two participants, the relevant mechanism, one passing and one failing observation, and the missing compatibility or authorization fact. Use the [three-job figure](../../book/figures/three-post-quantum-boundaries.svg) as a route through the choices. Explain why a hybrid TLS result does not show that the supplier used an ML-KEM KMS key or that the tablet accepts an ML-DSA signature.

Now change one fact: the supplier sends an encapsulated blob and reports that its `Encapsulate` call succeeded, but Maya has no authenticated message exchange or agreed key identity. Does that close the partner row? State the next observation and the stop condition. Keep this a design exercise: do not create a KMS key, run a paid API, copy a real key or assume the book's fictional partner can act in the reader's AWS account. AWS's [Encapsulate API](https://docs.aws.amazon.com/cli/latest/reference/kms/encapsulate.html), [hybrid TLS guide](https://docs.aws.amazon.com/kms/latest/developerguide/pqtls.html) and [ML-DSA key guide](https://docs.aws.amazon.com/kms/latest/developerguide/mldsa.html) describe different operations.

## Use AI after your own answer

Ask Codex to identify unsupported claims in your inventory and status report, using only the supplied observations and linked official sources. Require it to leave unknowns unresolved when evidence is missing. Compare with the [assessor notes](ASSESSOR.md), then revise one conclusion and explain why. This is authored practice, not an independent assessment of your competence.
