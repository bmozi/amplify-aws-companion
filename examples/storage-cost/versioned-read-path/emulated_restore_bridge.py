"""Join emulated S3 version sizes to a dated, incomplete public-price worksheet."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from moto import mock_aws

from priced_lab import SNAPSHOT, price_scenario


HERE = Path(__file__).resolve().parent
RESTORE_LAB = HERE.parents[1] / "integrated-restore" / "s3_version_lab.py"


def load_restore_lab():
    spec = importlib.util.spec_from_file_location("integrated_s3_version_lab", RESTORE_LAB)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_size(versions, version_id):
    matches = [row["Size"] for row in versions if row["VersionId"] == version_id]
    if len(matches) != 1 or type(matches[0]) is not int or matches[0] <= 0:
        raise ValueError("Expected exactly one positive-size emulated data version")
    return matches[0]


def project(*, source_versions, candidate_versions, marker_rows, ids, snapshot):
    """Require inventory facts; time and request counts remain explicit assumptions."""
    if len(marker_rows) != 1 or marker_rows[0]["VersionId"] != ids["delete_marker"] or not marker_rows[0]["IsLatest"]:
        raise ValueError("Current delete marker is not established")
    if len(source_versions) != 2 or len(candidate_versions) != 1:
        raise ValueError("Unexpected data-version inventory")
    original = require_size(source_versions, ids["confirmed_version"])
    replacement = require_size(source_versions, ids["wrong_version"])
    candidate = candidate_versions[0]["Size"]
    if type(candidate) is not int or candidate != original:
        raise ValueError("Staged candidate does not match confirmed version size")

    versions = [
        {"name": "confirmed_original", "bytes": original, "created_day": 0, "removed_day": 30},
        {"name": "wrong_replacement", "bytes": replacement, "created_day": 10, "removed_day": 30},
        {"name": "staged_candidate", "bytes": candidate, "created_day": 20, "removed_day": 30},
    ]
    assumptions = {"horizon_day": 30, "puts": 3, "gets": 2, "transfer_out_bytes": 0}
    retained = price_scenario(versions, assumptions, snapshot)
    removed = price_scenario([versions[0] | {"removed_day": 20}, *versions[1:]], assumptions, snapshot)
    return {
        "emulated_inventory_bytes": {"confirmed_original": original,
                                      "wrong_replacement": replacement,
                                      "staged_candidate": candidate},
        "assumed_lifetimes": versions,
        "assumed_selected_requests": {"put": assumptions["puts"], "get": assumptions["gets"],
                                      "internet_transfer_bytes": 0},
        "price_checked_at_utc": snapshot["checked_at_utc"],
        "retained_through_day_30": retained,
        "confirmed_original_removed_day_20_after_staging": removed,
        "selected_storage_difference_usd": (retained["gross_selected_subtotal_usd"]
                                            - removed["gross_selected_subtotal_usd"]),
        "unmodeled": [
            "delete-marker storage, version listings, bucket setup and deletion requests",
            "customer internet transfer, KMS if selected, retries, logs and other services",
            "actual lifecycle timing, account allowances, credit terms and billing",
        ],
        "approved_to_deploy": False,
    }


@mock_aws
def run():
    restore = load_restore_lab()
    s3 = restore.client()
    ids = restore.seed(s3)
    candidate_key = restore.stage_confirmed_photo(
        s3, actor=restore.OWNER, version_id=ids["confirmed_version"],
        confirmed_version=ids["confirmed_version"],
        confirmation_digest=sha256(restore.EXPECTED_PHOTO).hexdigest(),
    )
    source_versions, markers = restore.exact_versions(s3, restore.key_for(restore.OWNER))
    candidate_versions, _ = restore.exact_versions(s3, candidate_key)
    snapshot = json.loads(SNAPSHOT.read_text())
    result = project(source_versions=source_versions, candidate_versions=candidate_versions,
                     marker_rows=markers, ids=ids, snapshot=snapshot)
    result["scope"] = "Moto version sizes plus declared 30-day assumptions and dated selected public rates; no AWS bill"
    return result


def main():
    print(json.dumps(run(), default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
