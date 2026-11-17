"""Run a disposable, signed release exercise with nine changed conditions."""

from __future__ import annotations

import copy
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from gate import canonical_json, decide, sha256


NOW = datetime(2026, 10, 27, 18, 0, tzinfo=timezone.utc)


def keypair(work: Path, name: str) -> tuple[Path, Path]:
    private = work / f"{name}-private.pem"
    public = work / f"{name}-public.pem"
    subprocess.run(["openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private)], check=True)
    subprocess.run(["openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True)
    private.chmod(0o600)
    return private, public


def sign(statement: bytes, private: Path, work: Path) -> bytes:
    message = work / "signing-input.json"
    signature = work / "signing-output.sig"
    message.write_bytes(statement)
    subprocess.run(["openssl", "pkeyutl", "-sign", "-rawin", "-inkey", str(private),
                    "-in", str(message), "-out", str(signature)], check=True)
    return signature.read_bytes()


def run() -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="signed-release-") as root:
        work = Path(root)
        private, public = keypair(work, "trusted")
        artifact = b"fictional invoice service build B\n"
        scan = {
            "artifact_sha256": sha256(artifact),
            "status": "COMPLETE",
            "completed_at": "2026-10-27T17:00:00Z",
            "coverage": ["operating_system", "application_packages"],
            "findings": [],
        }
        statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                    "scan_sha256": sha256(canonical_json(scan))})
        signature = sign(statement, private, work)

        def check(a=artifact, s=scan, m=statement, sig=signature, key=public):
            return decide(a, s, m, sig, key, work, expected_release="invoice-v2", now=NOW)

        other_private, _ = keypair(work, "untrusted")
        stale = copy.deepcopy(scan)
        stale["completed_at"] = "2026-10-01T17:00:00Z"
        stale_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                          "scan_sha256": sha256(canonical_json(stale))})
        open_finding = copy.deepcopy(scan)
        open_finding["findings"] = [{"id": "F-101", "severity": "HIGH", "status": "OPEN"}]
        finding_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                            "scan_sha256": sha256(canonical_json(open_finding))})
        unknown_finding = copy.deepcopy(scan)
        unknown_finding["findings"] = [{"id": "F-102", "severity": "UNKNOWN", "status": "OPEN"}]
        unknown_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                             "scan_sha256": sha256(canonical_json(unknown_finding))})
        unknown_status = copy.deepcopy(scan)
        unknown_status["findings"] = [{"id": "F-103", "severity": "HIGH", "status": "UNREVIEWED"}]
        status_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                            "scan_sha256": sha256(canonical_json(unknown_status))})
        allowed_findings = copy.deepcopy(scan)
        allowed_findings["findings"] = [{"id": "F-104", "severity": "LOW", "status": "OPEN"},
                                         {"id": "F-105", "severity": "HIGH", "status": "CLOSED"}]
        allowed_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                             "scan_sha256": sha256(canonical_json(allowed_findings))})
        missing_coverage = copy.deepcopy(scan)
        missing_coverage["coverage"] = ["operating_system"]
        coverage_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                             "scan_sha256": sha256(canonical_json(missing_coverage))})
        incomplete = copy.deepcopy(scan)
        incomplete["status"] = "PENDING"
        incomplete_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                               "scan_sha256": sha256(canonical_json(incomplete))})
        wrong_artifact_scan = copy.deepcopy(scan)
        wrong_artifact_scan["artifact_sha256"] = sha256(b"old image A")
        wrong_artifact_statement = canonical_json({"release": "invoice-v2", "artifact_sha256": sha256(artifact),
                                                   "scan_sha256": sha256(canonical_json(wrong_artifact_scan))})
        return {
            "signed_and_current": check(),
            "unsigned": check(sig=None),
            "changed_artifact": check(a=artifact + b"changed"),
            "changed_report": check(s={**scan, "status": "PENDING"}),
            "wrong_signer": check(sig=sign(statement, other_private, work)),
            "stale_signed_scan": check(s=stale, m=stale_statement, sig=sign(stale_statement, private, work)),
            "open_high_finding": check(s=open_finding, m=finding_statement,
                                       sig=sign(finding_statement, private, work)),
            "unknown_severity": check(s=unknown_finding, m=unknown_statement,
                                       sig=sign(unknown_statement, private, work)),
            "unknown_status": check(s=unknown_status, m=status_statement,
                                     sig=sign(status_statement, private, work)),
            "known_nonblocking_findings": check(s=allowed_findings, m=allowed_statement,
                                                sig=sign(allowed_statement, private, work)),
            "os_only_coverage": check(s=missing_coverage, m=coverage_statement,
                                      sig=sign(coverage_statement, private, work)),
            "signed_incomplete_scan": check(s=incomplete, m=incomplete_statement,
                                            sig=sign(incomplete_statement, private, work)),
            "signed_scan_of_A": check(s=wrong_artifact_scan, m=wrong_artifact_statement,
                                      sig=sign(wrong_artifact_statement, private, work)),
        }


if __name__ == "__main__":
    for name, result in run().items():
        print(f"{name}: {result}")
