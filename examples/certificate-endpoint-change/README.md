# A new certificate in inventory is not a new certificate at every door

Maya has two storefront entrances in different locations. Her worksheet says both received a replacement certificate. A customer connects to each entrance: one presents the new certificate; the other still presents the old one. The worksheet and the customer observation answer different questions.

Predict the three results before running this local exercise:

1. Two listeners begin with the same disposable certificate. After changing only the west listener, what should a validated client see at west and east?
2. A fictional inventory marks both locations “replaced.” Does that statement prove the east listener now presents the replacement?
3. What happens when the client trusts the issuing practice CA but asks for `wrong.example` instead of the certificate's `localhost` name?

From the repository root, run:

```sh
python3 examples/certificate-endpoint-change/lab.py
```

The script uses Python's standard library and local OpenSSL to create a disposable CA and two different server certificates. It starts two HTTPS listeners on loopback ports, uses a client that validates the CA and hostname, changes one listener's TLS context, and reads the certificate actually presented on each connection. It then expects the wrong-name handshake to fail. The output reports comparisons, not private keys. All listeners and temporary files are removed afterward. No AWS account, ACM certificate, domain, external service or paid resource is involved.

## Change the decision

The disposable CA and server certificates declare their constraints, key usage and key identifiers explicitly so the exercise also works with Python 3.13's stricter certificate validation. Client verification stays enabled. These are local practice certificates, not an issuance procedure for production. See [OpenSSL certificate extensions](https://docs.openssl.org/3.0/man5/x509v3_config/).

Imagine the old certificate expires tonight. The inventory says both locations were renewed, but the local observation still finds the old one at east. Which location needs action, who owns the association or deployment path, and what client-side result would prove repair? Now suppose the new certificate is valid but the client uses a different hostname. Should the operator disable name validation to make the probe green? Explain the safer correction.

In AWS Certificate Manager, [managed renewal eligibility](https://docs.aws.amazon.com/acm/latest/userguide/managed-renewal.html) depends on the certificate and its use. Imported certificates are not eligible for ACM managed renewal; [reimporting](https://docs.aws.amazon.com/acm/latest/userguide/import-reimport.html) one can preserve its ARN and associations. ACM certificates are regional resources, so certificates for one domain in multiple Regions need independent renewal. AWS also documents a possible delay between renewal and [deployment to the using resource](https://docs.aws.amazon.com/acm/latest/userguide/troubleshooting-renewal.html). The local listeners model only the evidence question: **what did this connection actually receive?** They do not emulate ACM, integrated-service propagation, DNS routing, customer authentication, trust stores across a fleet, or expiry timing.

Ask Codex to list the inventory observation, the endpoint observation and the customer result separately. Have it propose a probe for every deployed entry path and a stop condition if a path still presents the old certificate. Check the probe's hostname and trust configuration yourself; a successful connection with verification disabled is not proof of a safe replacement.

Compare your prediction and changed-case answer with the separate [assessor notes](ASSESSOR.md) only after writing them down.
