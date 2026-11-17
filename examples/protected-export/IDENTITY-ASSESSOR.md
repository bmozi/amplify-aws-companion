# A15 identity-boundary changed cases and assessor

Answer without running the lab, then run it and compare. Use only fictional records.

1. Supplier P sends `POST /approve` with its own local session and `"actor": "Maya"` in the JSON. Does the label grant approval? Name the authority the server actually checks.
2. Maya approves `weekly-parts`, `v1` for Supplier P. Supplier Q presents a valid Supplier Q session and asks for those bytes. Is the session valid enough? Which separate question decides the result?
3. Supplier P reads `v1` and saves the bytes. Maya withdraws the owner grant. Which new request must fail, and which earlier copy can still exist? What evidence would be needed to claim the supplier deleted every copy?
4. A new `v2` uses the same key but different bytes. Supplier P has a valid session and the old `v1` approval. Can it read `v2`? Which binding is missing?
5. The local HTTP response contains bytes and a matching digest. What does that prove locally? Name two security facts it does **not** prove for an AWS cross-account transfer.
6. Codex proposes a bucket policy granting unversioned `s3:GetObject` to every principal in Supplier P's account because the local HTTP test passed. Why is that especially wrong for an exact-version export, and what review and negative tests would you demand before any bounded live run?

## Assessor reasoning

1. No. The server maps a temporary bearer value to the owner or supplier role; a body field cannot change that map. The supplier gets HTTP 403. An owner request containing an `actor` field also gets HTTP 400 so the API has one source of identity.
2. A valid session establishes *who* is asking, not *which export* that supplier may receive. The approved exact recipient is Supplier P, so Supplier Q gets HTTP 403.
3. A fresh owner read and therefore a fresh HTTP delivery fails after withdrawal. The already stored supplier copy remains. A deletion claim needs a supplier-side obligation, inventory/retention scope, an authenticated acknowledgement and evidence covering backups and derivative copies; the local fixture has none of that.
4. No. The approval binds key **and version**, plus digest and recipient. The replacement version needs its own approval even when the key string is unchanged.
5. It proves the bytes received by this local client match the digest in that response and the shelf retains the same bytes. It does not prove TLS peer identity, authenticated AWS principal, effective IAM/bucket/key policy, S3 version behavior or absence of another copy.
6. Reject the broad grant as unreviewed. A named S3 version read uses `s3:GetObjectVersion`; an unversioned `s3:GetObject` grant could permit a later current object without the version approval. Name the exact supplier principal, bucket/object/version and KMS key; inspect identity, resource and key policies plus any boundary, endpoint or access-point policy. Test the intended synthetic version positively and an adjacent object, unapproved version and different supplier negatively, then inspect audit results. Price the complete run and cleanup against spending and reserve limits chosen for the account. The local HTTP test cannot authorize a live policy. [AWS GetObject API](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html).

**Assessment limit:** These authored answers are not independent learner attempts, an AWS IAM simulation or proof of safe deployed access. Ask Codex to critique one answer only after you write your own; require it to cite current AWS primary documentation for any service-specific claim.
