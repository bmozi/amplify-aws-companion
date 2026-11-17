"""Compare fictional network-path charges without AWS credentials or network calls."""
from decimal import Decimal
import json

HOURS_PER_MONTH = Decimal("730")


def estimate_path(hours, fixed_hourly_items, data_gib_items):
    """Return componentized teaching points; items are (count or GiB, rate)."""
    hours = Decimal(str(hours))
    if hours < 0:
        raise ValueError("Hours cannot be negative")
    fixed = Decimal("0")
    for count, rate in fixed_hourly_items:
        count, rate = Decimal(str(count)), Decimal(str(rate))
        if count < 0 or rate < 0:
            raise ValueError("Counts and rates cannot be negative")
        fixed += count * hours * rate
    processed = Decimal("0")
    for gib, rate in data_gib_items:
        gib, rate = Decimal(str(gib)), Decimal(str(rate))
        if gib < 0 or rate < 0:
            raise ValueError("Traffic and rates cannot be negative")
        processed += gib * rate
    return {"fixed_hourly_points": fixed, "data_processing_points": processed,
            "total_points": fixed + processed}


def compare_s3_paths(volume_gib, *, same_region, workload_in_vpc):
    if not same_region or not workload_in_vpc:
        raise ValueError("This gateway-endpoint comparison requires a VPC workload and same-Region S3")
    if Decimal(str(volume_gib)) < 0:
        raise ValueError("Traffic volume cannot be negative")
    # These are deliberately fictional teaching rates, not AWS pricing.
    gateway = estimate_path(HOURS_PER_MONTH, [], [])
    nat = estimate_path(HOURS_PER_MONTH, [(1, "0.045")], [(volume_gib, "0.045")])
    return {"same_region_vpc_s3_gateway_endpoint": gateway,
            "nat_gateway_path": nat}


def compare_supported_aws_api_paths(volume_gib):
    # Invented rates make fixed-versus-variable tradeoffs visible without quoting AWS.
    if Decimal(str(volume_gib)) < 0:
        raise ValueError("Traffic volume cannot be negative")
    nat = estimate_path(HOURS_PER_MONTH, [(1, "0.045")], [(volume_gib, "0.045")])
    interface = estimate_path(HOURS_PER_MONTH, [(2, "0.030")], [(volume_gib, "0.010")])
    return {"nat_gateway_path": nat,
            "two_az_interface_endpoint_path": interface}


def main():
    s3 = compare_s3_paths(800, same_region=True, workload_in_vpc=True)
    low = compare_supported_aws_api_paths(100)
    high = compare_supported_aws_api_paths(500)
    assert s3["same_region_vpc_s3_gateway_endpoint"]["total_points"] == Decimal("0")
    assert s3["nat_gateway_path"]["total_points"] == Decimal("68.850")
    assert low["nat_gateway_path"]["total_points"] < low["two_az_interface_endpoint_path"]["total_points"]
    assert high["nat_gateway_path"]["total_points"] > high["two_az_interface_endpoint_path"]["total_points"]
    assert high["two_az_interface_endpoint_path"]["fixed_hourly_points"] == Decimal("43.800")
    try:
        compare_s3_paths(1, same_region=False, workload_in_vpc=True)
    except ValueError:
        wrong_region_rejected = True
    else:
        raise AssertionError("Do not extend a gateway-endpoint result to another Region")
    try:
        compare_supported_aws_api_paths(-1)
    except ValueError:
        negative_traffic_rejected = True
    else:
        raise AssertionError("Negative traffic cannot represent a workload")
    result = {
        "s3_800_gib": s3,
        "api_100_gib": low,
        "api_500_gib": high,
        "wrong_region_gateway_endpoint_comparison_rejected": wrong_region_rejected,
        "negative_traffic_rejected": negative_traffic_rejected,
        "scope": "Arithmetic over fictional teaching points only; no AWS rates, routes, usage, credentials or bill are inspected",
    }
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
