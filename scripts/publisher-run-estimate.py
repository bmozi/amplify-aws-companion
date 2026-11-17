"""Validate a human-reviewed, target-bound AWS publisher estimate before the credit gate.

This checks the record's structure and arithmetic, not the truth of forecast usage.
"""

import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import re
from zipfile import BadZipFile, ZipFile


REQUIRED_METERS = {
    "hosting_storage_gb_month", "hosting_transfer_gb", "amplify_build_minutes",
    "ssr_requests_million", "ssr_duration_gb_hour", "backend_and_logs_usd",
    "other_aws_usd",
}
BACKEND_COMPONENTS = {
    "cognito", "appsync", "dynamodb", "s3", "lambda", "cloudwatch", "network",
}
CREDIT_CHARGES = {"amplify_hosting", *BACKEND_COMPONENTS}
RESOURCE_DISPOSITIONS = {"remove_and_verify", "retain_with_next_budget"}


def amount(value, label):
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a nonnegative number")
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"{label} must be a nonnegative number") from None
    if not number.is_finite() or number < 0:
        raise ValueError(f"{label} must be a nonnegative finite number")
    return number


def instant(value, label):
    if not isinstance(value, str):
        raise ValueError(f"{label} needs a timezone-aware date and time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError(f"{label} needs an ISO date and time") from None
    if parsed.tzinfo is None:
        raise ValueError(f"{label} needs a timezone")
    return parsed.astimezone(timezone.utc)


def built_outputs_digest(archive_path, archive_sha256):
    """Read the build's browser-config fingerprint from the exact transferred ZIP."""
    if not re.fullmatch(r"[0-9a-f]{64}", archive_sha256):
        raise ValueError("Build archive digest is missing or malformed")
    with archive_path.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != archive_sha256:
        raise ValueError("Build archive differs from its recorded digest")
    try:
        with ZipFile(archive_path) as archive:
            if archive.namelist().count("config.sha256") != 1 or archive.getinfo("config.sha256").file_size != 65:
                raise ValueError("Build archive has no single browser-config fingerprint")
            digest = archive.read("config.sha256").decode("ascii")
    except (BadZipFile, KeyError, UnicodeDecodeError) as error:
        raise ValueError("Build archive has no readable browser-config fingerprint") from error
    if not re.fullmatch(r"[0-9a-f]{64}\n", digest):
        raise ValueError("Build archive browser-config fingerprint is malformed")
    return digest.strip()


def built_archive_raw_bytes(archive_path):
    """Raw artifact total used as a conservative review threshold, not visit bytes."""
    with ZipFile(archive_path) as archive:
        members = archive.infolist()
        names = [member.filename for member in members]
        if len(names) != len(set(names)) or "index.html" not in names:
            raise ValueError("Build archive needs unique files and an entry page")
        if any(member.is_dir() or member.filename.startswith("/") or "\\" in member.filename or
               any(part in {"", ".", ".."} for part in member.filename.split("/"))
               for member in members):
            raise ValueError("Build archive has an unsafe or directory member")
        if archive.testzip() is not None:
            raise ValueError("Build archive contains an unreadable file")
        return sum(member.file_size for member in members)


def assess(record, *, account_id, app_id, branch, scenario, app_tree_sha, outputs_sha256,
           built_archive_bytes, now):
    if not isinstance(record, dict) or record.get("schema_version") != 8 or record.get("review_status") != "reviewed":
        raise ValueError("Run record is not reviewed")
    if not re.fullmatch(r"[0-9a-f]{40}", app_tree_sha):
        raise ValueError("Current app tree identity is missing or malformed")
    if record.get("app_tree_sha") != app_tree_sha:
        raise ValueError("Run record app tree differs from the reviewed source")
    if not re.fullmatch(r"[0-9a-f]{64}", outputs_sha256):
        raise ValueError("Build browser-config fingerprint is missing or malformed")
    if record.get("amplify_outputs_sha256") != outputs_sha256:
        raise ValueError("Build browser configuration differs from the reviewed configuration")
    expected = {"account_id": account_id, "app_id": app_id, "branch": branch,
                "region": "us-east-2", "scenario": scenario}
    for key, value in expected.items():
        if not value or record.get(key) != value:
            raise ValueError(f"Run record target mismatch: {key}")
    if not isinstance(record.get("reviewed_by"), str) or not record["reviewed_by"].strip():
        raise ValueError("A named human reviewer is required")
    reviewed = instant(record.get("reviewed_at"), "reviewed_at")
    rates = instant(record.get("rates_checked_at"), "rates_checked_at")
    end = instant(record.get("planned_end"), "planned_end")
    for label, when in (("reviewed_at", reviewed), ("rates_checked_at", rates)):
        if when > now or now - when > timedelta(days=7):
            raise ValueError(f"{label} is future-dated or older than seven days")
    credit_terms = record.get("credit_terms")
    if not isinstance(credit_terms, dict) or credit_terms.get("review_status") != "reviewed":
        raise ValueError("Per-credit terms still need owner review")
    receipt_hash = credit_terms.get("owner_receipt_sha256")
    if not isinstance(receipt_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", receipt_hash):
        raise ValueError("Per-credit review needs an exact private receipt digest")
    credit_checked = instant(credit_terms.get("checked_at"), "credit_terms.checked_at")
    if credit_checked > now or now - credit_checked > timedelta(days=7):
        raise ValueError("Per-credit review is future-dated or older than seven days")
    applicability = credit_terms.get("applicability")
    if not isinstance(applicability, dict) or set(applicability) != CREDIT_CHARGES:
        raise ValueError("Per-credit review must cover every selected service family")
    if any(value not in {"eligible", "budgeted_without_credit"} for value in applicability.values()):
        raise ValueError("Per-credit applicability is unknown or malformed")
    if end <= now or end > now + timedelta(days=30):
        raise ValueError("planned_end must be in the next 30 days")
    if scenario == "static_smoke_100_visit_1d" and end > now + timedelta(days=1):
        raise ValueError("One-day smoke scenario must end within 24 hours")
    lifecycle = record.get("lifecycle_review")
    if not isinstance(lifecycle, dict) or lifecycle.get("review_status") != "reviewed":
        raise ValueError("Publication lifecycle still needs owner review")
    for key in ("owner", "stop_new_publication", "resource_verification"):
        if not isinstance(lifecycle.get(key), str) or not lifecycle[key].strip():
            raise ValueError(f"Publication lifecycle needs {key}")
    for key in ("hosting_disposition", "backend_disposition"):
        if not isinstance(lifecycle.get(key), str) or lifecycle[key] not in RESOURCE_DISPOSITIONS:
            raise ValueError(f"Publication lifecycle needs a supported {key}")
    retained = any(lifecycle[key] == "retain_with_next_budget"
                   for key in ("hosting_disposition", "backend_disposition"))
    retained_cost = amount(lifecycle.get("retained_cost_usd"), "retained_cost_usd")
    if retained:
        retained_until = instant(lifecycle.get("retained_until"), "lifecycle_review.retained_until")
        if retained_until <= end or retained_until > end + timedelta(days=30):
            raise ValueError("Retained resources need a removal deadline within 30 days after planned_end")
        if retained_cost <= 0:
            raise ValueError("Retained resources need a positive pre-allowance cost estimate")
        if not isinstance(lifecycle.get("retained_cost_basis"), str) or not lifecycle["retained_cost_basis"].strip():
            raise ValueError("Retained resources need a usage and price basis")
        cleanup_deadline = retained_until
    else:
        if lifecycle.get("retained_until") is not None or retained_cost != 0:
            raise ValueError("Removed resources cannot carry a retention window or cost")
        cleanup_deadline = end
    billing_recheck = instant(lifecycle.get("billing_recheck_at"), "lifecycle_review.billing_recheck_at")
    if billing_recheck <= cleanup_deadline or billing_recheck > cleanup_deadline + timedelta(days=45):
        raise ValueError("Billing recheck must follow cleanup within 45 days")
    if record.get("existing_resources_reviewed") is not True:
        raise ValueError("Existing resources need an explicit cost review")
    active_runs = record.get("active_run_review")
    if not isinstance(active_runs, dict) or active_runs.get("review_status") != "reviewed":
        raise ValueError("Other active runs need an explicit ledger review")
    active_checked = instant(active_runs.get("checked_at"), "active_run_review.checked_at")
    if active_checked > now or now - active_checked > timedelta(hours=1):
        raise ValueError("Active-run ledger review is future-dated or older than one hour")
    if not isinstance(active_runs.get("basis"), str) or not active_runs["basis"].strip():
        raise ValueError("Active-run ledger review needs its evidence basis")
    if type(active_runs.get("other_active_runs")) is not int or active_runs["other_active_runs"] != 0:
        raise ValueError("Another active or unknown run stops publication")
    if record.get("github_actions_reviewed") is not True:
        raise ValueError("GitHub Actions usage needs a separate review")
    rows = record.get("line_items")
    if not isinstance(rows, list):
        raise ValueError("line_items must be a list")
    seen = set()
    base = Decimal("0")
    for row in rows:
        if not isinstance(row, dict) or row.get("meter") not in REQUIRED_METERS:
            raise ValueError("Unknown or malformed cost meter")
        meter = row["meter"]
        if meter in seen:
            raise ValueError(f"Duplicate cost meter: {meter}")
        seen.add(meter)
        quantity = amount(row.get("quantity"), meter + " quantity")
        rate = amount(row.get("unit_price_usd"), meter + " unit price")
        if not isinstance(row.get("basis"), str) or not row["basis"].strip():
            raise ValueError(f"Missing usage or price basis: {meter}")
        base += quantity * rate
    if seen != REQUIRED_METERS:
        raise ValueError("Missing required meters: " + ", ".join(sorted(REQUIRED_METERS - seen)))
    audience = record.get("audience")
    if not isinstance(audience, dict) or audience.get("review_status") != "reviewed":
        raise ValueError("The whole-run audience still needs review")
    if not isinstance(audience.get("backend_usage_basis"), str) or not audience["backend_usage_basis"].strip():
        raise ValueError("The audience needs a backend usage basis for the same visitors")
    visits = amount(audience.get("visits"), "audience visits")
    bytes_per_visit = amount(audience.get("hosting_bytes_per_visit"), "hosting bytes per visit")
    if (visits <= 0 or bytes_per_visit <= 0 or visits != visits.to_integral_value()
            or bytes_per_visit != bytes_per_visit.to_integral_value()):
        raise ValueError("Audience visits and hosting bytes per visit must be positive whole numbers")
    artifact_bytes = amount(built_archive_bytes, "built archive bytes")
    if bytes_per_visit < artifact_bytes:
        raise ValueError("Hosting bytes per visit are below the exact built archive's raw bytes")
    if scenario == "static_smoke_100_visit_1d" and visits != Decimal("100"):
        raise ValueError("Smoke scenario audience must be 100 visits")
    modeled_transfer = visits * bytes_per_visit / Decimal("1000000000")
    hosting_row = next(row for row in rows if row["meter"] == "hosting_transfer_gb")
    if amount(hosting_row["quantity"], "hosting transfer") != modeled_transfer:
        raise ValueError("Hosting transfer does not match the reviewed whole-run audience")
    backend_row = next(row for row in rows if row["meter"] == "backend_and_logs_usd")
    if amount(backend_row["quantity"], "backend quantity") != 1:
        raise ValueError("Backend subtotal needs one reviewed aggregate unit")
    backend_total = amount(backend_row["unit_price_usd"], "backend subtotal")
    if backend_total == 0:
        raise ValueError("Field Lab backend and logs need a nonzero pre-allowance estimate")
    components = record.get("backend_components")
    if not isinstance(components, dict) or set(components) != BACKEND_COMPONENTS:
        raise ValueError("Backend cost breakdown must cover Cognito, AppSync, DynamoDB, S3, Lambda, CloudWatch and network")
    component_total = Decimal("0")
    for name in sorted(BACKEND_COMPONENTS):
        component = components[name]
        if not isinstance(component, dict) or not isinstance(component.get("basis"), str) or not component["basis"].strip():
            raise ValueError(f"Backend component needs a reviewed usage and price basis: {name}")
        if component.get("review_status") != "reviewed":
            raise ValueError(f"Backend component still needs review: {name}")
        component_total += amount(component.get("estimated_usd"), name + " estimated_usd")
    if component_total != backend_total:
        raise ValueError("Backend component estimates do not add up to backend_and_logs_usd")
    contingency = amount(record.get("contingency_usd"), "contingency_usd")
    base += retained_cost
    if contingency < base * Decimal("0.25"):
        raise ValueError("Contingency must be at least 25% of base estimate including retention")
    total = base + contingency
    if total > Decimal("5"):
        raise ValueError("Whole-run AWS estimate exceeds USD 5")
    return {"estimated_run_usd": str(total), "planned_end_epoch": str(int(cleanup_deadline.timestamp())),
            "base_usd": str(base), "contingency_usd": str(contingency),
            "audience_visits": str(visits), "retained_cost_usd": str(retained_cost)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--account-id", required=True)
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--app-tree-sha", required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--archive-sha256", required=True)
    args = parser.parse_args()
    try:
        outputs_sha256 = built_outputs_digest(args.archive, args.archive_sha256)
        archive_bytes = built_archive_raw_bytes(args.archive)
        result = assess(json.loads(args.record.read_text()), account_id=args.account_id,
                        app_id=args.app_id, branch=args.branch, scenario=args.scenario,
                        app_tree_sha=args.app_tree_sha, outputs_sha256=outputs_sha256,
                        built_archive_bytes=archive_bytes,
                        now=datetime.now(timezone.utc))
    except (ValueError, OSError) as error:
        parser.exit(2, f"Run estimate requires review: {error}\n")
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as output:
            for key in ("estimated_run_usd", "planned_end_epoch"):
                output.write(f"{key}={result[key]}\n")
    print("Reviewed AWS run estimate: USD " + result["estimated_run_usd"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
