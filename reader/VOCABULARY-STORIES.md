# Vocabulary through a customer request

Use these explanations when a term interrupts your reading. Follow the story, then return to the chapter and explain where its analogy stops. The [compact glossary](../curriculum/LEARNING-ROUTES.md#glossary) provides quick definitions.

## Read network words as a request story

Use this explanation beside [the network lesson](BOOK-LOCATORS.md#book-6948135871204c55). You do not need to memorize every service name before tracing one request. Follow the customer action and identify what each term contributes.

### Find the destination

A customer enters a website name. A **DNS resolver** is the component that looks up an answer for that name. **Authoritative DNS** is responsible for the relevant name's records. The resolver can keep an answer in a **cache**, a saved result reused for later work. The DNS **TTL**, or time to live, specifies how long that answer may be cached by recursive resolvers. Changing the authoritative record does not instantly replace previously cached answers.

The returned **IP address** helps identify a network destination. A **CIDR prefix** describes an address range. In IPv4, a `/25` fixes 25 of 32 address bits, leaving seven bits and therefore 128 addresses. A `/24` fixes fewer bits and contains 256. The larger suffix number describes the smaller range. Total addresses and assignable addresses differ in an AWS subnet, as the growth lab demonstrates.

A **route** tells the network where to send traffic matching a destination range. It does not give the caller permission to read a customer record. A **port** distinguishes a transport endpoint on an address; a **listener** accepts traffic using its configured protocol and port. An address can exist while the expected listener is absent.

### Reach the right worker

An **origin** is the source from which a content-delivery service obtains a response. An **edge location** brings delivery closer to clients; it is not automatically the location holding the authoritative customer record. A **cache key** identifies which saved response may be reused. If the key and access design fail to distinguish private responses correctly, speed can come at the expense of privacy.

A **load balancer** distributes incoming work among eligible destinations. A **target** is one such destination; a **target group** collects destinations with associated routing and health settings. A **health check** observes a configured signal, such as a response from a particular URL. That signal is narrower than proof that booking, payment or invoice calculations work correctly.

A **connection** can carry more than one request. Therefore, balancing connections, DNS answers and individual HTTP requests are different decisions. The right choice depends on the protocol and application behavior; a percentage in one layer does not automatically describe every other layer.

### Leave room when things change

**Headroom** is capacity deliberately left beyond expected demand. Always name its unit: spare addresses, requests per second, storage bytes or money. These quantities cannot substitute for one another. Fifty free addresses do not establish enough CPU or database capacity for fifty more workers.

A **failure domain** is a boundary within which a failure can affect multiple components. Putting two workers in different places helps only if their shared dependencies also meet the recovery requirement. **Failover** redirects work to a recovery path; it does not by itself establish that the destination has current data, enough capacity or authority to accept writes.

Explain this changed case without service names: the website name resolves, the connection succeeds, and the customer receives 403. Which steps have observations, and which permission question remains? Then explain why a failed DNS lookup would require a different investigation. Ask Codex to challenge your distinction between reachability, health and authorization, and verify its answer against the lesson before adopting it.

## Read contract and state words as a repair-shop story

Use this vocabulary beside [the request lesson](BOOK-LOCATORS.md#book-16b52b3769a877e6) and [rental transfer challenge](../examples/business-transfer/README.md). Start with the customer action before trying to remember the technical term.

### Make a promise, then record what happened

Maya's customer submits a repair request. The **API contract** is the agreement between the customer's program and the service: permitted input, required authority, returned information and what each result means. A **receipt** identifies accepted work under that agreement. It is not evidence that the repair is finished. A **business state**, such as accepted or completed, describes where the work stands. An HTTP success status can report that the status lookup worked while the business state says the repair was rejected.

An **invariant** is a rule that must remain true through allowed changes. “Only the owner may read this private request” and “one machine must not have overlapping confirmed rentals” are different invariants. An **atomic operation** makes a specified decision and change indivisible within its supported boundary. Checking a slot and then saving it as unrelated steps leaves room for another caller between those steps. A database transaction can protect the combined check and write in the demonstrated design; it does not make a real-world handover or an external payment part of that same database transaction.

If the reply disappears, the customer's **retry key** lets the service recognize the same intended operation within its defined caller scope and retention period. **Idempotency** means that repeating the operation does not multiply its intended effect under that contract. It does not mean that all repeated text is the same operation, or that an identifier works after its supporting record has expired. A **conflict** means the requested action contradicts a current rule or earlier intent—for example, the same retry key arrives with changed repair details. The caller needs a meaningful next action, not a silent replacement of the original work.

### Separate planned time from physical condition

For the carpet cleaner, an **interval** is a span of time. A **half-open interval** includes its start and excludes its end. In `[09:00, 12:00)`, the square bracket includes 09:00 and the parenthesis excludes 12:00. Another rental can therefore start exactly at noon without overlapping this interval. Planned turnaround time belongs inside the occupied interval in our exercise. The notation describes scheduling; it does not prove that the machine has returned.

A **state transition** changes a recorded condition under a rule: out becomes returned but uninspected, then inspection can make it ready or blocked. A **precondition** is something that must be true before a particular action may happen. The machine being ready is one precondition for handover. A confirmed reservation is another piece of evidence, not a substitute for readiness. A late physical return can leave the calendar mathematically valid while preventing the promised handover.

### Keep older readers working

A **producer** creates a message or representation; a **consumer** reads and acts on it. These are roles in an interaction: a client produces a request and consumes its response. **Serialization** turns the program's values into a transferable representation such as JSON bytes. Successfully decoding those bytes does not prove that the reader understands their business meaning.

**Compatibility** asks whether particular versions can still exchange the required meaning and perform the supported work. An added response field can be harmless to one consumer and rejected by another. An unknown state must not become a success just because the interface lacks a matching label. **Deprecation** announces that a supported contract is being phased out; **retirement** ends that support according to the stated policy. Neither upgrades an offline client automatically. Use the [client compatibility exercise](../examples/api-contract/COMPATIBILITY-REVIEW.md) to test these distinctions.

## Read cost and evidence words as a closing-time story

Maya closes the experiment, then sees its displayed cost increase the next morning. **Usage time** describes when resources were consumed. **Observation time** describes when she inspected the report. A late observation of earlier usage does not by itself prove a resource survived deletion.

**Attribution** assigns a cost or event to the workload that caused it, using supporting evidence. An account-wide total can include several applications. **Allocation** distributes a shared cost according to a stated accounting rule. Changing that rule can move cost between teams without reducing any resource use. Keep the rule visible.

**Reconciliation** compares records or observations, investigates differences and records what remains unresolved. It is not automatically a repair command. For billing, compare the estimate, usage windows, resource lifetime and later reports. For a database, compare the intended records and observed records before deciding whether a correction is justified. Deleting a resource is a change; establishing which resource caused a charge is an evidence task.

A **snapshot** is a view captured at a particular time. A newer billing snapshot may replace an earlier view of the same usage. An **increment** is an additional amount for a distinct interval or change. Adding replacement snapshots can count the same work repeatedly. **Credits** can reduce an amount charged without reducing the underlying usage. An **estimate** predicts cost under assumptions; a **reserve** is capacity in the spending plan deliberately kept for later work. Neither is a real-time enforcement mechanism. Practice with the [billing reconciliation packet](../examples/costs/RECONCILIATION-REVIEW.md).

Explain this changed case in your own words: a noon booking is confirmed, the machine fails inspection, the old client sees an unknown status, and yesterday's usage appears in today's report. Identify four different questions before proposing a fix. Ask Codex to challenge your explanation one question at a time; keep the first response so you can see which distinctions you understood without help.
