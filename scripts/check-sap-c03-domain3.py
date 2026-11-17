"""Check the SAP-C03 Domain 3 editorial map against the official source inventory."""

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "curriculum/SAP-C03-DOMAIN-3-EVIDENCE.md"
RECEIPT = ROOT / "curriculum/source-rechecks/2026-10-27-sap-c03.json"
SOURCE = ROOT / "artifacts/sap-c03-source-2026-10-27/solutions-architect-professional-03-domain3.md"


def main() -> None:
    text = MAP.read_text()
    receipt = json.loads(RECEIPT.read_text())
    expected = {f"3.{task}.{number}" for task, count in enumerate((4, 5, 5, 5), 1)
                for number in range(1, count + 1)}
    if receipt["numbered_skill_counts"][2] != len(expected):
        raise ValueError("Editorial skill count differs from the AWS source receipt")
    rows = re.findall(r"^\| (3\.\d+\.\d+) ([^\n]+)$", text, re.MULTILINE)
    ids = [skill for skill, _ in rows]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError(f"Domain 3 skill mismatch: missing={sorted(expected - set(ids))}, extra={sorted(set(ids) - expected)}")
    statuses = ["partial" if "**Partial." in row else "gap" if "**Gap." in row else "unclassified"
                for _, row in rows]
    if statuses.count("partial") != 19 or statuses.count("gap") != 0:
        raise ValueError(f"Unexpected Domain 3 judgment counts: {statuses.count('partial')} partial, {statuses.count('gap')} gaps")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("https://", "http://", "#")):
            continue
        path = target.split("#", 1)[0]
        if path and not (MAP.parent / path).is_file():
            raise ValueError(f"Missing linked teaching file: {target}")
    if SOURCE.is_file():
        if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != receipt["sha256"][SOURCE.name]:
            raise ValueError("Retained AWS guide bytes differ from the source receipt")
        official = set(re.findall(r"^\+ Skill (3\.\d+\.\d+):", SOURCE.read_text(), re.MULTILINE))
        if official != expected:
            raise ValueError("Editorial IDs differ from the retained official guide")
    print("SAP-C03 Domain 3: 19 unique source skills, 19 partial and 0 gaps; local links resolve")


if __name__ == "__main__":
    main()
