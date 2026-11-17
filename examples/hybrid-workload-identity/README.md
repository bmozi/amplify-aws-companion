# The warehouse scanner needs AWS access

Maya's repair company keeps a scanner service in its own warehouse. Each night it uploads a small inventory report to a specific S3 location. The service is software, not a person signing in. Its operator proposes storing an IAM access key on the scanner because it is outside AWS. Your job is to design a way for that outside workload to receive *temporary* AWS credentials while keeping the report destination narrow.

This is a paper lab for [SAP-C03 skill 2.1.5](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain2.html). Use the [identity lesson](../../reader/BOOK-LOCATORS.md#book-47726780fac09ca7) and [hybrid path lesson](../../reader/BOOK-LOCATORS.md#book-0b54b52a3c811230). Do not create a certificate authority, trust anchor, role, key, bucket or bill for this exercise.

## Draw the path

```text
warehouse scanner -> X.509 certificate + private-key proof -> IAM Roles Anywhere
        -> trusted CA anchor + profile + role trust -> temporary role credentials
        -> S3 request -> bucket/key policy and encryption checks -> report object
```

The certificate is the scanner's badge. The private key proves it holds that badge. A trust anchor says which certificate authority may issue acceptable badges. A Roles Anywhere profile chooses permitted roles and can narrow the session. The IAM role and resource policies decide what an issued session may do. The scanner still needs a network route to the service endpoint; credentials are not a route.

AWS documents the [non-AWS workload pattern](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_non-aws.html), [trust model](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/trust-model.html), [authentication requirements](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/authentication.html), and [credential helper](https://docs.aws.amazon.com/rolesanywhere/latest/userguide/credential-helper.html). Read the current pages before a real implementation. Their details, Region support, and pricing may change.

## Make six decisions before reading the assessor

For each case, state **the actor, intended action, trust check, permission check, one allowed test, one denied test, failure response, and remaining evidence**.

1. **First upload.** One named scanner may write reports only under `warehouse-a/daily/`. Explain what the CA, trust anchor, profile, role trust, role permission and S3 policy each contribute. What should a write to `warehouse-b/` do? Do not turn the example prefix into a production policy without checking the exact request and resource ARNs.
2. **A broad CA.** The same CA issues certificates to printers and scanners. A teammate proposes a role trust policy that accepts every certificate from that CA. How would you narrow which certificate identities may use this role? Who controls certificate subject fields, issuance and revocation?
3. **Stolen scanner.** A valid certificate and its private key are copied. Explain what rotating the machine's application password would and would not fix. Identify a credential issuance stop, a certificate revocation or replacement path, and what to do about already-issued temporary sessions. Do not promise instant invalidation without testing the actual mechanism.
4. **Broken network.** The warehouse cannot reach the Roles Anywhere endpoint. The operator offers a permanent access key as a fallback. Choose a safer degraded behavior and say how the report is queued, protected, retried and deduplicated. State the business cost of delayed inventory.
5. **New cloud.** The scanner moves to another cloud provider that offers its own workload identity. Compare a certificate-based Roles Anywhere bridge with a supported federation route. Do not assume the new provider's identity token is trusted by AWS merely because it exists. What issuer, audience, subject, exchange and role conditions would need proof?
6. **New Region and data owner.** Reports must go to a different Region and an account owned by the compliance team. Redraw the trust, network, S3 and KMS checks. Identify where data-location restrictions, cross-account grants, audit events and transfer charges require review.

## Use Codex as a design critic

Answer first. Give Codex only the fictional case and your proposed path. Ask it to trace every grant from certificate issuance through the final S3 write, invent one near-miss identity and one neighboring-object denial, and cite current AWS documentation for claims about Roles Anywhere. Verify its citations and revise your answer. Never paste a real certificate, private key, credential or account policy into the exercise.

## Evidence to retain

Keep one diagram with the six named boundaries, your original and revised decisions, a permitted and denied request specification, an incident/rotation procedure, a cost estimate for a *future* chosen setup, and a list of observations a real pilot would need. A correct paper answer is design evidence. It is not proof that AWS issued credentials or denied a request. Compare your work with the [assessor notes](ASSESSOR.md).
