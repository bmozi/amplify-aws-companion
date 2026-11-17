"""Join fictional repair outcomes to a *direct-tagged proxy*, not a full bill."""

import argparse
import csv
from decimal import Decimal
from pathlib import Path

from lab import HERE, PERIODS, load_adjustments, load_lines, reconcile


def load_outcomes(path: Path):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"period", "workload", "definition", "correct_on_time_distinct", "provenance"}
        if set(reader.fieldnames or []) != required:
            raise ValueError("Outcome-count fields differ from the fictional case")
        rows = list(reader)
    if len(rows) != len(PERIODS) or {row["period"] for row in rows} != PERIODS:
        raise ValueError("Need exactly one outcome row for each billing period")
    result = {}
    for row in rows:
        if (row["workload"] != "repair" or row["definition"] != "correct_on_time_distinct"
                or row["provenance"] != "fictional_case"):
            raise ValueError("Outcome scope, definition or provenance changed")
        raw = row["correct_on_time_distinct"]
        if not raw.isascii() or not raw.isdecimal():
            raise ValueError("Outcome count must be a nonnegative whole number")
        result[row["period"]] = int(raw)
    return result


def direct_tagged_proxy(totals, outcomes):
    """Never relabel a partial numerator as fully allocated workload cost."""
    if set(outcomes) != PERIODS or any(type(value) is not int or value < 0 for value in outcomes.values()):
        raise ValueError("Need a nonnegative integer outcome count for each period")
    result = {}
    for period in sorted(PERIODS):
        groups = totals[period]
        direct = groups["repair"]
        account = groups["account_precredit"]
        if direct < 0 or account <= 0 or direct > account:
            raise ValueError("Invalid pre-credit direct/account totals")
        count = outcomes[period]
        result[period] = {
            "fictional_correct_on_time_distinct_repairs": count,
            "direct_tagged_precredit_usd": str(direct),
            "shared_precredit_usd": str(groups["shared"]),
            "unallocated_precredit_usd": str(groups["unallocated"]),
            "account_precredit_usd_context_only": str(account),
            "account_credit_usd_context_only": str(groups["account_net"] - account),
            "direct_tagged_usd_per_qualifying_repair_proxy": str(direct / Decimal(count)) if count else None,
            "unit_cost_scope": "direct-tagged proxy only; shared/unallocated costs not assigned",
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-outcomes", type=int, help="Change only the fictional current-period count")
    args = parser.parse_args()
    try:
        counts = load_outcomes(HERE / "outcome-counts.csv")
        if args.current_outcomes is not None:
            counts["current"] = args.current_outcomes
        totals = reconcile(load_lines(HERE / "line-items.csv"),
                           load_adjustments(HERE / "adjustments.csv"))
        result = direct_tagged_proxy(totals, counts)
    except ValueError as error:
        parser.exit(2, f"Cannot make the comparison: {error}\n")
    for period, row in result.items():
        ratio = row["direct_tagged_usd_per_qualifying_repair_proxy"]
        display = f"${ratio}" if ratio is not None else "undefined"
        print(f"{period}: {row['fictional_correct_on_time_distinct_repairs']} qualifying repairs; "
              f"direct-tagged proxy {display} per result; "
              f"shared ${row['shared_precredit_usd']}; unallocated ${row['unallocated_precredit_usd']}")
    print("These fictional counts are declared summaries, not validated customer receipts. "
          "No full repair allocation, AWS billing or live outcome is established.")


if __name__ == "__main__":
    main()
