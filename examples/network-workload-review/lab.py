"""Aggregate a teaching CSV, not raw AWS records, preserving missing markers."""
from collections import defaultdict
import csv
from pathlib import Path


DATA = Path(__file__).with_name("evidence.csv")


def summarize(path=DATA):
    totals = defaultdict(int)
    statuses = defaultdict(int)
    with path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            status = row["status"]
            statuses[status] += 1
            if status in {"SKIPDATA", "NODATA"}:
                if row["bytes"] not in {"", "-"} or row["action"] not in {"", "-"}:
                    raise ValueError(f"{status} cannot supply measured action or bytes")
                continue
            if status != "OK" or row["action"] not in {"ACCEPT", "REJECT"}:
                raise ValueError("expected an OK flow with ACCEPT or REJECT")
            size = int(row["bytes"])
            if size < 0:
                raise ValueError("bytes must be nonnegative")
            totals[(row["source_group"], row["action"])] += size
    return totals, statuses


def main():
    totals, statuses = summarize()
    print("Synthetic VPC Flow Log-like sample (fictional; analyst labels are not AWS fields)")
    for (group, action), byte_count in sorted(totals.items()):
        print(f"{group:>8} {action:>6}: {byte_count:,} recorded bytes")
    print("Flow record status counts:", ", ".join(f"{k}={v}" for k, v in sorted(statuses.items())))
    print("SKIPDATA is an unknown interval, not zero bytes or an app-b byte estimate.")
    print("Separate fictional NAT metric: BytesInFromSource = 920 GiB for the month")
    print("Separate fictional billing rows: NAT processing = 900 GiB; regional transfer = 120 GiB")
    print("These datasets have different boundaries. No exact match or cause is inferred.")


if __name__ == "__main__":
    main()
