"""Offline, fictional Bedrock routing and token-cost decision exercise."""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


HERE = Path(__file__).resolve().parent
METERS = ("standard_input", "cache_read_input", "cache_write_input", "output")
MILLION = Decimal("1000000")


def nonnegative_decimal(value):
    try:
        number = Decimal(value)
    except (InvalidOperation, TypeError) as error:
        raise ValueError("A token count or rate is not numeric") from error
    if not number.is_finite() or number < 0:
        raise ValueError("Token counts and rates must be finite and nonnegative")
    return number


def review(scenario):
    if scenario.get("fictional") is not True:
        raise ValueError("This calculator accepts explicitly fictional rates only")
    source = scenario["source_region"]
    allowed = set(scenario["allowed_processing_regions"])
    if not allowed or not source or source not in allowed:
        raise ValueError("The source Region must be in a nonempty allowed set")
    usage = scenario["usage_tokens"]
    if set(usage) != set(METERS):
        raise ValueError("All four distinct token meters are required")
    counts = {meter: nonnegative_decimal(usage[meter]) for meter in METERS}
    results = []
    seen = set()
    for candidate in scenario["candidates"]:
        name = candidate["name"]
        destinations = set(candidate["destination_regions"])
        rates = candidate["fictional_usd_per_million_tokens"]
        if not name or name in seen or not destinations or set(rates) != set(METERS):
            raise ValueError("Candidate name, destinations and four rates must be complete and unique")
        seen.add(name)
        components = {meter: counts[meter] / MILLION * nonnegative_decimal(rates[meter]) for meter in METERS}
        results.append({
            "name": name,
            "eligible_by_location": destinations <= allowed,
            "unapproved_destinations": sorted(destinations - allowed),
            "components_usd": components,
            "token_subtotal_usd": sum(components.values(), Decimal("0")),
        })
    if not results:
        raise ValueError("At least one candidate is required")
    return results


def main():
    scenario = json.loads((HERE / "scenario.json").read_text())
    print("Fictional rates and usage; not an AWS quote or account estimate")
    for result in review(scenario):
        location = "eligible by stated location rule" if result["eligible_by_location"] else "REJECT: unapproved destination"
        print(f"{result['name']}: ${result['token_subtotal_usd']:.3f} token subtotal; {location}")
        if result["unapproved_destinations"]:
            print("  Possible unapproved destinations: " + ", ".join(result["unapproved_destinations"]))
    print("Add requests, storage, logs, guardrails, retries, quality tests and current model/profile prices before a real decision.")


if __name__ == "__main__":
    main()
