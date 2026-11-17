"""Reconcile fictional cost rows without contacting AWS or recommending deletion."""

import csv
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
PERIODS = {"baseline", "current"}


def load_lines(path: Path):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"period", "resource_id", "service", "meter", "quantity", "unit", "precredit_usd", "project"}
        if set(reader.fieldnames or []) != required:
            raise ValueError("Line-item fields differ from the reviewed fixture")
        rows = list(reader)
    return validate_lines(rows)


def validate_lines(rows):
    seen = set()
    checked = []
    for row in rows:
        row = row.copy()
        key = (row["period"], row["resource_id"], row["meter"])
        if row["period"] not in PERIODS or not row["resource_id"] or not row["meter"] or key in seen:
            raise ValueError("Unknown period, missing identifier or duplicate line")
        seen.add(key)
        try:
            row["quantity"] = Decimal(row["quantity"])
            row["precredit_usd"] = Decimal(row["precredit_usd"])
        except InvalidOperation as error:
            raise ValueError("Non-numeric cost or quantity") from error
        if (not row["quantity"].is_finite() or not row["precredit_usd"].is_finite()
                or row["quantity"] < 0 or row["precredit_usd"] < 0):
            raise ValueError("Usage lines cannot contain negative credits or quantities")
        checked.append(row)
    return checked


def load_adjustments(path: Path):
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        if set(reader.fieldnames or []) != {"period", "type", "amount_usd"}:
            raise ValueError("Adjustment fields differ from the reviewed fixture")
        rows = list(reader)
    if len(rows) != len(PERIODS) or {r["period"] for r in rows} != PERIODS:
        raise ValueError("Need one adjustment for each period")
    result = {}
    for row in rows:
        if row["type"] != "account_credit":
            raise ValueError("Unexpected adjustment type")
        try:
            amount = Decimal(row["amount_usd"])
        except InvalidOperation as error:
            raise ValueError("Non-numeric adjustment") from error
        if not amount.is_finite() or amount > 0:
            raise ValueError("Account credit must not increase usage cost")
        result[row["period"]] = amount
    return result


def reconcile(rows, credits):
    by_period = defaultdict(lambda: defaultdict(lambda: Decimal("0.00")))
    for row in rows:
        group = row["project"] or "unallocated"
        by_period[row["period"]][group] += row["precredit_usd"]
        by_period[row["period"]]["account_precredit"] += row["precredit_usd"]
        if row["meter"] == "internet_out":
            by_period[row["period"]]["internet_out"] += row["precredit_usd"]
            by_period[row["period"]]["internet_out_GB"] += row["quantity"]
    for period in PERIODS:
        groups = by_period[period]
        assert groups["repair"] + groups["shared"] + groups["unallocated"] == groups["account_precredit"]
        groups["account_net"] = groups["account_precredit"] + credits[period]
    return by_period


def main():
    lines = load_lines(HERE / "line-items.csv")
    credits = load_adjustments(HERE / "adjustments.csv")
    totals = reconcile(lines, credits)
    assert totals["baseline"]["account_precredit"] == Decimal("101.00")
    assert totals["current"]["account_precredit"] == Decimal("117.00")
    assert totals["current"]["repair"] == Decimal("78.00")
    assert totals["current"]["shared"] == Decimal("12.00")
    assert totals["current"]["unallocated"] == Decimal("27.00")
    assert totals["current"]["account_net"] == Decimal("102.00")
    assert totals["current"]["internet_out"] - totals["baseline"]["internet_out"] == Decimal("16.00")
    assert totals["current"]["internet_out_GB"] - totals["baseline"]["internet_out_GB"] == Decimal("160")
    assert totals["current"]["account_precredit"] > Decimal("110.00")
    assert totals["current"]["account_net"] < Decimal("110.00")
    # The guard rejects a duplicate, even if a later summary would look plausible.
    with (HERE / "line-items.csv").open(newline="") as stream:
        raw = list(csv.DictReader(stream))
    raw.append(raw[0].copy())
    try:
        validate_lines(raw)
    except ValueError as error:
        assert "duplicate" in str(error)
    else:
        raise AssertionError("A duplicate usage line was accepted")
    for period in ("baseline", "current"):
        group = totals[period]
        print(f"{period}: precredit ${group['account_precredit']:.2f}; repair ${group['repair']:.2f}; "
              f"shared ${group['shared']:.2f}; unallocated ${group['unallocated']:.2f}; "
              f"net after account credit ${group['account_net']:.2f}")
    print(f"Current internet-out: {totals['current']['internet_out_GB']} GB / "
          f"${totals['current']['internet_out']:.2f}; baseline: "
          f"{totals['baseline']['internet_out_GB']} GB / "
          f"${totals['baseline']['internet_out']:.2f}. Scope, route and business cause remain unknown.")
    print("A fictional $110 precredit alert threshold is crossed; the net view is below it. "
          "No AWS alert was configured.")


if __name__ == "__main__":
    main()
