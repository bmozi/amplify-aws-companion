# When cheap storage produces an expensive bill

Read [the storage lesson](../../reader/BOOK-LOCATORS.md#book-dc76cc7d0deb3da2) first. This is a local arithmetic exercise with invented offers, not AWS pricing, an invoice forecast or an instruction to change a storage class. It uses no credentials, network or paid service.

After this invented-model exercise, use the [dated Ohio S3 upload-and-delete comparison](ohio-upload-delete/README.md) to see the same reasoning applied to selected public AWS meters and a measured local file-size distribution. That second path is still a pre-credit estimate, not a live bill or a whole-run spending authorization.

Next, try the [versioned read-path worksheet](versioned-read-path/README.md). It adds a replacement, an ordinary delete marker, retained data versions, successful downloads, transfer and explicit unknown KMS calls. Its rates are invented cost units so that the reader can practice finding missing meters without mistaking the subtotal for a regional AWS quote.

Run from the repository root with Python 3.10 or newer:

```sh
python3 examples/storage-cost/lab.py
```

The script prints separate storage, transition and retrieval amounts, billable capacity, charged duration and deadline eligibility. Do not use Python optimization (`-O`): the hand-calculated checks use assertions. Monetary values are fictional cost units (CU), not dollars. One GiB means 2^30 bytes; a billing month is exactly 30 days in this model.

## Assumptions to inspect before calculating

All objects arrive together, are equal in size, remain unchanged, and are deleted together after the supplied days. Each enters the candidate offer once. Retrieval is cumulative GiB over that period; repeat reads can exceed the stored volume. We include the full minimum-duration liability when comparing the alternatives, even if it would be invoiced later. This is a lifecycle comparison, not a statement about monthly cash flow.

| Invented offer | CU/GiB-month | Minimum duration | Billable size floor per object | Entry CU/object | Retrieval CU/GiB | Complete delivery minutes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Ready | 0.02 | 0 days | 0 bytes | 0 | 0 | 1 |
| Shelf | 0.005 | 90 days | 64 KiB | 0.001 | 0.04 | 120 |

For this exercise only, delivery times are assumed complete and fixed; interface, protection and availability requirements are assumed satisfied. Real proposals require evidence for those assumptions. No actual AWS class combines these invented terms by implication.

The model omits request charges other than entry, metadata overhead, temporary restored copies, network transfer, encryption requests, monitoring, taxes, tier discounts, growth, versioning, duplicate copies and operational labor. These are explicit omissions, not claims that those costs are zero in AWS. Object-size floors and metadata overhead are different mechanisms; this model implements only a floor.

## Predict before running

1. Compare 100 objects of one GiB each, retained for 90 days with 10 GiB retrieved. The deadline is 180 minutes. Which offer qualifies, and which costs less?
2. Change only retrieved volume to 150 GiB. Explain why this is possible with only 100 GiB stored. Find the retrieval volume at which costs tie.
3. Return to 100 GiB, but delete all objects after ten days and retrieve nothing. Does deleting data cancel the minimum-duration liability?
4. Store 1,024 objects of one KiB each for 90 days, retrieving nothing. Separate actual bytes, billable bytes and per-object entry charges. Why is multiplying actual bytes by the lowest rate misleading?
5. Return to case 1 but require delivery within 30 minutes. Is a lower calculated cost sufficient to choose Shelf?

Transfer: a teammate proposes combining the small files into one large archive. Explain the effects on entry counts, minimum-size accounting, individual retrieval, customer permissions, deletion and partial updates before deciding. Do not assume packing is always beneficial.

Record your unaided answer before opening [assessor reasoning](ASSESSOR.md). Then ask Codex to challenge the units, omitted costs and deadline assumptions. Keep its corrections separate from your first answer. This exercise does not establish an AWS cost saving.
