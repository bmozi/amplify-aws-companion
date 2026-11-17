"""Local application-side gate for fictional agent tool proposals; no model or AWS calls."""

from dataclasses import dataclass, field


ACTORS = {
    "maya": {"tenant": "shop-a", "documents": {"policy-a"}, "may_issue_credit": True},
    "lee": {"tenant": "shop-a", "documents": {"policy-a"}, "may_issue_credit": False},
    "bob": {"tenant": "shop-b", "documents": {"policy-b"}, "may_issue_credit": True},
}
DOCUMENTS = {"policy-a": "shop-a", "policy-b": "shop-b"}
JOBS = {
    "repair-17": {"tenant": "shop-a", "revision": 4},
    "repair-28": {"tenant": "shop-b", "revision": 2},
}
APPROVALS = {
    "approval-17": {
        "actor": "maya", "tool": "issue_credit", "job": "repair-17",
        "amount_cents": 1200, "revision": 4, "expires_at": 200,
    },
}


@dataclass
class State:
    # One state object represents a fictional, single-process application boundary.
    credits: dict[str, tuple] = field(default_factory=dict)
    # Current action intents come from the trusted application workflow, never
    # from a retrieved document or model proposal.
    intents: dict[str, tuple[str, str, str, int]] = field(default_factory=dict)
    max_new_credits: int = 2


def decide(actor_id: str, proposal: dict, state: State, now: int = 100) -> tuple[str, str]:
    """Evaluate a proposal using server-owned identity, records and approval fixtures."""
    if not isinstance(actor_id, str) or not isinstance(proposal, dict):
        return "deny", "unknown_actor_or_request"
    actor = ACTORS.get(actor_id)
    if actor is None:
        return "deny", "unknown_actor_or_request"
    tool = proposal.get("tool")
    if tool == "read_policy":
        if set(proposal) != {"tool", "document"}:
            return "deny", "unexpected_fields"
        document = proposal.get("document")
        if not isinstance(document, str):
            return "deny", "invalid_document"
        if document not in actor["documents"] or DOCUMENTS.get(document) != actor["tenant"]:
            return "deny", "document_not_authorized"
        return "allow", "authorized_read_only"
    if tool != "issue_credit":
        return "deny", "tool_not_allowlisted"
    if set(proposal) != {"tool", "job", "amount_cents", "approval_id", "operation_id"}:
        return "deny", "unexpected_fields"
    job_id = proposal.get("job")
    if not isinstance(job_id, str):
        return "deny", "invalid_job"
    job = JOBS.get(job_id)
    if job is None or job["tenant"] != actor["tenant"] or not actor["may_issue_credit"]:
        return "deny", "job_or_actor_not_authorized"
    amount = proposal.get("amount_cents")
    if type(amount) is not int or not 0 < amount <= 5000:
        return "deny", "amount_out_of_bounds"
    approval_id = proposal.get("approval_id")
    if not isinstance(approval_id, str):
        return "deny", "invalid_approval_id"
    operation_id = proposal.get("operation_id")
    if not isinstance(operation_id, str) or not operation_id or len(operation_id) > 64:
        return "deny", "invalid_operation_id"
    previous = state.credits.get(operation_id)
    if previous is not None:
        # A receipt for already-recorded work remains discoverable after approval
        # expiry. This path does not perform the action again.
        original = previous[:4]
        requested = (actor_id, job_id, amount, approval_id)
        return ("replay", "same_operation") if original == requested else ("deny", "operation_conflict")
    if state.intents.get(operation_id) != (actor_id, tool, job_id, amount):
        return "deny", "no_matching_trusted_intent"
    approval = APPROVALS.get(approval_id)
    if approval is None or any((
        approval["actor"] != actor_id,
        approval["tool"] != tool,
        approval["job"] != job_id,
        approval["amount_cents"] != amount,
        approval["revision"] != job["revision"],
        now >= approval["expires_at"],
    )):
        return "deny", "approval_not_current_or_exact"
    if len(state.credits) >= state.max_new_credits:
        return "deny", "local_action_limit"
    intended = (actor_id, job_id, amount, approval_id, job["revision"])
    state.credits[operation_id] = intended
    return "allow", "fictional_credit_recorded"


def main() -> None:
    state = State(intents={"op-17": ("maya", "issue_credit", "repair-17", 1200)})
    cases = [
        ("maya", {"tool": "read_policy", "document": "policy-a"}),
        ("maya", {"tool": "read_policy", "document": "policy-b"}),
        ("maya", {"tool": "export_all_customer_records", "document": "policy-b"}),
        ("maya", {"tool": "issue_credit", "job": "repair-17", "amount_cents": 1200,
                  "approval_id": "approval-17", "operation_id": "op-17"}),
        ("maya", {"tool": "issue_credit", "job": "repair-17", "amount_cents": 1200,
                  "approval_id": "approval-17", "operation_id": "op-17"}),
    ]
    for actor, proposal in cases:
        print(f"{actor} {proposal['tool']}: {decide(actor, proposal, state)}")
    print(f"fictional committed credits: {len(state.credits)}")


if __name__ == "__main__":
    main()
