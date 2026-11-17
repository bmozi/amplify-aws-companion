"""Local teaching gate for a signed, digest-bound release decision.

This module runs no scanner, registry, deployment, or AWS call. The caller
supplies a scan-shaped fixture and a pinned public key.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


REQUIRED_COVERAGE = {"operating_system", "application_packages"}
BLOCKING_SEVERITIES = {"HIGH", "CRITICAL"}  # Fictional team's chosen policy.


def canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_signature(payload: bytes, signature: bytes, public_key: Path, work: Path) -> bool:
    message = work / "attestation.json"
    sig = work / "attestation.sig"
    message.write_bytes(payload)
    sig.write_bytes(signature)
    result = subprocess.run(
        ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key),
         "-rawin", "-in", str(message), "-sigfile", str(sig)],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def decide(
    artifact: bytes,
    scan: dict,
    attestation: bytes,
    signature: bytes | None,
    public_key: Path,
    work: Path,
    *,
    expected_release: str,
    now: datetime,
) -> str:
    """Return an explicit hold reason or ALLOW for one fictional policy."""
    if signature is None or not verify_signature(attestation, signature, public_key, work):
        return "HOLD: missing or untrusted signature"
    try:
        signed = json.loads(attestation)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return "HOLD: malformed signed statement"
    if not isinstance(signed, dict) or signed.get("release") != expected_release:
        return "HOLD: wrong release identity"
    artifact_digest = sha256(artifact)
    if signed.get("artifact_sha256") != artifact_digest:
        return "HOLD: artifact bytes differ from signed identity"
    if signed.get("scan_sha256") != sha256(canonical_json(scan)):
        return "HOLD: scan report differs from signed evidence"
    if scan.get("artifact_sha256") != artifact_digest:
        return "HOLD: scan belongs to a different artifact"
    if scan.get("status") != "COMPLETE":
        return "HOLD: scan is incomplete or unavailable"
    coverage = scan.get("coverage")
    if (not isinstance(coverage, list) or any(not isinstance(item, str) for item in coverage)
            or not REQUIRED_COVERAGE.issubset(set(coverage))):
        return "HOLD: required scan coverage is missing"
    try:
        completed = datetime.fromisoformat(scan["completed_at"].replace("Z", "+00:00"))
    except (KeyError, AttributeError, TypeError, ValueError):
        return "HOLD: scan completion time is missing or invalid"
    if completed.tzinfo is None or not (now - timedelta(days=7) <= completed <= now):
        return "HOLD: scan is stale or future-dated"
    findings = scan.get("findings")
    if not isinstance(findings, list) or any(not isinstance(f, dict) for f in findings):
        return "HOLD: findings are unreadable"
    if any(f.get("status") not in ("OPEN", "CLOSED") or
           f.get("severity") not in ("LOW", "MEDIUM", "HIGH", "CRITICAL") for f in findings):
        return "HOLD: finding status or severity is unrecognized"
    if any(f.get("status") == "OPEN" and f.get("severity") in BLOCKING_SEVERITIES
           for f in findings):
        return "HOLD: an open finding crosses this team's release threshold"
    return "ALLOW: local evidence gate passed"
