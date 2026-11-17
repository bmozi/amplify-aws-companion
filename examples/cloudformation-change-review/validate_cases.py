"""Run installed cfn-lint and cfn-guard locally on the six fictional cases.

No credentials, AWS service call, stack or resource is involved. Install tools
separately from their official sources; this script never downloads packages.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from export_cases import export_cases


RULES = Path(__file__).with_name("archive-study.guard")


def installed_tool(value: str | None, default_name: str) -> str:
    tool = value or shutil.which(default_name)
    if not tool or not Path(tool).is_file():
        raise SystemExit(f"{default_name} is unavailable; install it separately or pass its executable path")
    return tool


def run_cases(lint: str, guard: str, region: str) -> dict:
    if not RULES.is_file():
        raise SystemExit("The project-specific Guard rules are missing")
    report = {
        "cfn_lint_version": subprocess.check_output([lint, "--version"], text=True).strip(),
        "cfn_guard_version": subprocess.check_output([guard, "--version"], text=True).strip(),
        "region_for_schema": region,
        "rules_sha256": sha256(RULES.read_bytes()).hexdigest(),
        "cases": {},
        "scope": "Local schema and authored policy rules only; no AWS stack, effective access or customer result",
    }
    with tempfile.TemporaryDirectory(prefix="cloudformation-change-cases-") as scratch:
        for path in export_cases(Path(scratch) / "cases"):
            template_hash = sha256(path.read_bytes()).hexdigest()
            lint_run = subprocess.run(
                [lint, "--format", "json", "--regions", region, "-t", str(path)],
                capture_output=True, text=True, timeout=120,
            )
            guard_run = subprocess.run(
                [guard, "validate", "--rules", str(RULES), "--data", str(path),
                 "--output-format", "json", "--show-summary", "none", "--structured"],
                capture_output=True, text=True, timeout=120,
            )
            try:
                lint_findings = json.loads(lint_run.stdout or "[]")
                guard_reports = json.loads(guard_run.stdout)
            except json.JSONDecodeError as error:
                raise SystemExit(f"A validator did not return structured JSON for {path.name}") from error
            if not isinstance(lint_findings, list) or not isinstance(guard_reports, list) or len(guard_reports) != 1:
                raise SystemExit(f"Unexpected validator report shape for {path.name}")
            guard_report = guard_reports[0]
            if guard_report.get("status") not in {"PASS", "FAIL"}:
                raise SystemExit(f"Guard did not evaluate {path.name}")
            if lint_run.stderr or guard_run.stderr:
                raise SystemExit(f"Validator diagnostic on stderr for {path.name}: {lint_run.stderr} {guard_run.stderr}")
            report["cases"][path.stem] = {
                "template_sha256": template_hash,
                "cfn_lint_exit": lint_run.returncode,
                "cfn_lint_findings": lint_findings,
                "cfn_guard_exit": guard_run.returncode,
                "cfn_guard_status": guard_report["status"],
                "cfn_guard_failed_rules": [item["Rule"]["name"] for item in guard_report["not_compliant"]],
            }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cfn-lint", help="Path to an installed cfn-lint executable")
    parser.add_argument("--cfn-guard", help="Path to an installed cfn-guard executable")
    parser.add_argument("--region", default="us-east-2", help="Schema region for this fictional study")
    parser.add_argument("--out", type=Path, help="Optional JSON evidence output")
    args = parser.parse_args()
    result = run_cases(installed_tool(args.cfn_lint, "cfn-lint"),
                       installed_tool(args.cfn_guard, "cfn-guard"), args.region)
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        if args.out.exists():
            parser.error("Refusing to overwrite an existing validation report")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    for case, item in result["cases"].items():
        rules = ",".join(item["cfn_guard_failed_rules"]) or "none"
        ids = ",".join(finding["Rule"]["Id"] for finding in item["cfn_lint_findings"]) or "none"
        print(f"{case}: cfn-lint={ids}; cfn-guard={item['cfn_guard_status']} ({rules})")
    if args.out:
        print(f"Report: {args.out}")


if __name__ == "__main__":
    main()
