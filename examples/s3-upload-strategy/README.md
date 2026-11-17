# Choose an S3 upload strategy

This paper exercise provisions nothing and includes no AWS prices. Record an unaided design first, then read the [assessor criteria](ASSESSOR.md).

## Three arrivals

Maya's repair shop has three incoming data sets:

1. Customer photographs need an immediate owner-scoped download and independent replacement or deletion.
2. Device readings arrive continuously. Analysts query them in time windows; a delay of up to two minutes is acceptable, and individual reading lookup is rare.
3. A nightly 12-GiB export is already assembled as one file and must be uploaded reliably over an unstable connection.

For each set, choose whether to store separate objects, buffer records into grouped objects, or upload one large object using multipart upload. Explain why the other choices create a mismatch. Distinguish S3 Batch Operations from all three upload choices. Draw the write and read path, including where identity and the individual record index live.

Then answer:

- How many S3 objects and write requests would the device case create if 10,000 records were written one at a time? How many if one output object contains 100 records? State why the lower count is not itself a complete price comparison.
- What must be recorded so an incomplete multipart upload or failed batch delivery can be found and cleaned up?
- Which case changes if the customer must retrieve each reading within five seconds? Which changes if a customer replaces only one photograph?
- What evidence would demonstrate record completeness, integrity and authorized retrieval after a retry?

Do not run a live transfer for this exercise. A real experiment needs a dated regional estimate, explicit object-count/byte caps, duration, retention and a verified cleanup plan.
