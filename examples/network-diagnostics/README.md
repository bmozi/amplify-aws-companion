# Diagnose a request without spending cloud credits

Run from the repository root with Python 3.9 or newer:

```sh
python3 examples/network-diagnostics/lab.py
```

The program briefly opens an HTTP server on `127.0.0.1` using an available port. It sends six requests, shuts the server down and checks that the listener has closed. It also evaluates a small in-memory IPv4 route table. No cloud account, external network request, package installation or persistent server is required. An optional `--output evidence/network-drill.json` saves the report in an existing evidence folder.

Before running, predict the result of each request:

| Request | Expected observation | What it establishes |
| --- | --- | --- |
| Alice reads Alice's note | 200 and synthetic note | This fixture's allowed path works |
| Bob reads Alice's note | 403 without note | The application received and rejected this authenticated fixture actor |
| No identity | 401 without note | The fixture requires authentication |
| Unknown credential | 401 without note | An arbitrary credential is not accepted |
| Valid fixture string with no Bearer scheme | 401 without note | Recognizing a value alone is not enough to accept the header |
| Synthetic unavailable dependency path | 503 | An HTTP responder exists, but this fixture reports unavailable service |

After the server closes, a new TCP connection is refused. This is a transport observation, not a 401, 403 or 503. The lab does not create a timeout and does not prove that real infrastructure returns these particular symptoms for every failure.

## Inspect the routing decision

For `10.20.8.9`, the model selects the matching `/24` rather than the broader `/16` or default route. Its target is marked `blackhole`. The model retains that failed choice; it does not silently choose the healthy default route. For another address inside the `/16`, the local route wins. Without a matching route, the result is `null`.

This illustrates longest-prefix selection, not all AWS routing. It has no propagated routes, prefix lists, IPv6, endpoint policies, route-association logic or real packet forwarding. Duplicate destinations are rejected rather than pretending to implement AWS's tie-breaking rules.

## Independent challenge

Add Charlie with a separate note and prove all four Alice/Charlie owner-versus-other combinations. Keep an expected-result table before editing code. A user-supplied owner name must not become authority to read that owner's data. This fixture uses invented tokens; a real application must validate its identity provider's credentials and claims.

For routing, add `10.20.8.128/25` with a different target. Predict where `.9` and `.200` go before running. Explain why changing a route cannot fix an application-level 403. Then consider a timeout: list at least three possible causes and one observation that would distinguish each.

Ask Codex to critique your predictions without running commands or supplying the answer. After the exercise, explain which results came from real loopback behavior and which came from a deliberately simplified model. Connect the result to E02, E09 and the [networking unit](../../reader/BOOK-LOCATORS.md#book-6948135871204c55).
