"""Compare decoded, synthetic business outputs; not a mainframe compatibility test."""

import csv
import sys
from pathlib import Path

FIELDS = ["claim_id", "amount_cents", "status"]
STATUSES = {"PAID", "HELD", "REVERSED"}


def load(path: Path) -> dict[str, tuple[int, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"{path}: expected fields {FIELDS}")
        rows = {}
        for line, row in enumerate(reader, 2):
            claim = row["claim_id"]
            if not claim or claim in rows:
                raise ValueError(f"{path}:{line}: blank or duplicate claim ID {claim!r}")
            cents = row["amount_cents"]
            if not cents.isdecimal() or row["status"] not in STATUSES:
                raise ValueError(f"{path}:{line}: invalid cents or status")
            rows[claim] = (int(cents), row["status"])
        return rows


def compare(source: Path, candidate: Path) -> list[str]:
    old, new = load(source), load(candidate)
    errors = []
    for claim in sorted(old.keys() | new.keys()):
        if claim not in old:
            errors.append(f"unexpected claim {claim}")
        elif claim not in new:
            errors.append(f"missing claim {claim}")
        elif old[claim] != new[claim]:
            errors.append(f"{claim}: source {old[claim]}, candidate {new[claim]}")
    return errors


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: reconcile.py source.csv candidate.csv", file=sys.stderr)
        return 2
    try:
        errors = compare(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    if errors:
        print("FAIL: normalized business outputs differ")
        for error in errors:
            print(f"- {error}")
        return 1
    print("MATCH: normalized claim outputs agree; platform and bank behavior remain untested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
