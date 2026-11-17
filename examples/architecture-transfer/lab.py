"""Observe three different business promises in existing local fixtures; no AWS calls."""

from importlib import import_module, util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory


BASE = Path(__file__).resolve().parents[2]


def must_deny(action):
    try:
        action()
    except PermissionError:
        return True
    raise AssertionError("The proposed read was unexpectedly allowed")


def repair_receipt():
    """Execute the real two-process SQLite/HTTP retry drill, not a copied rule."""
    command = [sys.executable, str(BASE / "examples/resilience-exercise/process_lab.py")]
    completed = subprocess.run(command, cwd=BASE, check=True, capture_output=True,
                               text=True, timeout=20)
    observed = json.loads(completed.stdout)
    assert observed["first_customer_outcome"] == "timeout"
    assert observed["committed_before_worker_stop"]
    assert observed["worker_pids_differ"]
    assert observed["fault_request_records"] == 1
    assert observed["hypothesis_met"]
    return {
        "accepted_fact": "one local booking record survived a lost reply and worker replacement",
        "retry_same_record": observed["fault_request_records"] == 1,
        "changed_customer_rejected": observed["customer_conflict_rejected"],
        "copying_rule_would_miss": "whether an external technician scheduler committed before its reply vanished",
        "evidence": "loopback HTTP, two processes, same-host SQLite",
    }


def school_release(path):
    """Use the actual two-gate module: storage and scan are not approval."""
    school_dir = BASE / "examples/file-intake"
    sys.path.insert(0, str(school_dir))
    try:
        review = import_module("review_lab")
        intake = import_module("lab")
        review.initialize_review(path)
        data = b"Invented school document"
        digest = intake.upload(path, "school-1", "alice", data)
        with sqlite3.connect(path) as db:
            stored_before_review = db.execute(
                "SELECT status FROM objects WHERE id='school-1'").fetchone() == ("quarantined",)
        assert stored_before_review
        upload_private = must_deny(lambda: intake.read(path, "school-1", "alice"))
        assert review.decide(path, "school-1", digest, "scanner-1", "scan", "pass") == "awaiting_review"
        scan_private = must_deny(lambda: intake.read(path, "school-1", "alice"))
        assert review.decide(path, "school-1", digest, "reviewer-1", "review", "approve") == "available"
        released = intake.read(path, "school-1", "alice") == data
        other_owner_private = must_deny(lambda: intake.read(path, "school-1", "bob"))
        assert upload_private and scan_private and released and other_owner_private
        return {
            "accepted_fact": "private bytes arrived, but no approved owner read existed yet",
            "stored_before_review": stored_before_review,
            "owner_denied_after_upload": upload_private,
            "owner_denied_after_scan_pass": scan_private,
            "owner_reads_exact_bytes_after_review": released,
            "other_owner_denied": other_owner_private,
            "copying_rule_would_miss": "a stored file or clean scan is not a human-approved release",
            "evidence": "local SQLite gate decisions and owner read, synthetic identities and scan",
        }
    finally:
        sys.path.pop(0)


def tenant_result(path):
    """Use the actual tenant-scoped query/cache fixture with a colliding ID."""
    spec = util.spec_from_file_location("transfer_tenant_lab", BASE / "examples/tenant-isolation/lab.py")
    assert spec and spec.loader
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    service = module.Service(path)
    a = service.read("fixture-alice", "shared-id")
    b = service.read("fixture-bob", "shared-id")
    assert a == "A private note" and b == "B private note" and a != b
    guessed_neighbor_denied = must_deny(lambda: service.read("fixture-alice", "b-only"))
    forged_scope_denied = must_deny(
        lambda: service.read("fixture-alice", "shared-id", requested_tenant="shop-b"))
    cache_separated = set(service.cache) == {("shop-a", "shared-id"), ("shop-b", "shared-id")}
    assert guessed_neighbor_denied and forged_scope_denied and cache_separated
    service.cache.clear()
    cold_cache_separated = (service.read("fixture-bob", "shared-id") == b
                            and service.read("fixture-alice", "shared-id") == a)
    assert cold_cache_separated
    return {
        "accepted_fact": "the same record ID exists in two organizations with different private contents",
        "guessed_neighbor_denied": guessed_neighbor_denied,
        "forged_scope_denied": forged_scope_denied,
        "warm_cache_keys_include_tenant": cache_separated,
        "cold_cache_stays_separate": cold_cache_separated,
        "copying_rule_would_miss": "a shared record ID or ID-only cache key is not tenant authority",
        "evidence": "local SQLite query and in-process cache with fixture memberships",
    }


def run():
    repair = repair_receipt()
    with TemporaryDirectory(prefix="amplify-context-transfer-") as raw:
        folder = Path(raw)
        school = school_release(folder / "school.sqlite")
        tenant = tenant_result(folder / "tenant.sqlite")
    assert not folder.exists()
    return {
        "repair": repair,
        "school": school,
        "tenant": tenant,
        "cross_context_result": "one common request path, three different acceptance and access contracts",
        "limits": "No external scheduler, authentication, real scan, direct object URL, distributed cache, AWS service, bill, or learner result was tested",
        "temporary_files_removed": True,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
