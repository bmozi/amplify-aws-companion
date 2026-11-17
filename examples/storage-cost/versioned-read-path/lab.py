"""A local version-retention and reader-path worksheet, with invented CU rates.

This is not an AWS bill estimator. The caller supplies observed/requested counts;
the model never guesses how many KMS calls S3 will make.
"""

from decimal import Decimal as D
import json


GIB = D(2**30)
MODEL_MONTH_DAYS = D(30)
RATES_CU = {
    "storage_per_gib_month": D("0.02"),
    "put_each": D("0.0001"),
    "get_each": D("0.00001"),
    "transfer_out_per_gib": D("0.08"),
    "kms_request_each": D("0.00002"),
    "kms_key_per_model_month": D("0.5"),
}

MIB = 2**20
COMMON = {"horizon_day": 30, "puts": 2, "gets": 40,
          "transfer_out_bytes": 40 * 6 * MIB}
RETAINED_VERSIONS = [
    {"name": "original", "bytes": 4 * MIB, "created_day": 0, "removed_day": 30},
    {"name": "replacement", "bytes": 6 * MIB, "created_day": 10, "removed_day": 30},
]
REMOVED_OLD_VERSION = [
    {"name": "original", "bytes": 4 * MIB, "created_day": 0, "removed_day": 20},
    {"name": "replacement", "bytes": 6 * MIB, "created_day": 10, "removed_day": 30},
]


def estimate(*, versions, horizon_day, puts, gets, transfer_out_bytes,
             kms_requests=None, kms_key_months=None, rates=RATES_CU):
    """Return a bounded subtotal and separate reasons it is not a whole bill."""
    if type(horizon_day) is not int or horizon_day <= 0:
        raise ValueError("horizon_day must be positive")
    if not isinstance(versions, list) or not versions:
        raise ValueError("versions must be a nonempty list")
    byte_days = 0
    for item in versions:
        if set(item) != {"name", "bytes", "created_day", "removed_day"}:
            raise ValueError("each version needs name, bytes, created_day, removed_day")
        size, created, removed = (item[k] for k in ("bytes", "created_day", "removed_day"))
        if (not isinstance(item["name"], str) or not item["name"]
                or type(size) is not int or size <= 0
                or type(created) is not int or type(removed) is not int
                or not 0 <= created < removed <= horizon_day):
            raise ValueError("invalid version lifetime")
        byte_days += size * (removed - created)
    for name, value in (("puts", puts), ("gets", gets),
                        ("transfer_out_bytes", transfer_out_bytes)):
        if type(value) is not int or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")
    if kms_requests is not None and (type(kms_requests) is not int or kms_requests < 0):
        raise ValueError("kms_requests must be an observed nonnegative count")
    if kms_key_months is not None:
        kms_key_months = D(str(kms_key_months))
        if not kms_key_months.is_finite() or kms_key_months < 0:
            raise ValueError("kms_key_months must be nonnegative")
    required_rates = set(RATES_CU)
    if set(rates) != required_rates or any(not D(str(x)).is_finite() or D(str(x)) < 0 for x in rates.values()):
        raise ValueError("invalid invented rate set")

    components = {
        "stored_version_byte_days": D(byte_days) / GIB / MODEL_MONTH_DAYS * D(str(rates["storage_per_gib_month"])),
        "put_requests": D(puts) * D(str(rates["put_each"])),
        "get_requests": D(gets) * D(str(rates["get_each"])),
        "transfer_out": D(transfer_out_bytes) / GIB * D(str(rates["transfer_out_per_gib"])),
    }
    unknown = []
    if kms_requests is None:
        unknown.append("SSE-KMS request count, if SSE-KMS is selected")
    else:
        components["kms_requests"] = D(kms_requests) * D(str(rates["kms_request_each"]))
    if kms_key_months is None:
        unknown.append("customer-managed KMS key time, if that key is selected")
    else:
        components["kms_key_time"] = kms_key_months * D(str(rates["kms_key_per_model_month"]))
    unknown.extend(("actual regional rates and Free plan or credit terms",
                    "multipart, logging, lifecycle, replication and other enabled features",
                    "failed attempts, verification, cleanup and retained resources"))
    return {
        "version_byte_days": byte_days,
        "components_cu": components,
        "modeled_subtotal_cu": sum(components.values()),
        "unknown_for_whole_run": unknown,
        "approved_to_deploy": False,
    }


def main():
    # The customer replaces the 4 MiB file with a 6 MiB file on day 10,
    # then sends an ordinary delete on day 20. A versioned bucket retains
    # both data versions behind a delete marker unless further action occurs.
    print(json.dumps({
        "scope": "invented CU rates; local storage/request/transfer comparison, never a deploy estimate",
        "scenario": "one object replaced on day 10; ordinary delete marker on day 20; 30-day horizon",
        "no_noncurrent_expiry": estimate(versions=RETAINED_VERSIONS, **COMMON),
        "old_version_removed_on_day_20": estimate(versions=REMOVED_OLD_VERSION, **COMMON),
    }, default=str, indent=2))


if __name__ == "__main__":
    main()
