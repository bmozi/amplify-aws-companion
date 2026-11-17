"""Compare a bounded Ohio S3 upload-and-delete path using dated public rates."""

from decimal import Decimal as D
import json
from pathlib import Path
from refresh_prices import SELECTIONS

HERE = Path(__file__).resolve().parent
GIB = D(2**30)
MIN_IA_BYTES = 128 * 1024
MIN_IA_DAYS = 30
DAYS_PER_MODEL_MONTH = D(30)


def prices(snapshot):
    if snapshot.get("schema_version") != 1 or "us-east-2/index.json" not in snapshot.get("source", {}).get("url", ""):
        raise ValueError("expected dated Ohio S3 offer snapshot")
    expected = {"standard_storage": "GB-Mo", "ia_storage": "GB-Mo",
                "ia_small_floor": "GB-Mo", "standard_put": "Requests", "ia_put": "Requests",
                "ia_early_storage": "GB-Mo", "ia_early_small_floor": "GB-Mo"}
    if set(snapshot.get("rates", {})) != set(expected):
        raise ValueError("selected meter set changed")
    result = {}
    for name, unit in expected.items():
        record = snapshot["rates"][name]
        sku, usage, selected_unit = SELECTIONS[name]
        if (record.get("sku") != sku or record.get("usage_type") != usage
                or record.get("unit") != unit or unit != selected_unit
                or record.get("begin_range") != "0"):
            raise ValueError(f"wrong rate selection, unit or tier: {name}")
        value = D(record["usd_per_unit"])
        if not value.is_finite() or value < 0:
            raise ValueError(f"invalid rate: {name}")
        result[name] = value
    return result


def compare_sizes(*, sizes_bytes, days, rates):
    if not isinstance(sizes_bytes, list) or not sizes_bytes or any(type(size) is not int or size <= 0 for size in sizes_bytes):
        raise ValueError("sizes_bytes must be a nonempty list of positive integers")
    objects = len(sizes_bytes)
    if type(days) is not int or days <= 0:
        raise ValueError("days must be a positive integer")
    if days > 365:
        raise ValueError("this teaching model is limited to at most 365 days")
    actual_gb = D(sum(sizes_bytes)) / GIB
    floor_extra_gb = D(sum(max(0, MIN_IA_BYTES - size) for size in sizes_bytes)) / GIB
    held_months = D(days) / DAYS_PER_MODEL_MONTH
    early_months = D(max(0, MIN_IA_DAYS - days)) / DAYS_PER_MODEL_MONTH
    standard = {"stored_bytes": actual_gb * held_months * rates["standard_storage"],
                "puts": D(objects) * rates["standard_put"]}
    ia = {"stored_bytes": actual_gb * held_months * rates["ia_storage"],
          "small_object_floor": floor_extra_gb * held_months * rates["ia_small_floor"],
          "early_delete_stored_bytes": actual_gb * early_months * rates["ia_early_storage"],
          "early_delete_floor": floor_extra_gb * early_months * rates["ia_early_small_floor"],
          "puts": D(objects) * rates["ia_put"]}
    return {"objects": objects, "actual_bytes": sum(sizes_bytes), "days": days,
            "actual_gb": actual_gb, "ia_billable_gb": actual_gb + floor_extra_gb,
            "standard": {**standard, "total": sum(standard.values())},
            "standard_ia": {**ia, "total": sum(ia.values())}}


def compare(*, objects, bytes_each, days, rates):
    for name, value in (("objects", objects), ("bytes_each", bytes_each)):
        if type(value) is not int or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    return compare_sizes(sizes_bytes=[bytes_each] * objects, days=days, rates=rates)


def main():
    snapshot = json.loads((HERE / "public-prices.json").read_text())
    rates = prices(snapshot)
    cases = {
        "short_lived_small_objects": compare(objects=10_000, bytes_each=1024, days=10, rates=rates),
        "long_lived_large_objects": compare(objects=100, bytes_each=2**30, days=60, rates=rates),
    }
    shape = json.loads((HERE / "source-shape.json").read_text())
    if shape.get("schema_version") != 1 or len(shape.get("sizes_bytes", [])) != shape.get("objects"):
        raise ValueError("invalid measured source shape")
    if sum(shape["sizes_bytes"]) != shape.get("unpacked_bytes"):
        raise ValueError("measured source bytes do not reconcile")
    cases["measured_source_individual_files"] = compare_sizes(sizes_bytes=shape["sizes_bytes"], days=10, rates=rates)
    cases["measured_source_one_archive"] = compare_sizes(sizes_bytes=[shape["archive_bytes"]], days=10, rates=rates)
    print(json.dumps({"scope": "direct one-PUT-per-object upload, no read or listing, delete at end; S3-only pre-credit teaching estimate",
                      "price_source": snapshot["source"],
                      "measured_source": {key: value for key, value in shape.items() if key != "sizes_bytes"},
                      "cases": cases}, default=str, indent=2))


if __name__ == "__main__":
    main()
