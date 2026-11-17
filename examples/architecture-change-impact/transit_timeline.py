"""Fictional transit alert evidence exercise. No messages are sent."""

from __future__ import annotations

import json
from pathlib import Path
import sys

FIXTURE = Path(__file__).with_name("transit-timeline.json")


def review(case: dict) -> list[dict]:
    facts = sorted(case["facts"], key=lambda row: row["confirmed_minute"])
    versions = [row["version"] for row in facts]
    if not facts or versions != list(range(1, len(facts) + 1)):
        raise ValueError("Facts need unique, increasing versions in confirmation order")
    decisions = []
    for event in case["events"]:
        minute = event["minute"]
        known = [fact for fact in facts if fact["confirmed_minute"] <= minute]
        if not known:
            raise ValueError("Event precedes the first confirmed route fact")
        current = known[-1]
        if event["kind"] == "send":
            consent_changes = [row for row in case["consent_changes"]
                               if row["recipient"] == event["recipient"] and row["minute"] <= minute]
            consent = max(consent_changes, key=lambda row: row["minute"])["allowed"] if consent_changes else False
            if event["version"] != current["version"]:
                outcome = "stale_send_blocked"
            elif not consent:
                outcome = "consent_blocked"
            elif event["accepted_by_channel"]:
                outcome = "channel_accepted_reach_unproved"
            else:
                outcome = "send_not_accepted"
        elif event["kind"] == "observation":
            outcome = ("current_notice_observed_on_path" if event["version"] == current["version"]
                       else "stale_notice_observed_on_path")
        else:
            raise ValueError("Unknown event kind")
        decisions.append({
            "id": event["id"], "minute": minute,
            "fact_version_at_event": current["version"],
            "event_version": event["version"], "outcome": outcome,
            "within_five_minutes_of_current_fact": minute - current["confirmed_minute"] <= 5,
        })
    return decisions


def main() -> None:
    if len(sys.argv) != 1:
        raise SystemExit("Usage: python3 transit_timeline.py")
    print(json.dumps(review(json.loads(FIXTURE.read_text())), indent=2))


if __name__ == "__main__":
    main()
