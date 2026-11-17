#!/usr/bin/env python3
"""Compare two small frozen JSON exports; never connect to or modify a database."""
import argparse
import json
from collections import Counter
from pathlib import Path

FIELDS = {"booking_id", "customer", "amount_cents", "status"}


def validate(rows):
    if not isinstance(rows, list) or not rows:
        raise ValueError("Expected a nonempty list for this four-booking exercise")
    for row in rows:
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError("Each row must contain exactly the four booking fields")
        if any(not isinstance(row[k], str) or not row[k].strip()
               for k in ("booking_id", "customer")):
            raise ValueError("Booking ID and customer must be nonempty strings")
        if type(row["amount_cents"]) is not int or row["amount_cents"] < 0:
            raise ValueError("Amount must be nonnegative integer cents")
        if row["status"] not in ("confirmed", "cancelled"):
            raise ValueError("Unknown booking status")


def compare(expected, candidate):
    """Expected is authoritative for this snapshot, including during rollback."""
    for rows in (expected, candidate):
        validate(rows)
    duplicates = {
        name: sorted(k for k, count in Counter(r["booking_id"] for r in rows).items()
                     if count > 1)
        for name, rows in (("expected", expected), ("candidate", candidate))
    }
    # Do not collapse duplicate IDs into a dict and silently discard evidence.
    if any(duplicates.values()):
        return {"result": "HOLD", "duplicate_ids": duplicates,
                "reason": "Identity is ambiguous; no field comparison performed"}
    left = {r["booking_id"]: r for r in expected}
    right = {r["booking_id"]: r for r in candidate}
    missing = sorted(left.keys() - right.keys())
    unexpected = sorted(right.keys() - left.keys())
    changed = {
        key: {field: {"expected": left[key][field], "candidate": right[key][field]}
              for field in sorted(FIELDS - {"booking_id"})
              if left[key][field] != right[key][field]}
        for key in sorted(left.keys() & right.keys())
        if left[key] != right[key]
    }
    totals = {
        name: {"rows": len(rows), "amount_cents": sum(r["amount_cents"] for r in rows),
               "confirmed_cents": sum(r["amount_cents"] for r in rows
                                      if r["status"] == "confirmed")}
        for name, rows in (("expected", expected), ("candidate", candidate))
    }
    return {"result": "HOLD" if missing or unexpected or changed else "MATCH",
            "missing_ids": missing, "unexpected_ids": unexpected,
            "changed_fields": changed, "totals": totals,
            "scope": "Frozen supplied records only; MATCH is not cutover approval"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        report = compare(json.loads(args.expected.read_text()),
                         json.loads(args.candidate.read_text()))
    except (OSError, ValueError) as exc:
        print(json.dumps({"result": "INVALID", "reason": str(exc)}))
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["result"] == "MATCH" else 1


if __name__ == "__main__":
    raise SystemExit(main())
