# Who pays when a shared object is downloaded?

This is a design exercise, not an executable bucket lab. It changes no permissions or billing settings. Read [the storage lesson](../../reader/BOOK-LOCATORS.md#book-100cd25ca8175529), then write your answers before opening the [assessor notes](REQUESTER-PAYS-ASSESSOR.md).

A research group publishes a large reference dataset in an S3 general purpose bucket. The owner wants other AWS accounts to download it without paying every visitor's request and download charges. The owner is willing to pay for keeping the data stored. The dataset is not anonymous or public; each client must use an approved AWS identity.

1. Identify the S3 access option that could fit this narrow charge-allocation requirement. Say which party pays storage, request and download transfer under the stated conditions.
2. What must a requester communicate to show acceptance of the charge? What fails if the client assumes an anonymous public GET will work?
3. A requester assumes a role in another account. Which account is associated with the request charge? Explain why the identity path belongs in the cost design.
4. A website lets an approved researcher download the same object. In design A, the browser signs a direct S3 request using the researcher's AWS role. In design B, the website backend fetches the object with its own execution role and streams it to the browser. Which account does S3 identify as the requester in each design? Does Requester Pays bill the human browser visitor in design B? If the business wants customer-level chargeback, what must the application add?
5. The owner restores an archived object. Which party pays the restore request, and which party pays retrieval charges according to current AWS guidance?
6. An in-owner-account request returns AccessDenied. Can the owner assume every failed call is billed to the visitor? Explain the supplied exception and the evidence still needed to attribute actual usage.
7. Change the business requirement: any member of the public must be able to download the dataset with no AWS identity. Does the same option fit? What other access and cost design would need review?

Then ask Codex to identify a missing cost bearer and a security assumption in your design. Preserve your answer first; an AI answer is not a deployed policy or invoice.
