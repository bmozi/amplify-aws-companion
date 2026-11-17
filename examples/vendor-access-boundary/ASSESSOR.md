# Vendor-access boundary: assessor reasoning

These answers follow the artificial rule cards in [the exercise](README.md). They are design judgments, not observed AWS decisions. The two gate model is based on AWS's [cross-account evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html), [third-party external-ID guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_third-party.html) and [session-policy rules](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html#policies_session).

| Card | Entry | Object read through Cedar role | Reason |
| --- | --- | --- | --- |
| 1 Expected customer | Yes, under the stated policy inputs | Yes, under the stated policy inputs | Caller grant and Cedar trust match; the role grant covers the exact object and no supplied limiter removes it. |
| 2 Wrong value | No | No request through this role | Trust's `sts:ExternalId` condition fails even though Beacon's caller has a grant. |
| 3 Missing caller grant | No | No request through this role | Cedar's trust alone does not authorize Beacon's cross-account caller. |
| 4 Narrowed session | Yes | No | The supplied session policy omits `s3:GetObject`; the role's grant cannot expand that session. The session policy alone also cannot grant `s3:ListBucket` if the role's identity policy omits it. |
| 5 Wrong object | Yes | No | The stipulated identity grant names only the original object and no other grant is supplied. |
| 6 Explicit deny | Yes | No | The deny concerns the later object request, not the preceding assume-role request. An applicable explicit deny defeats the otherwise matching read grant. |
| 7 Shared identifier | Unknown for an actual request | Unknown | Reuse defeats the intended customer distinction if Beacon can be induced to present Cedar's role ARN and shared ID. Actual vendor behavior, caller grant, installed trust, permissions and resource request still need observation. |
| 8 Direct resource path | Not attempted | Unknown | Direct cross-account resource access needs a caller-side identity allow and a resource-side allow under the documented cross-account path. Cedar-role trust and its external ID are outside this different request path. Other controls may still deny. |

**Assessment standard.** A useful answer names the actor and action at each gate, does not call an external ID secret, distinguishes a limiting session policy from a grant, and marks cards 7–8 as incomplete evidence. It names a safe allowed and denied fixture with matching action/resource types, includes cost and cleanup ownership, and does not propose a destructive denial test. A verbal correct answer does not prove effective installed policy, customer isolation or independent learner transfer.
