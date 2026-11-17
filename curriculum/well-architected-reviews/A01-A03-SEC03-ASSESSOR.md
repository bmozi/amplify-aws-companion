# Assessor: the 10:00 receipt is not the 10:10 role

This is authored reasoning for the [SEC 03 changed case](A01-A03-SEC03.md#changed-condition-exercise-a-green-file-and-a-wider-role), not an AWS observation or learner score.

The 10:00 receipt predates the 10:05 attachment. It cannot support a 10:10 claim that the role still has only its earlier inline grants. The attached policy's *name* is not its authority. Read its ARN and default version document, alongside the role's current trust, all inline and other attached policies, any boundary, applicable resource policies and session/organization context. Record the observation time. If any read is denied or incomplete, keep the authority conclusion pending.

For an unrelated app, first verify the actual caller and choose a harmless action/resource pair that is valid for that app, preferably a disposable fixture. Static comparison and IAM simulation can find a likely grant or omission but cannot show that the service accepted a real request. Do not attempt deletion as a denial test. A new policy may grant, deny or be inapplicable; without its contents and context, asserting either “safe” or “compromised” is unsupported. Existing workflow gate `false` stops new jobs of that workflow but does not itself revoke AWS trust or cancel a session already issued.

A strong answer keeps the five evidence layers separate: **local recipe, collected account documents, effective session authorization, actual service response, and customer-visible result**. It names the changed observation that would justify each stronger claim and does not propose widening the policy merely because one legitimate request failed. No independent learner has attempted this packet.
