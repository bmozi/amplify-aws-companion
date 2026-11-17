"""Build the real browser source twice with invented destinations, without AWS."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"
PUBLISHER = APP / "frontend-publisher"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_bundle(js: str, approved_host: str, known_hosts: tuple[str, ...]) -> bool:
    """Check only the invented host markers in this locally built JS."""
    return (approved_host in js and
            all(host == approved_host or host not in js for host in known_hosts))


def run() -> dict:
    dependencies = PUBLISHER / "node_modules"
    if not dependencies.is_dir():
        raise RuntimeError("Install the locked frontend publisher dependencies first")
    with tempfile.TemporaryDirectory(prefix="amplify-config-build-") as folder:
        target = Path(folder)
        for name in ("src", "public"):
            shutil.copytree(APP / name, target / name)
        for name in ("index.html", "vite.config.ts"):
            shutil.copy2(APP / name, target / name)
        shutil.copy2(PUBLISHER / "package.json", target / "package.json")
        (target / "node_modules").symlink_to(dependencies, target_is_directory=True)

        observations = []
        hosts = ("practice.example.invalid", "live.example.invalid")
        cases = (
            ("practice", "practice", True),
            ("practice", "live", False),  # copied live output behind a practice URL
            ("live", "live", True),
        )
        for frontend, backend, should_pass in cases:
            config = {"data": {"url": f"https://{backend}.example.invalid/graphql"}, "version": "1.4"}
            config_file = target / "amplify_outputs.json"
            config_file.write_text(json.dumps(config, separators=(",", ":")))
            result = subprocess.run(["npm", "run", "build"], cwd=target,
                                    capture_output=True, text=True, check=False)
            if result.returncode:
                raise RuntimeError("Local Vite build failed: " + result.stderr[-1000:])
            dist = target / "dist"
            files = {str(path.relative_to(dist)): sha256(path)
                     for path in dist.rglob("*") if path.is_file()}
            js = "\n".join(path.read_text(errors="replace") for path in dist.rglob("*.js"))
            if f"{backend}.example.invalid" not in js:
                raise RuntimeError("The selected invented destination did not reach the browser bundle")
            other = "live" if backend == "practice" else "practice"
            if f"{other}.example.invalid" in js:
                raise RuntimeError("The prior invented destination leaked into the new bundle")
            passed = audit_bundle(js, f"{frontend}.example.invalid", hosts)
            if passed != should_pass:
                raise RuntimeError("Built browser destination audit disagreed with the approved fixture")
            observations.append({"config_sha256": sha256(config_file), "files": files,
                                 "audit_passed": passed})

        if observations[0]["config_sha256"] == observations[1]["config_sha256"]:
            raise RuntimeError("Changed browser configuration kept the same fingerprint")
        if observations[0]["files"] == observations[1]["files"]:
            raise RuntimeError("Changed browser configuration kept identical built files")
        if observations[1]["files"] != observations[2]["files"]:
            raise RuntimeError("Identical live configuration built different artifacts solely from the frontend label")
        return {"builds": 3, "first_files": len(observations[0]["files"]),
                "second_files": len(observations[1]["files"]),
                "config_changed": True, "bundle_changed": True,
                "copied_live_rejected": not observations[1]["audit_passed"],
                "same_bytes_allowed_only_for_live": observations[2]["audit_passed"],
                "scope": "existing-host local Vite builds with invented destinations; no AWS"}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
