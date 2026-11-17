"""Join synthetic security records by exact scope and time; no AWS integration."""
from datetime import datetime, timedelta
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VALID_COVERAGE = {"complete", "partial", "not_configured"}
SEVERITY = {"low": 1, "medium": 2, "high": 3, "critical": 4}


def parse_time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("timestamps must include a UTC offset")
    return parsed


def analyze(case):
    window = timedelta(minutes=case["window_minutes"])
    coverage = {}
    for item in case["coverage"]:
        if item["state"] not in VALID_COVERAGE:
            raise ValueError(f"invalid coverage state: {item['state']}")
        key = (item["source"], item["account"], item["region"], item["resource"])
        if key in coverage:
            raise ValueError(f"duplicate coverage declaration: {key}")
        coverage[key] = item["state"]

    findings = [record for record in case["records"] if record["kind"] == "finding"]
    evidence = [record for record in case["records"] if record["kind"] == "evidence"]
    reports = []
    for finding in findings:
        moment = parse_time(finding["time"])
        parse_time(finding["observed_at"])
        expected = set(finding["expected_sources"])
        matched, matched_clocks, excluded = [], [], []
        for record in evidence:
            reason = None
            if record["source"] not in expected:
                reason = "source_not_expected"
            elif record["account"] != finding["account"]:
                reason = "account_mismatch"
            elif record["region"] != finding["region"]:
                reason = "region_mismatch"
            elif record["resource"] != finding["resource"]:
                reason = "resource_mismatch"
            elif abs(parse_time(record["time"]) - moment) > window:
                reason = "outside_time_window"
            if reason:
                excluded.append({"id": record["id"], "reason": reason})
            else:
                matched.append(record["id"])
                parse_time(record["observed_at"])
                matched_clocks.append({"id": record["id"], "event_time": record["time"], "observed_at": record["observed_at"]})

        source_coverage = {
            source: coverage.get((source, finding["account"], finding["region"], finding["resource"]), "unknown")
            for source in sorted(expected)
        }
        complete = bool(expected) and all(state == "complete" for state in source_coverage.values())
        rule = case["alert_rule"]
        alert_reasons = []
        if SEVERITY[finding["severity"].lower()] < SEVERITY[rule["minimum_severity"].lower()]:
            alert_reasons.append("below_minimum_severity")
        for field in ("category", "environment", "account", "region"):
            if finding[field] != rule[field]:
                alert_reasons.append(field + "_mismatch")
        reports.append({
            "finding_id": finding["id"],
            "finding_event_time": finding["time"],
            "finding_observed_at": finding["observed_at"],
            "matched_evidence_ids": matched,
            "matched_evidence_clocks": matched_clocks,
            "excluded_records": excluded,
            "source_coverage": source_coverage,
            "coverage_result": "fixture_declares_complete_for_selected_sources" if complete else "unknown_or_incomplete",
            "interpretation": "correlated_records_to_review" if matched else "no_correlated_record_in_fixture",
            "causation_established": False,
            "alert_evaluation": {
                "rule_id": rule["id"],
                "decision": "candidate_alert" if not alert_reasons else "no_alert",
                "reasons": alert_reasons,
                "owner": rule["owner"],
                "next_read_only_check": rule["next_read_only_check"],
                "delivery_failure_route": rule["delivery_failure_route"],
                "automated_response": False,
            },
        })
    return reports


def main():
    case = json.loads((ROOT / "fixture.json").read_text())
    print(json.dumps(analyze(case), indent=2))


if __name__ == "__main__":
    main()
