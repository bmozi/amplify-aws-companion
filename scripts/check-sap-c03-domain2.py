"""Check that the SAP-C03 Domain 2 editorial map is complete and navigable."""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "curriculum/SAP-C03-DOMAIN-2-EVIDENCE.md"
RECEIPT = ROOT / "curriculum/source-rechecks/2026-10-27-sap-c03.json"
SOURCE = ROOT / "artifacts/sap-c03-source-2026-10-27/solutions-architect-professional-03-domain2.md"


def main() -> None:
    text = MAP.read_text()
    receipt = json.loads(RECEIPT.read_text())
    expected = {f"2.{task}.{number}" for task, count in enumerate((5, 4, 6, 6, 3), 1)
                for number in range(1, count + 1)}
    if receipt["numbered_skill_counts"][1] != len(expected):
        raise ValueError("Editorial skill count differs from the AWS source receipt")
    rows = re.findall(r"^\| (2\.\d+\.\d+) ([^\n]+)$", text, re.MULTILINE)
    ids = [skill for skill, _ in rows]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError(f"Domain 2 skill mismatch: missing={sorted(expected - set(ids))}, extra={sorted(set(ids) - expected)}")
    statuses = ["partial" if "**Partial." in row else "gap" if "**Gap." in row else "unclassified"
                for _, row in rows]
    if statuses.count("partial") != 24 or statuses.count("gap") != 0:
        raise ValueError(f"Unexpected Domain 2 judgment counts: {statuses.count('partial')} partial, {statuses.count('gap')} gaps")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("https://", "http://", "#")):
            continue
        path = target.split("#", 1)[0]
        if path and not (MAP.parent / path).is_file():
            raise ValueError(f"Missing linked teaching file: {target}")
    if SOURCE.is_file():
        digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        if digest != receipt["sha256"][SOURCE.name]:
            raise ValueError("Locally retained AWS guide bytes differ from the source receipt")
        official = set(re.findall(r"^\+ Skill (2\.\d+\.\d+):", SOURCE.read_text(), re.MULTILINE))
        if official != expected:
            raise ValueError("Editorial IDs differ from the retained official guide")
    print("SAP-C03 Domain 2: 24 unique source skills, 24 partial and 0 gaps; local links resolve")


if __name__ == "__main__":
    main()
