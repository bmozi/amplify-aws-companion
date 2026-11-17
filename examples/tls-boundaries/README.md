# A trusted connection is not permission to read every invoice

Maya wants two promises: customers reach the intended server through an encrypted connection, and each customer receives only the right invoice. This exercise makes those promises visibly separate.

```text
Connect to loopback → verify certificate trust and server name → send HTTP request
                                  │                                  │
                       failure stops before HTTP          application permits or denies
```

Run from the repository root:

```sh
python3 examples/tls-boundaries/lab.py
```

Requirements: Python with its `ssl` module, plus an OpenSSL command-line executable supporting `req -addext`. The initial check used OpenSSL CLI 3.6.4. The Python-linked TLS library can differ from the CLI; the result records it. Nothing is installed automatically. Missing prerequisites or unexpected verification codes fail rather than silently skipping a case. Run without `-O` so the scenario assertions execute.

## Predict the four results

| Client setup | Expected result | What it establishes |
| --- | --- | --- |
| Trust the temporary certificate; verify `localhost`; request as fictional Alice | TLS handshake succeeds; HTTP 200 contains the fixture invoice | This client's trust/name checks and this application branch succeeded |
| Trust no certificate authorities; verify `localhost` | Certificate verification fails before HTTP | An unknown self-signed issuer is rejected |
| Trust the temporary certificate; verify `wrong.example` | Hostname verification fails before HTTP | Trusting an issuer does not make every name acceptable |
| Trust the certificate; verify `localhost`; request as fictional Bob | TLS succeeds; application returns HTTP 403 without the invoice | Transport protection and application authorization are different checks |

The two failures are actual TLS handshakes, not prewritten error messages. The program verifies OpenSSL's expected codes (18 for this self-signed issuer; 62 for this hostname mismatch) and confirms that neither failure reached the HTTP handler. It also checks the full allowed fixture response and absence of the invoice from the denied response. The first run negotiated TLS 1.3; the program reports the actual negotiated version rather than promising the same result on every machine.

## Where the trust comes from

The lab creates a fresh, one-day self-signed certificate containing `localhost` in its Subject Alternative Name. It uses that certificate as this client's explicit local trust anchor. This is a deliberately simplified, single-certificate teaching arrangement; it does not reproduce a public certificate authority chain or an ACM certificate.

The private key and certificate live inside a temporary directory. The key is restricted to owner access; both files and the directory are removed when the exercise ends, including ordinary assertion failures. This is file cleanup, not a claim of forensic erasure. Nothing is added to the operating system or browser trust store. No certificate or key is uploaded or checked into Git.

The server listens only on IPv4 loopback. Every client connects directly to `127.0.0.1`; `server_hostname` supplies the name to verify and does not cause a DNS lookup. Even `wrong.example` never receives a network connection. Both server and client require at least TLS 1.2, and certificate/name verification remains enabled in every case. Accepted sockets have a bounded timeout; the server is closed and its serving thread joined afterward.

Python's [TLS client context documentation](https://docs.python.org/3/library/ssl.html#ssl.PROTOCOL_TLS_CLIENT) explains the verification settings. The [OpenSSL request command reference](https://docs.openssl.org/3.6/man1/openssl-req/) documents the certificate-generation options. These APIs are mechanisms; the four observed outcomes are the execution evidence for this fixture.

## Do not mistake the actor fixture for login

`X-Fixture-Actor` is a public string that the client chooses. Any local caller can send `alice`. It exists only to make the application's allow/deny branch visible after TLS completes. There is no real authentication, token validation, tenancy system or mutual TLS. Do not adapt this header as a production identity mechanism.

The certificate proves server identity only relative to this client's chosen trust and expected name. It does not validate the human customer's identity or decide invoice ownership. A production application needs an authenticated identity and authorization tied to the real record. The separate tenant-isolation and Amplify lessons address those responsibilities with their own evidence limits.

## Change the situation

Before modifying code, explain the expected outcome:

1. The certificate is trusted, but the application returns the wrong customer's data. Which layer needs correction, and why would replacing the certificate not fix the bug?
2. An operator changes a URL to an IP address that is not in the certificate. Explain the verification problem without disabling name checks.
3. A load balancer terminates TLS and forwards a request to another service. Draw the next connection and specify its own protection and identity requirements.
4. A certificate renews successfully in an inventory system, but an endpoint still presents the old certificate. Identify the observation needed at the endpoint.

Ask Codex to explain each recorded result and propose a test that would detect skipped hostname checking. Require an executed failure under a deliberate temporary defect before trusting the test's sensitivity. Never ask it to resolve this exercise by turning verification off.

## Evidence boundary

This is actual local TLS, HTTP and synthetic authorization behavior. It does not demonstrate DNS validation, public CA issuance, expiry handling, revocation checks, certificate renewal, mutual TLS, browser behavior, load-balancer configuration or AWS ACM. It does not establish production cipher hardening or independent learner success. Those remain separate implementation and assessment work.

Return to [data protection throughout its life](../../reader/BOOK-LOCATORS.md#book-4f6cf1453aa8c153) and explain why “the connection is encrypted” is a narrower claim than “the customer's data is protected throughout the system.”
