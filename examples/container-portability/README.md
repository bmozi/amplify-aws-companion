# Carry one source bag through two Linux rooms

Imagine Maya packs the same recipe in one sealed bag. She can open that bag in two kitchens, but an ARM64 mixer and an AMD64 mixer need different motor parts. A recipe that passes in one kitchen may expose a hidden machine assumption in the other. It still does not prove diners received the right meal.

The [illustrated path](source-two-cpus.svg) uses this repository's companion **source ZIP**, not a deployable application image. It checks its manifest and runs local lessons/tests in Linux ARM64 and Linux AMD64 containers on the **same Mac**. The AMD64 lane uses emulation. Both containers run the archive with networking disabled, no mounted AWS credentials, no Docker socket, a non-root user, and bounded CPU/memory. Image construction downloads Node and Terraform and verifies their official SHA-256 listings; the check run does not download anything. Inspect the exact [runner](../../scripts/check-companion-linux.sh) and [Dockerfile](../../infra/linux-companion/Dockerfile) before trusting the scope.

After committing your intended source and packaging it with `python3 scripts/package-source.py`, run from the repository root if local Docker is available:

```bash
bash scripts/check-companion-linux.sh --arch arm64
bash scripts/check-companion-linux.sh --arch amd64
```

The runner retains separate `default-arm64-package-checks.json` and `default-amd64-package-checks.json` under ignored `artifacts/linux-verification/artifacts/`. Compare each report's `archive_sha256`, `source_files`, `status`, `returncode` and host architecture. A meaningful comparison needs the **same archive hash**, both statuses passed, and the expected different CPU families. A passing count alone does not prove that every optional check ran; read the `companion.checks` entries and reasons for `not_requested`.

### Observed case: native x86 settles an emulation failure

For source commit `398897263b9edcb6a73432ff434556237b37764d`, both same-Mac containers verified the identical 1,481-file source ZIP SHA-256 `5ef5eb909025293c95b006260b4ace52454c56016ecd7c8e1cfc78e61619c56a`. ARM64 passed 241 requested checks; 17 optional groups were not requested. AMD64 under emulation passed 235 but failed six Terraform-related checks when the emulated Go runtime reported `lfstack.push invalid packing`. Raising the suite's process limit from five to 20 minutes allowed the actual failure to surface; time alone did not repair it. The AMD64 failure report was preserved. This same-host experiment does **not** count as a two-lane pass.

The native Ubuntu x86 workflow run in the owner's private repository (run record withheld from this packet) checked out that exact commit, rebuilt a byte-identical source ZIP and manifest, ran the cloud-free suite, and reported `status: passed` with temporary extraction removed. Its host was `Linux-7.0.0-1017-azure-x86_64-with-glibc2.39`. This supports portability of the checked source and suite across the tested ARM container and native x86 runner. The host, base image, and tool installation differ, so it is not a proof that the same Docker image runs every check on x86, an ECS image works, or a customer receives the right result. The workflow's GitHub Actions minute is separate from AWS credits; no AWS account was used.

The optional `--extended` route installs the pinned Moto and DuckDB environments during image construction and runs those additional local checks without execution networking. It is slower under AMD64 emulation. It does not start AWS, a real database service or an ECS task. The `--app-config` route uses invented destinations and networked npm installation; it is a separate build check, not part of the default offline comparison.

Before reading the [assessor notes](ASSESSOR.md), answer three changed cases:

1. ARM passes but AMD64 fails to start Node because an ARM binary was copied into that lane. Would rerunning ARM settle the failure? Name the file and build selection to inspect.
2. Both reports pass but their archive hashes differ. Can they establish that *this exact source snapshot* works in both rooms?
3. Both reports pass, then an ECS task using a different application image starts but returns the wrong invoice. Which evidence did the source check establish, and what separate image/platform and customer-path observations are missing?

AWS ECS task definitions can specify `runtimePlatform.cpuArchitecture` as `X86_64` or `ARM64`; the selected application image must match the intended platform. [AWS runtime platform reference](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RuntimePlatform.html). Docker documents emulation as one way to build or run across platforms and warns it can be slower than native nodes. [Docker multi-platform builds](https://docs.docker.com/build/building/multi-platform/). Our same-host source check is narrower than an ECS deployment, a native x86 host, an independent machine or a customer outcome.

Ask Codex to compare the two reports and identify one unsupported conclusion in your first answer. Have it point to the exact report fields or missing ECS/customer observation. Keep your unaided answer, its critique and your revision separate. This lab uses no AWS account or credit; any later cloud trial still needs scoped non-root identity, complete selected-service pricing and cleanup. Choose whole-run spending and reserve limits for the account you will use.
