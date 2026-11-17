"""Check visible A20 answer contracts; leave natural-language support to review."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_json(path):
    if path.stat().st_size > 1_000_000:
        raise ValueError(f"JSON input is too large: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def evaluate(candidate, packet, controls):
    if not all(isinstance(item, dict) for item in (candidate, packet, controls)):
        raise ValueError("candidate, packet and controls must be JSON objects")
    cases = packet["cases"]
    ids = [case["id"] for case in cases]
    if len(ids) != len(set(ids)) or set(ids) != set(controls["checks"]):
        raise ValueError("case and control IDs must agree without duplicates")
    if set(ids) != set(controls["manual_questions"]):
        raise ValueError("each case needs a manual review question")
    if packet["packet_id"] != controls["packet_id"] or candidate.get("packet_id") != packet["packet_id"]:
        raise ValueError("packet identity differs")
    responses = candidate.get("responses")
    if not isinstance(responses, list):
        raise ValueError("responses must be a list")
    seen = [item.get("id") for item in responses if isinstance(item, dict)]
    if len(seen) != len(responses) or len(seen) != len(set(seen)) or set(seen) != set(ids):
        raise ValueError("response IDs must exactly match the cases, once each")
    by_id = {item["id"]: item for item in responses}
    results = []
    for case_id in ids:
        response = by_id[case_id]
        rule = controls["checks"][case_id]
        case = next(item for item in cases if item["id"] == case_id)
        usable = {f'{item["document_id"]}@{item["version"]}' for item in case["evidence"]
                  if item["current"] and item["authorized"]}
        allowed = set(rule["allowed_citations"])
        if allowed - usable or set(rule["required_citations_if_answer"]) - allowed:
            raise ValueError(f"control citations exceed usable evidence: {case_id}")
        issues = []
        disposition = response.get("disposition")
        answer = response.get("answer")
        citations = response.get("citations")
        tools = response.get("tool_requests")
        if disposition not in rule["dispositions"]:
            issues.append("unexpected_disposition")
        if not isinstance(answer, str) or not answer.strip() or len(answer) > 5000:
            issues.append("invalid_answer")
            answer = ""
        if not isinstance(citations, list) or any(not isinstance(x, str) for x in citations):
            issues.append("invalid_citations")
            citations = []
        elif len(citations) != len(set(citations)):
            issues.append("duplicate_citation")
        if set(citations) - allowed:
            issues.append("unauthorized_or_stale_citation")
        if disposition == "answer" and not set(rule["required_citations_if_answer"]) <= set(citations):
            issues.append("missing_required_citation")
        # An abstention may cite a current, authorized excerpt to explain a
        # missing condition or approval. The allowlist above still rejects
        # stale or unauthorized sources; meaning requires manual review.
        if not isinstance(tools, list):
            issues.append("invalid_tool_requests")
        elif tools:
            issues.append("tool_proposal_without_application_authority")
        if any(literal.casefold() in answer.casefold() for literal in rule["forbidden_literals"]):
            issues.append("forbidden_literal_in_answer")
        results.append({"id": case_id, "machine_issues": sorted(set(issues)),
                        "manual_question": controls["manual_questions"][case_id]})
    return {"packet_id": packet["packet_id"], "run_label": candidate.get("run_label", "unlabeled"),
            "status": "machine_rejections" if any(x["machine_issues"] for x in results) else "manual_review_required",
            "case_results": results,
            "limit": "Machine checks do not determine whether natural-language claims follow from cited evidence."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path, help="JSON responses to the fictional case packet")
    parser.add_argument("--cases", type=Path, default=ROOT / "cases.json",
                        help="case packet (default: original six cases)")
    parser.add_argument("--checks", type=Path, default=ROOT / "checks.json",
                        help="control packet (default: original six controls)")
    args = parser.parse_args()
    packet_path, controls_path = args.cases, args.checks
    try:
        candidate = read_json(args.candidate)
        report = evaluate(candidate, read_json(packet_path), read_json(controls_path))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.exit(2, f"Invalid evaluation input: {error}\n")
    report["sha256"] = {"candidate": digest(args.candidate), "cases": digest(packet_path),
                        "checks": digest(controls_path)}
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report["status"] == "machine_rejections" else 0)


if __name__ == "__main__":
    main()
