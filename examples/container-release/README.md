# A running container is not necessarily ready

This exercise builds one real Docker image and runs five configurations of it. It uses a small Python router on your computer to send actual HTTP requests to loopback-bound container ports. It does not deploy AWS, upload an image, or use AWS credentials.

Prerequisites: Python 3, Docker CLI and a running Linux-container engine reached through a local Unix-socket Docker context. The runner refuses `DOCKER_HOST` overrides and SSH/TCP endpoints, then pins every Docker command to the selected context. A local socket can still be a proxy; use only a workstation engine you control. The pinned Python base must be available locally or downloadable from its public registry. A first build may download that base; `--network=none` disables build-step networking, not registry resolution. This is not an offline guarantee. The recorded run used the already-cached base on an ARM64 Linux Docker engine through Rancher Desktop on macOS.

Run from the repository root:

```sh
python3 examples/container-release/lab.py
```

Do not use Python optimization. Predict which version should answer after each step:

1. Start `v1`, check readiness and route a request to it.
2. Start `bad-config`. Its `/live` returns 200, but `/ready` returns 503. Refuse promotion and confirm the router still serves `v1`.
3. Start `wrong-invoice`. Both health endpoints pass, but a synthetic 1,000-cent subtotal with a 100-cent discount returns 1,000 rather than 900 cents. Refuse promotion and prove the router still serves `v1` with the expected invoice total.
4. Start `v2`. Hold one request open on `v1`, verify readiness and the known invoice result for `v2`, switch the router and prove a new request reaches `v2`. Stop `v1` with SIGTERM; prove its original request completes before the process exits.
5. Hold a request open on a fifth container, then deliberately send SIGKILL to that container only. Verify the connection breaks, the process exits 137 without an OOM flag, and it never logs request completion.
6. Stop the remaining processes and check zero exit codes, no OOM termination and each graceful process's shutdown log.

The five configurations deliberately share one image. The bad candidate is a **bad readiness configuration**, not different defective application code. The printed image ID identifies the locally built artifact. It is not a registry manifest digest or a security-scan result.

## Read the files

- `Dockerfile` pins the base digest, copies only the service, and selects numeric user 10001. Pinning prevents silent base changes but does not establish that the base is free of vulnerabilities; update it through a reviewed rebuild.
- `.dockerignore` keeps unrelated source, credentials and local files out of the build context.
- `service.py` provides distinct liveness/readiness endpoints, a synthetic integer-cent invoice endpoint, and a SIGTERM path that stops accepting requests and waits for non-daemon handlers. Its standard-library HTTP server is a teaching component, not a billing application.
- `lab.py` builds the image, launches bounded containers, checks real HTTP and exact release/total responses before switching the local router, and removes its own resources in a `finally` block.

Each container has a read-only root filesystem, dropped Linux capabilities, no-new-privileges, and bounded CPU, memory and process count. No host folders or Docker socket are mounted. Ports bind only to `127.0.0.1`; Docker's default bridge can still provide outbound connectivity. These settings reduce scope but are not a security audit.

The harness uses unique names and removes only its containers and image tag. It leaves the base image and Docker build cache intact. If interrupted by a force kill or daemon outage, inspect `docker ps -a --filter name=amplify-lesson-` and the printed/run-specific names before removing leftovers. Do not run a global prune against a shared workstation.

## Why the invoice probe matters

The `wrong-invoice` container is **ready** but deliberately ignores the discount. The local release gate asks for a known 900-cent total and the exact candidate release identity before changing the router. This is a tiny business acceptance case, not proof that all invoice rules or customer permissions work. If the same image/configuration can produce a wrong result, green liveness and readiness are insufficient evidence for promotion.

Run the second negative control, which disables only the business probe in the harness. The wrong candidate must then reach the attempted promotion and trigger `BusinessGateFailure`:

```sh
python3 examples/container-release/check-business-negative.py
```

The negative control succeeds only when it exposes that missing gate. It uses unique local Docker resources and removes its own containers and image tag. It does not alter AWS or the normal lab source.

## Why the controlled request matters

`/held` is a test-only endpoint. It records that a request is active, waits for SIGTERM, then waits for the accept loop to stop and performs one second of controlled work before responding. This establishes a known ordering; it is not a model of normal business logic. The harness observes the active state before signaling and checks both the client result and the order of request/termination/completion/exit logs. Request and stop deadlines keep the fixture bounded.

The server explicitly sets `daemon_threads = False` and `block_on_close = True`, so `server_close()` waits for request handlers. Run the negative control to see what happens when that protection is removed in a temporary source copy:

```sh
python3 examples/container-release/check-negative.py
```

This builds another temporary image with daemon request threads. The release test must raise its specific `DrainFailure`, and the negative control succeeds only when that regression is detected. It cleans up its own resources. The original short-delay fixture failed to distinguish the two implementations; the current fixture waits until the accept loop ends before its remaining work. That change strengthens the test without claiming to measure arbitrary production workloads.

## Evidence limits and next challenge

The Docker drill verifies one known invoice result, one controlled in-flight completion and one forced-stop interruption. Both deliberate negative controls detect their targeted regressions. It does **not** prove all invoice rules, zero downtime under load, automatic rollback, multi-host recovery or database compatibility. The router is not an ALB, and this drill contains no ECS scheduler, task role, secret injection, registry scan or AWS network.

## Try work on both sides of a stop deadline

The controlled `/held` request above waits for termination by design. This second, Docker-free exercise gives the same teaching service a bounded amount of actual timed work. It runs two local processes, sends SIGTERM after each request has started, and observes the client and process. No AWS credential or Docker engine is needed.

```sh
python3 examples/container-release/deadline_lab.py
```

Before running it, predict what a 0.4-second request will do inside a three-second stop window, and what a four-second request will do when the process is killed after one second. The script asserts both cases, prints response/exit/log evidence, and removes each child process. It binds only to loopback on an ephemeral port. The `/work` endpoint accepts exactly one integer duration from 0 through 10,000 milliseconds; it makes no persistent change.

The first case returned HTTP 200, logged completion after SIGTERM, and exited zero. The second lost its connection after the forced kill and exited by signal. A response tells us what this local client saw; it does not tell us whether a separate durable write or external charge happened. For real work, choose a request identity and an authoritative status/reconciliation path before telling a disconnected client to retry.

Changed case: if work takes 2.5 seconds and the stop deadline is two seconds, what would you expect? State what must be measured before using that expectation for a customer promise. Ask Codex to explain the difference between the process exit, the client response and a persisted result, then challenge any statement that invents a database effect. This is one process on one workstation, not representative load or a scheduler test.

Independent challenge: add a second invoice rule, such as a capped discount or tax rounding, that the current one-case probe misses. Explain how the candidate, its configuration and the expected business result stay bound to the same release. Do not label the outcome zero downtime or complete invoice correctness without representative workload and failure evidence.

Ask Codex: “Trace the actual promotion and shutdown sequence. Separate process health, readiness, business correctness and in-flight completion. Identify a failure this test cannot catch, then propose a measurable test.” Read [the container lesson](../../reader/BOOK-LOCATORS.md#book-8444a5a7a3bbe0d5) for the AWS mapping and cost boundaries.
