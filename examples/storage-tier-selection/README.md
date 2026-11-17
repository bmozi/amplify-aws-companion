# Select a storage tier from the access promise

This paper case uses no AWS account and quotes no price. Read the [storage lesson](../../reader/BOOK-LOCATORS.md#book-99d2bc42768a81b0) first, then verify current [S3 storage class behavior](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html) and [archive retrieval guidance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/glacier-storage-classes.html). A tier name is a candidate, not a full cost or recovery design.

## Choose for these five datasets

For each row, pick a primary class or a short list to compare. State the access promise, failure/recreation assumption, object-size distribution, retrieval frequency and total-cost terms that matter. Mark each assumption that you would verify before transition.

| Dataset | Business access promise | Important constraint |
| --- | --- | --- |
| Product thumbnails | Requests arrive at unpredictable times; customer needs an immediate image response | Frequent hot reads and changing popularity |
| Completed analytics output | Usually untouched for months, but may need an immediate read during an investigation | The output can be recomputed from retained source data; finance asks for a lower storage bill |
| Research image archive | A team may retrieve selected images about once per quarter; staff need them immediately during an appointment | Long-lived images, known retrieval audience, many objects near the small-object boundary |
| Annual audit package | An approved request may wait half a business day | Long-lived records; restorations may be grouped |
| Historical instrument logs | Rarely needed, but retention team accepts a multi-day restoration process | Keep separate from live operational recovery copies |

Do not rank by storage price alone. For every candidate, include request/transition and retrieval costs, minimum storage duration, per-object size/metadata effects, restore preparation and temporary copies, transfer, monitoring, expected copies, deletion schedule and human operations. A tier that misses the response promise is not eligible even if its storage line is lowest.

## Changed cases

1. Thumbnail popularity is now stable and high. Does an automatic tiering class still answer the need, or should you compare a frequent-access class? Identify monitoring and request costs.
2. The analytics output is no longer reproducible because the source was deleted. Reconsider the failure/recovery assumption before choosing a single-zone or archive class.
3. The research team now needs instant access only to a small subset but can wait several hours for the rest. Consider splitting datasets or using a restore request workflow; state the added catalog and authorization needs.
4. Audit packages are now requested twice a week. Recalculate eligibility from retrieval activity and total requests; do not assume the original annual-access choice remains best.
5. The log retention period falls below a candidate class's minimum duration. Include the remaining charge if deleted or transitioned early; do not retain data against its deletion requirement to avoid a fee.

Write an unaided answer first and then compare with [assessor notes](ASSESSOR.md). Ask Codex: “Which of my assumptions changes the eligible class, and which changes only its cost?” Verify current AWS facts from the links. No actual tier transition, regional quote, saving or learner result follows from these cases.
