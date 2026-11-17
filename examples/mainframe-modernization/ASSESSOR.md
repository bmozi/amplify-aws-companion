# Assessor: mainframe modernization

The learner should begin with the 06:00 correct-payment promise and distinguish the online transaction, batch chain, data encoding/layout and bank delivery. A service name without those contracts is insufficient.

The matching CSV run proves only that four normalized rows agree under the local comparator. The defective file pays `C-102`, which the source holds; it must fail even though its amount is unchanged. A correct answer treats status as a business result and names the missing evidence: raw record decoding, job order and restart, real integration, deadline, security, reconciliation of bank receipts and business sign-off.

For the 00:01 correction, an acceptable design names the cutoff owner and either queues the correction for the next authorized cycle or performs a documented exception process with a new, idempotent payment instruction. It must not silently mutate an already delivered cycle. A target rerun needs an immutable batch/cycle identifier, stable payment IDs, a record of bank acknowledgements, and a rule for retrying an unacknowledged file without paying twice. The target remains nonpaying until comparative cycles and external-effect tests pass. After payment authority changes, a discovered mismatch requires a halt and forward repair or compensating bank process; simply routing back to the old writer risks a second payment.

Ask why retaining the writer during an inquiry pilot is justified and what evidence would allow another route. A learner may choose a different route if they justify it against compatibility, licensing, timing and irreversible effects. Recheck [AWS's availability notice](https://docs.aws.amazon.com/m2/latest/userguide/mainframe-modernization-availability-change.html) before accepting any claim that a new customer can simply provision the AWS Mainframe Modernization runtime.

No result here establishes compatibility with a mainframe or learner mastery. This is a locally checked design exercise with a synthetic business-output fixture.
