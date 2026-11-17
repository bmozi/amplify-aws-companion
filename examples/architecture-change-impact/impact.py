"""Create a review worklist from authored requirement-to-decision links; no AWS calls."""

import argparse
from collections import deque
import json
from pathlib import Path

CASES = Path(__file__).with_name("cases.json")
FOUNDATION_QUESTIONS = {
    "authority": "Who may act?",
    "entry_path": "Where does the request go?",
    "work": "What accepts, performs and retries the work?",
    "data": "Where does the authoritative data live?",
    "delivery": "How does the selected change reach customers?",
    "recovery": "How will trouble be detected and corrected?",
    "whole_cost": "What does the complete path cost and retain?",
}


def worklist(case):
    nodes = case["nodes"]
    start = case["start"]
    if not isinstance(nodes, dict) or not nodes or start not in nodes:
        raise ValueError("start must name an authored decision node")
    for name, node in nodes.items():
        if not all(isinstance(node.get(field), str) and node[field].strip()
                   for field in ("question", "rejecting_observation")):
            raise ValueError(f"incomplete decision prompt: {name}")
        if not isinstance(node.get("leads_to"), list) or len(node["leads_to"]) != len(set(node["leads_to"])):
            raise ValueError(f"invalid dependency list: {name}")
        if any(next_name not in nodes for next_name in node["leads_to"]):
            raise ValueError(f"unknown dependency: {name}")
    paths = {start: [start]}
    pending = deque([start])
    while pending:
        current = pending.popleft()
        for next_name in nodes[current]["leads_to"]:
            if next_name not in paths:
                paths[next_name] = paths[current] + [next_name]
                pending.append(next_name)
    if set(paths) != set(nodes):
        raise ValueError("authored nodes must be reachable from the changed fact")
    return [{"decision_id": name, "path_from_change": path,
             "question": nodes[name]["question"],
             "rejecting_observation": nodes[name]["rejecting_observation"]}
            for name, path in paths.items()]


def review_foundations(case, rows):
    """Check a separately authored seven-question map, not design correctness."""
    mapping = case.get("foundation_review")
    if not isinstance(mapping, dict) or set(mapping) != set(FOUNDATION_QUESTIONS):
        raise ValueError("foundation review needs exactly the seven shared questions")
    reachable = {row["decision_id"] for row in rows}
    result = []
    for key, question in FOUNDATION_QUESTIONS.items():
        names = mapping[key]
        if (not isinstance(names, list) or not names
                or any(not isinstance(name, str) or not name for name in names)
                or len(names) != len(set(names))):
            raise ValueError(f"foundation {key} needs distinct authored nodes")
        if any(name not in reachable for name in names):
            raise ValueError(f"foundation {key} names a missing or unreachable decision")
        result.append({"foundation": key, "shared_question": question,
                       "authored_decisions": names})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", help="One of the authored case IDs")
    args = parser.parse_args()
    cases = json.loads(CASES.read_text())
    if args.case not in cases:
        parser.error("choose one of: " + ", ".join(sorted(cases)))
    case = cases[args.case]
    try:
        items = worklist(case)
        foundations = review_foundations(case, items)
    except (KeyError, TypeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps({"case": args.case, "changed_fact": case["change"],
                      "review_worklist": items,
                      "foundation_review": foundations,
                      "limit": "Both the graph and foundation mapping were authored by people. Passing them does not discover an omitted business dependency, select an AWS service or prove the design."}, indent=2))


if __name__ == "__main__":
    main()
