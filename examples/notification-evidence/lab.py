"""Classify fictional push observations without claiming real delivery."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ALLOWED = {
    "requested": {"aws_accepted"},
    "aws_accepted": {"provider_accepted", "provider_rejected"},
    "provider_accepted": set(),
    "provider_rejected": set(),
}

CLAIMS = {
    "requested": "A send was requested; AWS acceptance is unknown.",
    "aws_accepted": "AWS accepted the request; provider delivery is unknown.",
    "provider_accepted": "The push provider accepted the message; a person reading it is unproved.",
    "provider_rejected": "The push provider rejected the message; delivery must not be claimed.",
}


def evaluate(case: dict) -> dict:
    """Return a bounded claim for one fictional message, or reject bad evidence."""
    if not isinstance(case, dict):
        raise ValueError("Each case must be an object")
    message_id = case.get("message_id")
    recipient_id = case.get("recipient_id")
    if not isinstance(message_id, str) or not message_id or not isinstance(recipient_id, str) or not recipient_id:
        raise ValueError("A nonempty message_id and recipient_id are required")
    if type(case.get("consent")) is not bool or type(case.get("device_registered")) is not bool:
        raise ValueError("Consent and device_registered must be booleans")
    if type(case.get("app_open_recorded")) is not bool:
        raise ValueError("app_open_recorded must be a boolean independent of the send trail")
    events = case.get("events")
    if not isinstance(events, list):
        raise ValueError("events must be a list")

    app_open = case["app_open_recorded"]
    if not case["consent"] or not case["device_registered"]:
        if events:
            raise ValueError("A send trail after missing consent or device registration needs investigation")
        reason = "consent missing" if not case["consent"] else "device not registered"
        result = {"message_id": message_id, "state": "blocked", "claim": f"Do not send: {reason}."}
        return with_app_observation(result, app_open)

    previous = None
    for event in events:
        if not isinstance(event, dict) or event.get("message_id") != message_id or event.get("recipient_id") != recipient_id:
            raise ValueError("An event lacks matching message and recipient IDs")
        kind = event.get("kind")
        if previous is None:
            if kind != "requested":
                raise ValueError("The trail must start with a requested event")
        elif kind not in ALLOWED[previous]:
            raise ValueError(f"Invalid or contradictory event after {previous}: {kind}")
        previous = kind

    if previous is None:
        result = {"message_id": message_id, "state": "ready", "claim": "Eligible in this fixture; no send is observed."}
    else:
        result = {"message_id": message_id, "state": previous, "claim": CLAIMS[previous]}
    return with_app_observation(result, app_open)


def with_app_observation(result: dict, app_open: bool) -> dict:
    result["app_open_recorded"] = app_open
    if app_open:
        result["claim"] += " The app also opened; no causal link or notification read is proved."
    return result


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python3 lab.py CASE.json", file=sys.stderr)
        return 2
    try:
        cases = json.loads(Path(argv[1]).read_text())
        if not isinstance(cases, list):
            raise ValueError("The input must be a list of cases")
        for case in cases:
            print(json.dumps(evaluate(case), sort_keys=True))
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
        print(f"Evidence rejected: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
