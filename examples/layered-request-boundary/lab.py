"""Small, cloud-free request-path model; deliberately not an AWS WAF emulator."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    caller: str
    owner: str
    suspicious: bool = False
    trusted_path: bool = False


def evaluate(request: Request, suspicious_action: str = "count", early_allow: bool = False,
             enforce_owner: bool = True):
    """Return the first terminal decision and the boundaries actually reached."""
    if suspicious_action not in {"count", "block"}:
        raise ValueError("action must be count or block")
    trace = []
    if early_allow and request.trusted_path:
        trace.append("early_allow")
    else:
        if request.suspicious:
            trace.append("matched_" + suspicious_action)
            if suspicious_action == "block":
                return "waf_block", trace
        trace.append("default_allow")
    trace.append("application")
    if enforce_owner and request.caller != request.owner:
        return "owner_denied", trace
    return "record_returned", trace


CASES = {
    "ordinary_owner": Request("alice", "alice"),
    "ordinary_other_owner": Request("alice", "bob"),
    "suspicious_owner": Request("alice", "alice", suspicious=True),
    "suspicious_other_owner": Request("alice", "bob", suspicious=True),
    "trusted_suspicious": Request("alice", "alice", suspicious=True, trusted_path=True),
}


if __name__ == "__main__":
    for name, request in CASES.items():
        for action, early_allow, owner_check in (("count", False, True),
                                                  ("block", False, True),
                                                  ("block", True, True),
                                                  ("count", False, False)):
            outcome, trace = evaluate(request, action, early_allow, owner_check)
            print(f"{name:25} action={action:5} early_allow={early_allow!s:5} "
                  f"owner_check={owner_check!s:5} -> {outcome:15} {' > '.join(trace)}")
