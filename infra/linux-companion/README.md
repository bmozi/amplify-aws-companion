# Recheck a clean companion archive on Linux

The usual source-ZIP check extracts and runs on the same Mac that built it. This second route uses Linux/ARM64 by default or locally emulated Linux/AMD64 with `--arch amd64`. Both use Python 3.13, Node 22.23.2 and Terraform 1.6.4. The [Dockerfile](Dockerfile) selects CPU-matched Node and Terraform archives from their official distributions and checks each against its distributor's SHA-256 list during image construction. Default and extended archive checks run with container networking disabled, no mounted AWS credentials, no Docker socket, a non-root user and bounded CPU/memory. The optional fresh npm install below needs network access during its check.

After committing the intended source and creating `artifacts/aws-amplify-lab-source.zip` with `python3 scripts/package-source.py`, run from the repository root:

```sh
bash scripts/check-companion-linux.sh
bash scripts/check-companion-linux.sh --arch amd64
```

Use both commands against the **same** clean source archive when checking this snapshot across the two CPU families. Compare `archive_sha256`, source count, `host`, `status`, `returncode` and each optional-check status in the separate `default-arm64-package-checks.json` and `default-amd64-package-checks.json` reports. The legacy `default-package-checks.json` path is the latest default run and can be overwritten by the next architecture; use the architecture-suffixed reports for comparison. The [reader exercise](../../examples/container-portability/README.md) explains the limits in ordinary language.

The runner copies the archive and checker into the ignored `artifacts/linux-verification/` folder, builds a local image, and invokes the same manifest-verifying `check-packaged-companion.py` that runs on macOS. It retains `artifacts/linux-verification/artifacts/package-checks.json`, including the source ZIP hash, Linux/Python identity and each requested companion result. A failed check returns nonzero. The default suite does not request the npm application build, optional Moto/DuckDB environments or Docker-in-Docker container release drill.

To exercise the optional Moto-emulated architecture and local DuckDB/Parquet suites in the same Linux container, choose the expanded route after packaging:

```sh
bash scripts/check-companion-linux.sh --extended
```

This builds `Dockerfile.extended` on the base image using the **exact pinned requirement lists in this checkout**, then runs the verified ZIP with those two Python environments. It saves a separate `artifacts/linux-verification/artifacts/extended-package-checks.json`; the default run similarly saves `default-package-checks.json`. The expanded route downloads Python packages during image construction, but runs the source archive with networking disabled. Pinned versions reduce drift; these requirement lists do not pin distribution-file hashes, so image construction is not a fully hermetic supply-chain proof. Compare the report's archive SHA-256 with the ZIP you intend to share. The expanded route still leaves application builds and the Docker-in-Docker release drill unrequested.

To check the application and separately staged frontend publisher with **invented** client destinations, provide a local JSON file. For example, in this private checkout:

```sh
printf '%s\n' '{"version":"1.4","data":{"url":"https://practice.example.invalid/graphql"}}' > artifacts/linux-verification/fake-amplify-outputs.json
bash scripts/check-companion-linux.sh --app-config artifacts/linux-verification/fake-amplify-outputs.json
```

This opt-in route verifies the packaged archive, installs both locked npm trees with lifecycle scripts disabled, checks app compatibility, runs a publisher audit, builds both frontends and compares their output bytes. It uses network access for npm registry and advisory reads; it passes empty AWS credential paths and no AWS secrets to the container. The report is `artifacts/linux-verification/artifacts/default-app-package-checks.json`. A second `--extended` flag can add the Python suites. The JSON is a fixture, not a real Amplify backend configuration; a successful build does not prove authentication, authorization, hosted bytes or a visitor result. An npm audit is a dated advisory query, not proof of zero security risk.

This checks source portability across macOS and selected Linux CPU containers on the **same physical computer**. A passing AMD64 lane under emulation is not a native x86 host or independent clean machine. Neither lane proves an application image, ECS behavior, live AWS deployment, independent learner result or final book review. Image construction needs package downloads; default and extended source checks have no execution network. Docker storage used by the local image is separate from AWS credits. [Node release archive](https://nodejs.org/download/release/v22.23.2/), [Terraform release archive](https://releases.hashicorp.com/terraform/1.6.4/).
