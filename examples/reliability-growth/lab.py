"""Fictional reliability-growth arithmetic; no AWS calls or predictions."""
import argparse
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import json
from pathlib import Path


def positive_int(value, label, *, allow_zero=False):
    if type(value) is not int or value < (0 if allow_zero else 1):
        raise ValueError(f"{label} must be a {'nonnegative' if allow_zero else 'positive'} integer")
    return value


def analyze(fixture):
    peaks = fixture["weekly_peak_success_per_second"]
    if not isinstance(peaks, list) or len(peaks) < 2:
        raise ValueError("at least two weekly peaks are required")
    peaks = [positive_int(value, "weekly peak") for value in peaks]
    planning_peak = positive_int(fixture["planning_next_peak_success_per_second"], "planning peak")
    try:
        retry_percent = Decimal(str(fixture["retry_overhead_percent"]))
    except (InvalidOperation, ValueError):
        raise ValueError("retry overhead must be a finite percentage") from None
    if not retry_percent.is_finite() or retry_percent < 0:
        raise ValueError("retry overhead must be a finite nonnegative percentage")
    attempts_needed = int((Decimal(planning_peak) * (1 + retry_percent / 100)).to_integral_value(rounding=ROUND_CEILING))

    layouts = fixture["layouts"]
    if not isinstance(layouts, list) or not layouts:
        raise ValueError("at least one layout is required")
    results = []
    names = set()
    for layout in layouts:
        name = layout["name"]
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("layout names must be unique nonempty strings")
        names.add(name)
        zones = layout["zone_attempt_capacity_per_second"]
        if not isinstance(zones, dict) or len(zones) < 2:
            raise ValueError("each layout needs at least two zones")
        capacities = {zone: positive_int(value, "zone capacity") for zone, value in zones.items()}
        if any(not isinstance(zone, str) or not zone for zone in capacities):
            raise ValueError("zone names must be nonempty strings")
        data = positive_int(layout["shared_data_attempt_capacity_per_second"], "shared data capacity")
        failures = []
        for failed_zone in capacities:
            surviving_app = sum(value for zone, value in capacities.items() if zone != failed_zone)
            useful = min(surviving_app, data)
            failures.append({"failed_zone": failed_zone, "surviving_application": surviving_app,
                             "shared_data": data, "modeled_path_capacity": useful,
                             "margin": useful - attempts_needed,
                             "limiter": "application" if surviving_app < data else "data" if data < surviving_app else "tied"})
        worst = min(failures, key=lambda row: (row["margin"], row["failed_zone"]))
        results.append({"name": name, "worst_failure": worst, "all_zone_failures": failures})

    launch = fixture["proposed_launch"]
    requested = positive_int(launch["requested_workers"], "requested workers")
    quota = positive_int(launch["applied_quota_headroom_workers"], "quota headroom", allow_zero=True)
    placement = positive_int(launch["compatible_placement_workers"], "compatible placement", allow_zero=True)
    ready = positive_int(launch["registered_and_business_ready_workers"], "ready workers", allow_zero=True)
    permission = launch["image_role_permission_verified"]
    if type(permission) is not bool or ready > requested:
        raise ValueError("permission must be boolean and ready workers cannot exceed requested workers")
    blockers = []
    if quota < requested:
        blockers.append("applied_quota")
    if placement < requested:
        blockers.append("compatible_placement")
    if not permission:
        blockers.append("image_role_permission")
    if ready < requested:
        blockers.append("registered_business_ready")
    return {"scope": "synthetic capacity screen; no AWS performance or availability proof",
            "observed_weekly_changes": [b-a for a, b in zip(peaks, peaks[1:])],
            "planning_peak_is_supplied_not_predicted": planning_peak,
            "retry_overhead_percent": str(retry_percent), "attempts_needed": attempts_needed,
            "layouts": results,
            "proposed_launch": {"requested_workers": requested, "blockers": blockers,
                                "status": "blocked" if blockers else "provisioning_candidate_only"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).with_name("fixture.json"))
    args = parser.parse_args()
    print(json.dumps(analyze(json.loads(args.fixture.read_text())), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
