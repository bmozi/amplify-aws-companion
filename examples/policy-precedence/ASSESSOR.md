# Assessor reasoning: which policy governs?

Read after the first attempt. This key describes invented business rules.

1. **September 30:** The October 1 bulletin is not applicable yet. The approved general household rule gives 45 days when a receipt is present. The score did not choose it; the acceptance date did.
2. **October 2:** Both household rules apply, but the approved bulletin has higher priority and gives 60 days with a receipt. Search ranks the general source at 0.99 and bulletin at 0.31 in this invented packet. Treating 0.99 as legal or business authority would be a category error.
3. **No receipt:** The selected rule requires one, so the fixture abstains from a coverage answer. The application would need the actual receipt fact and any real policy exceptions; it should not invent them.
4. **Commercial equipment:** The separate approved exclusion applies. A 45- or 60-day household answer would ignore the repair type.
5. **Missing or revoked bulletin:** The general rule must not silently replace a potentially governing bulletin. The fixture requires every applicable approved source and a current grant before deciding. That is conservative; a real catalog needs a maintained completeness and access policy, not just a fortunate search result.
6. **Changed bulletin:** A changed source version or digest stops the old rule mapping. Updating the digest mechanically would still not validate the meaning: a human policy owner must review any changed date, condition or duration before approving a new mapping.
7. **Equal top priorities:** Two conflicting rules with equal priority cause abstention. The fixture cannot decide which author had authority or whether a newer notice superseded the other. Resolve that in a governed catalog and test the changed case again.

The program checks declared metadata and byte identity. It cannot interpret natural language, authenticate Alice, know whether a real policy was approved, guarantee an index returned all needed documents, or measure a model's answer. A returned `answer` is a **local fixture result**, not a customer commitment. For a cloud design, keep search/discovery, current document access, business rule approval, generated explanation and any consequential tool action as separately testable boundaries. [AWS Knowledge Bases retrieval documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html) describes the retrieved result/score boundary.
