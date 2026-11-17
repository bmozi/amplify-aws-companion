# Requester Pays: reasoning to look for

These notes were checked against AWS's current [Requester Pays documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html) on October 19, 2026. They are authored criteria, not a live account test or calibrated learner rubric.

1. Requester Pays may fit the narrow goal. The bucket owner continues to pay storage. For supported successful requests, the requester pays the request and data download. The feature does not move every bucket charge.
2. Anonymous requests are not supported. A requester needs an authenticated request and must explicitly accept the charge using the supported request-payer header or parameter. A missed client setting can cause access failure; do not fix it by opening the bucket anonymously.
3. When the requester uses an assumed role, the role's account is charged for the request. A tag or billing dashboard does not itself decide which identity pays at request time.
4. In design A, S3 receives a request signed as the researcher's role, so the role's account is the AWS requester. In design B, S3 receives a request signed as the application's execution role; the application's account is charged, even though the human visitor receives the bytes. Requester Pays is not end-user billing. Customer-level chargeback requires a separate application billing/authorization contract or a direct customer AWS identity path.
5. For `RestoreObject`, AWS says Requester Pays is supported when the request-payer value is supplied, but the requester pays only the request charge; the bucket owner pays retrieval charges. Do not extrapolate the usual download rule to restoration.
6. AWS documents an exception: an AccessDenied request initiated inside the bucket owner's individual account or organization is charged to the owner. Attribute actual cost with the observed request path, caller, error and billing scope; a general rule is not proof about a particular request.
7. A public anonymous audience is incompatible with Requester Pays. Revisit authentication, who may read, how visitors are informed of any charge, transfer and storage bills, misuse exposure and the business promise. Do not announce that downloads are free because the bucket owner shifted some costs.

The decision is narrow: Requester Pays changes responsibility for supported requests and downloads. It does not grant read permission, establish customer eligibility, make storage free, or ensure every related operation is charged to the requester. No policy configuration or cost allocation was performed in this exercise.
