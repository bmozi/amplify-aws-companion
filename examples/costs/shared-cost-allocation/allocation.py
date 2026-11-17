"""Exact-cent allocation of a fictional pre-credit bill; no AWS data is read."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent


def read_rows(path: Path, columns: set[str]) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or ()) != columns:
            raise ValueError(f"Unexpected columns in {path.name}")
        return list(reader)


def split_cents(cents: int, weights: dict[str, int]) -> dict[str, int]:
    """Largest remainder gives a reproducible whole-cent allocation."""
    if cents < 0 or not weights or any(not owner or units <= 0 for owner, units in weights.items()):
        raise ValueError("Positive driver units and nonnegative charge required")
    total_units = sum(weights.values())
    base = {owner: cents * units // total_units for owner, units in weights.items()}
    remainders = sorted(weights, key=lambda owner: (-(cents * weights[owner] % total_units), owner))
    for owner in remainders[: cents - sum(base.values())]:
        base[owner] += 1
    assert sum(base.values()) == cents
    return base


def allocate(lines: list[dict[str, str]], drivers: list[dict[str, str]]) -> tuple[dict[str, int], int]:
    owners = defaultdict(int)
    shared = {}
    seen_ids = set()
    bill = 0
    for row in lines:
        ident, kind, owner, pool = (row[key].strip() for key in ("id", "kind", "owner", "pool"))
        if not ident or ident in seen_ids or not row["cents"].isdigit():
            raise ValueError("Line IDs must be unique and cents nonnegative integers")
        seen_ids.add(ident)
        cents = int(row["cents"])
        bill += cents
        if kind == "direct" and owner and not pool:
            owners[owner] += cents
        elif kind == "shared" and pool and not owner:
            shared[pool] = shared.get(pool, 0) + cents
        elif kind == "unallocated" and not owner and not pool:
            owners["Unallocated"] += cents
        else:
            raise ValueError(f"Invalid ownership fields in {ident}")
    weights = defaultdict(dict)
    for row in drivers:
        pool, owner, units_text = (row[key].strip() for key in ("pool", "owner", "units"))
        if pool not in shared or not owner or owner == "Unallocated" or not units_text.isdigit():
            raise ValueError("Unknown pool, owner or non-integer driver")
        units = int(units_text)
        if units <= 0 or owner in weights[pool]:
            raise ValueError("Driver units must be positive and owner unique per pool")
        weights[pool][owner] = units
    if set(weights) != set(shared):
        raise ValueError("Every shared pool needs a complete driver declaration")
    for pool, cents in shared.items():
        for owner, assigned in split_cents(cents, weights[pool]).items():
            owners[owner] += assigned
    if sum(owners.values()) != bill:
        raise AssertionError("Owner totals do not reconcile to bill")
    return dict(sorted(owners.items())), bill


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dispute", action="store_true", help="reassign one fictional network driver unit")
    args = parser.parse_args()
    lines = read_rows(HERE / "line-items.csv", {"id", "kind", "owner", "pool", "cents"})
    name = "drivers-dispute.csv" if args.dispute else "drivers.csv"
    drivers = read_rows(HERE / name, {"pool", "owner", "units"})
    owners, bill = allocate(lines, drivers)
    print("Fictional pre-credit bill (cents):", bill)
    for owner, cents in owners.items():
        print(f"{owner}: {cents} cents")
    print("Reconciled:", sum(owners.values()) == bill)


if __name__ == "__main__":
    main()
