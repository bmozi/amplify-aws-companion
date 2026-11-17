"""Compare normalized synthetic source and archive events, not AWS delivery."""

import json
import sys
from collections import Counter
from pathlib import Path

FIELDS = ("account", "region", "group", "event_id", "event_time", "result")
KEY = FIELDS[:4]


def load(path: Path) -> tuple[dict[tuple[str, ...], tuple[str, str]], Counter]:
    events = {}
    occurrences = Counter()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        record = json.loads(line)
        if set(record) != set(FIELDS) or not all(isinstance(record[field], str) and record[field] for field in FIELDS):
            raise ValueError(f"{path}:{number}: invalid normalized event")
        key = tuple(record[field] for field in KEY)
        value = (record["event_time"], record["result"])
        if key in events and events[key] != value:
            raise ValueError(f"{path}:{number}: conflicting copies of {key}")
        events[key] = value
        occurrences[key] += 1
    return events, occurrences


def compare(source: Path, archive: Path) -> tuple[list[str], int]:
    old, old_counts = load(source)
    new, new_counts = load(archive)
    if any(count > 1 for count in old_counts.values()):
        raise ValueError("source fixture has duplicate event identities")
    errors = []
    for key in sorted(old.keys() | new.keys()):
        if key not in new:
            errors.append(f"missing archived event {key[-1]}")
        elif key not in old:
            errors.append(f"unexpected archived event {key[-1]}")
        elif old[key] != new[key]:
            errors.append(f"changed event for {key[-1]}: {old[key]} → {new[key]}")
    duplicates = sum(count - 1 for count in new_counts.values())
    return errors, duplicates


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: audit.py source.jsonl archive.jsonl", file=sys.stderr)
        return 2
    try:
        errors, duplicates = compare(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(exc, file=sys.stderr)
        return 2
    if errors:
        print(f"FAIL: archive coverage differs; duplicate copies observed: {duplicates}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"MATCH: synthetic event coverage; duplicate copies observed: {duplicates}; AWS delivery untested")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
