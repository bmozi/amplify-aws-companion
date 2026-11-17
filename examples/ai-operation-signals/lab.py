"""Offline quality/coverage join over fictional reviewed AI responses."""

import json
from decimal import Decimal
from pathlib import Path


HERE = Path(__file__).resolve().parent
REVIEWS = {"supported", "unsupported", "unreviewed"}


def summarize(payload):
    if payload.get("fictional") is not True:
        raise ValueError("Only explicitly fictional observations are accepted")
    expected = payload.get("expected_reviewed_per_window")
    if type(expected) is not int or expected <= 0:
        raise ValueError("Expected reviewed count must be a positive integer")
    windows = payload.get("windows", {})
    if set(windows) != {"baseline", "current"}:
        raise ValueError("Both baseline and current windows are required")
    answer = {}
    seen = set()
    for label, rows in windows.items():
        if not rows:
            raise ValueError("An empty window cannot support an operating judgment")
        for row in rows:
            if row.get("id") in seen or not row.get("id") or row.get("review") not in REVIEWS or not row.get("source_version"):
                raise ValueError("Missing or duplicate identity, review or source version")
            seen.add(row["id"])
            for meter in ("latency_ms", "input_tokens", "output_tokens"):
                value = row.get(meter)
                if type(value) is not int or value < 0:
                    raise ValueError(f"{meter} must be a nonnegative integer")
        reviewed = [row for row in rows if row["review"] != "unreviewed"]
        unsupported = [row for row in reviewed if row["review"] == "unsupported"]
        answer[label] = {
            "requests": len(rows),
            "reviewed": len(reviewed),
            "unsupported": len(unsupported),
            "unsupported_rate_reviewed": Decimal(len(unsupported)) / Decimal(len(reviewed)) if reviewed else None,
            "latency_mean_ms": Decimal(sum(row["latency_ms"] for row in rows)) / Decimal(len(rows)),
            "input_tokens": sum(row["input_tokens"] for row in rows),
            "output_tokens": sum(row["output_tokens"] for row in rows),
            "source_versions": sorted({row["source_version"] for row in rows}),
            "review_sample_sufficient_for_fixture": len(reviewed) >= expected,
        }
    current = answer["current"]
    baseline = answer["baseline"]
    answer["review_signal"] = bool(
        current["review_sample_sufficient_for_fixture"]
        and baseline["review_sample_sufficient_for_fixture"]
        and current["unsupported_rate_reviewed"] > baseline["unsupported_rate_reviewed"]
    )
    return answer


def main():
    data = json.loads((HERE / "observations.json").read_text())
    report = summarize(data)
    for label in ("baseline", "current"):
        row = report[label]
        print(f"{label}: reviewed {row['reviewed']}/{row['requests']}; unsupported {row['unsupported']}; "
              f"mean latency {row['latency_mean_ms']:.1f} ms; source {','.join(row['source_versions'])}")
    print("Quality investigation signal: " + ("yes" if report["review_signal"] else "not established by this fixture"))
    print("Small fictional samples cannot prove model drift, root cause, production quality or AWS telemetry delivery")


if __name__ == "__main__":
    main()
