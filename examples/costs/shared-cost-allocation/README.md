# One bill, more than one owner

Maya's repair company and its sales team share a network path and an AI assistant. The AWS bill charges the account; it does not know the company's internal agreement about who should pay for each shared use. **Showback** explains an allocation to teams. **Chargeback** uses an approved rule to transfer or recover the amount internally. Either way, the calculation must add back to the chosen bill measure, and a disputed assignment must be reviewable.

This illustrated, entirely fictional lab supports [SAP-C03 skill 3.3.4](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-03/solutions-architect-professional-03-domain3.html). It builds on the [cost and context lesson](../../../reader/BOOK-LOCATORS.md#book-97215f8e0e3f150d), [multi-account billing exercise](../MULTI-ACCOUNT-BILLING.md), and [cost audit](../optimization-audit/README.md). The CSVs are **normalized teaching rows**, not an AWS CUR 2.0 export, actual account bill, price quote or organization configuration.

![A fictional pre-credit bill separates direct Repair and Sales charges, shared Network and AI pools, and an Unallocated row. Driver weights divide shared pools into owner totals that reconcile to the original bill; a dispute changes one driver without changing billed cost.](figure.svg)

## Decide the measure and the rule

The fixture uses one closed fictional period, a **pre-credit positive-cost measure**, integer cents, and five line IDs. Direct charges retain their known owner. Shared Network uses a declared `3:1` activity ratio; shared AI uses `1200:800` **cost-weight points**, not bare token counts. Those points stand for a separately reviewed estimate that accounts for model, input/output mix, modalities and rate. A raw token total alone can misallocate dollars when prices differ. A `1000`-cent unknown line stays **Unallocated**; the program refuses to make it disappear by guessing an owner.

For actual Bedrock `InvokeModel` or `Converse` usage, [application inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/cost-mgmt-application-inference-profiles.html) can attach activated cost-allocation tags to aggregated billed usage by application/team. AWS says their finest billing grain is per usage type per day, not per request. If per-prompt attribution is needed, [model invocation logs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) can supply token counts and optional request metadata for supported calls, but logging has privacy, completeness and storage-cost choices; it is disabled by default and does not cover every endpoint. An internal per-request estimate must be reconciled to billed dollars. For shared network, choose a driver tied to the actual direction, route, bytes, hourly components and beneficiary; the simple `3:1` ratio is a hypothesis, not proof.

AWS **Cost Categories** can group charges, and split-charge rules can show an allocation of shared category values by fixed, even or proportional methods. AWS explicitly says those split results appear on the Cost Categories details page and **do not change CUR or Cost Explorer costs**. Do not confuse that view with **CUR 2.0 split cost allocation data**, a separate export option for supported shared-resource allocation that adds rows/columns and can enlarge the export. Decide which feature fits the question before writing queries. [Cost Categories split charges](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/splitcharge-cost-categories.html), [CUR 2.0 configuration](https://docs.aws.amazon.com/cur/latest/userguide/table-dictionary-cur2.html).

## Reproduce the allocation

From the repository root:

```sh
python3 examples/costs/shared-cost-allocation/allocation.py
python3 examples/costs/shared-cost-allocation/allocation.py --dispute
python3 -m unittest discover -s examples/costs/shared-cost-allocation -p 'test_*.py'
```

The baseline script prints a **fictional 16,000-cent bill**, allocating 9,450 cents to Repair, 5,550 to Sales and 1,000 to Unallocated. A colleague then disputes one of Repair's three network driver units: an inventory shows it belonged to the Platform team. `--dispute` changes only that declared driver. The script prints 8,700 Repair, 5,550 Sales, 750 Platform and 1,000 Unallocated; the same 16,000 cents still reconcile. The change is an accounting decision pending evidence and owner acceptance, not a change to AWS billing. The code uses integer arithmetic and a deterministic largest-remainder rule so odd cents are neither lost nor invented.

Before opening the [assessor](ASSESSOR.md), answer:

1. What **billing period, cost measure, line-item types and currency** must match before you compare owner totals with a real bill? Where would credits, refunds, taxes or discounts sit if the business chooses a different measure?
2. What observations justify the network `3:1` ratio? Does a byte count alone prove who benefited if directions and transfer rates differ? How would you isolate a common fixed-hour charge?
3. What evidence turns the AI `1200:800` weights from an assumption into a defensible allocation? How do model choice, input/output tokens, retries, cached tokens and logging coverage affect it?
4. Who can approve the revised Platform driver, what original receipt should remain, and how do you explain the 750-cent movement without pretending the AWS bill changed?
5. Why should the unknown 1,000 cents remain visible? What investigation and deadline would let you assign it later, and what happens if the billing period closes before ownership is proven?

Ask Codex to attack the ledger with a duplicated line ID, missing shared-pool driver, zero units, an extra credit row and a claim that a Cost Category split altered CUR. Require it to reconcile every proposed view to the same-scope source total and cite current AWS documentation for service behavior. The local tests check arithmetic and input rejection; they cannot verify real usage, a finance-approved rule, live export coverage or bill agreement.

This lesson uses no AWS account or credits. A real export, Athena query, Cost Category, profile or logging configuration must be priced and reviewed for storage, query and retention cost, access, and sensitive prompt data. For any live experiment, choose a bounded whole-run limit and reserve for your own account, name a cleanup owner, and reconcile usage afterward. Organization chargeback remains a design exercise here.
