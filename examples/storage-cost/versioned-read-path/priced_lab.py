"""Dated public-price extension of the offline version-retention worksheet."""

from decimal import Decimal as D
import json
from pathlib import Path

from lab import COMMON, GIB, REMOVED_OLD_VERSION, RETAINED_VERSIONS, estimate

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE / "public-prices.json"
METERS = ("standard_storage", "standard_put", "standard_get", "internet_out")


def price_scenario(versions, common, snapshot):
    """Return selected pre-credit meters, never a whole-run deployment approval."""
    if snapshot.get("schema_version") != 1 or set(snapshot.get("rates", {})) != set(METERS):
        raise ValueError("missing or unexpected selected public rates")
    rates = snapshot["rates"]
    expected_units = {"standard_storage": "GB-Mo", "standard_put": "Requests",
                      "standard_get": "Requests", "internet_out": "GB"}
    for key, unit in expected_units.items():
        row = rates[key]
        if row.get("unit") != unit or row.get("begin_range") != "0":
            raise ValueError(f"{key}: unsupported unit or tier")
        value = D(row["usd_per_unit"])
        if not value.is_finite() or value < 0:
            raise ValueError(f"{key}: invalid rate")
    checked = estimate(versions=versions, **common)
    counts = {"standard_storage": D(checked["version_byte_days"]) / GIB / D(30),
              "standard_put": D(common["puts"]),
              "standard_get": D(common["gets"]),
              "internet_out": D(common["transfer_out_bytes"]) / GIB}
    for key, count in counts.items():
        upper = rates[key].get("end_range", "Inf")
        if upper != "Inf" and count >= D(upper):
            raise ValueError(f"{key}: modeled use exceeds selected first tier")
    components = {key: counts[key] * D(rates[key]["usd_per_unit"]) for key in METERS}
    return {
        "version_byte_days": checked["version_byte_days"],
        "metered_quantities": counts,
        "components_usd": components,
        "gross_selected_subtotal_usd": sum(components.values()),
        "unpriced_or_unverified": [
            "account-specific Free plan, shared internet allowance, credits and expiry",
            "delete-marker bytes and any other retained versions or replicas",
            "KMS key and request use if SSE-KMS is selected",
            "failed or retried requests, verification, cleanup and other enabled services",
            "taxes and future price or tier changes",
        ],
        "approved_to_deploy": False,
    }


def main():
    snapshot = json.loads(SNAPSHOT.read_text())
    result = {
        "scope": "offline, dated Ohio public-price comparison; no account access or deployment approval",
        "price_checked_at_utc": snapshot["checked_at_utc"],
        "price_sources": snapshot["sources"],
        "retained_through_day_30": price_scenario(RETAINED_VERSIONS, COMMON, snapshot),
        "old_version_removed_day_20": price_scenario(REMOVED_OLD_VERSION, COMMON, snapshot),
    }
    result["retained_minus_removed_usd"] = (
        result["retained_through_day_30"]["gross_selected_subtotal_usd"]
        - result["old_version_removed_day_20"]["gross_selected_subtotal_usd"]
    )
    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
