"""Keep the current teaching-gap queue aligned with the five editorial maps."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "curriculum"


def main():
    gaps = set()
    for domain in range(1, 6):
        text = (ROOT / f"SAP-C03-DOMAIN-{domain}-EVIDENCE.md").read_text()
        rows = re.findall(rf"^\| ({domain}\.\d+\.\d+) .*?\*\*Gap\.", text, re.MULTILINE)
        gaps.update(rows)
    queue = (ROOT / "SAP-C03-GAP-QUEUE.md").read_text()
    queued = re.findall(r"^\| (\d\.\d+\.\d+) ", queue, re.MULTILINE)
    if len(queued) != len(set(queued)) or set(queued) != gaps:
        raise ValueError(f"Gap queue differs: missing={sorted(gaps - set(queued))}, extra={sorted(set(queued) - gaps)}")
    print(f"SAP-C03 teaching queue: {len(gaps)} unique gap skills agree with five domain maps")


if __name__ == "__main__":
    main()
