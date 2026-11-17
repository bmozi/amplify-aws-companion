"""Export the fictional CloudFormation cases for local third-party validation.

This writes JSON files only. It never calls AWS or runs a validator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from review import load_baseline, proposed_template


CASES = ("tag", "name", "public", "transport", "unknown")


def export_cases(destination: Path) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=False)
    templates = {"baseline": load_baseline()}
    templates.update({case: proposed_template(case) for case in CASES})
    paths = []
    for name, template in templates.items():
        path = destination / f"{name}.json"
        path.write_text(json.dumps(template, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths.append(path)
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="new directory for exported JSON templates")
    args = parser.parse_args()
    for path in export_cases(args.out):
        print(path)


if __name__ == "__main__":
    main()
