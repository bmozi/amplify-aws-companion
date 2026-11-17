# Assessor reasoning: one JSON handoff, two interpretations

Keep this page separate until the learner has written predictions and run the [two-language exercise](README.md#follow-the-same-bytes-into-node). Assess the explanation of *where* meaning changed, not just the printed values.

The safe update is a control: the quoted part ID and zero-cent price reach both readers; omission is still omission. The Python application returns a new record retaining the old note. The Node program only parses and reports field presence; it does not persist or apply the update. A learner who says both programs saved the record overstates the evidence.

The large numeric event ID remains exact in Python, while ordinary Node `JSON.parse` produces a `Number` outside its safe-integer range and the observed lower value. The quoted variant arrives as text with exact digits. The contract should define identifier syntax and keep it textual end to end; converting to `Number` first and then quoting cannot restore lost digits. This case says nothing about the bounded price field.

The repeated `price_cents` has two values on the wire. The Python lab's `object_pairs_hook` rejects the name before applying an update. Node's ordinary `JSON.parse` result contains the last value, 20; a later object-only validator cannot see that there had been a 10. The appropriate cross-language rule for this teaching contract is reject duplicates at ingress, before treating the parsed object as authoritative. Do not generalize this fixture to every JSON parser or framework.

The emoji note separates three measures: 800 UTF-8 bytes for the note value, 200 Unicode code points, and 400 UTF-16 code units in JavaScript `.length`. `Array.from(note).length` counts code points for this valid string. Neither code-point count nor UTF-16 units automatically equals user-perceived grapheme clusters. The previous Python contract says “200 characters” but implements code points; this exercise makes that implicit unit explicit. A complete production rule would also state normalization, malformed Unicode handling and whole-message byte limits.

For the first changed case, a JavaScript sender that converts the ID to `Number` may already round it before the JSON writer runs; the recipient cannot infer the original digits. For the combining-mark case, two code points may display as one perceived character; a `.length` or code-point cap is not necessarily a reader-perceived-character cap. For the early-rejection client, a duplicate-aware parser can refuse the message while the raw names are still present. These are reasoned extensions, not cases executed by the included script.

Strong work cites the exact observed local output, states the business rule for IDs/duplicates/text length, and names the missing authentication, durable storage and deployed-path checks. No independent learner has attempted this packet yet.
