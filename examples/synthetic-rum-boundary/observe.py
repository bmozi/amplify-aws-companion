"""Offline evidence arithmetic for a fictional booking journey; no AWS access."""

import json
import sys
from pathlib import Path


def inspect(window):
    fields = (
        "canary_expected", "canary_reported", "canary_success",
        "browser_visits", "rum_received", "rum_error_sessions",
        "accepted", "completed",
    )
    for field in fields:
        value = window[field]
        if type(value) is not int or value < 0:
            raise ValueError(f"{field} must be a nonnegative whole number")
    if not 0 <= window["canary_success"] <= window["canary_reported"] <= window["canary_expected"]:
        raise ValueError("canary counts must be success <= reported <= expected")
    if not 0 <= window["rum_error_sessions"] <= window["rum_received"] <= window["browser_visits"]:
        raise ValueError("RUM counts must be errors <= received <= independent browser visits")
    if window["completed"] > window["accepted"]:
        raise ValueError("completed cannot exceed accepted in this stipulated cohort")
    if type(window["accepted_inventory_complete"]) is not bool:
        raise ValueError("accepted_inventory_complete must be true or false")

    missing_canaries = window["canary_expected"] - window["canary_reported"]
    observed_canary_failures = window["canary_reported"] - window["canary_success"]
    flags = []
    if not window["canary_expected"]:
        flags.append("no canary runs scheduled; no scripted journey evidence")
    if missing_canaries:
        flags.append("scheduled canary results missing")
    if observed_canary_failures:
        flags.append("canary failures observed; inspect steps and artifacts")
    if window["rum_error_sessions"]:
        flags.append("client errors observed in sampled sessions")
    if window["browser_visits"] and not window["rum_received"]:
        flags.append("browser visits recorded but no RUM sessions received")
    if not window["accepted_inventory_complete"]:
        flags.append("accepted-work inventory incomplete; backlog unknown")
    elif window["accepted"] > window["completed"]:
        flags.append("accepted work remains unfinished")

    return {
        "window": window["name"],
        "canary": f'{window["canary_success"]}/{window["canary_reported"]} reported runs succeeded; {missing_canaries} expected run results missing',
        "rum": (
            f'{window["rum_error_sessions"]}/{window["rum_received"]} received sessions reported a client error'
            if window["rum_received"] else "no sampled client sessions received; error rate unknown"
        ),
        "accepted_work": (
            f'{window["accepted"] - window["completed"]} accepted requests unfinished in stipulated complete inventory'
            if window["accepted_inventory_complete"] else "accepted-work backlog unknown; inventory completeness unverified"
        ),
        "flags": flags,
        "scope": "These counts describe separate fictional observations; none establishes success for every browser visit or root cause.",
    }


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("windows.json")
    windows = json.loads(path.read_text())
    print(json.dumps([inspect(window) for window in windows], indent=2))


if __name__ == "__main__":
    main()
