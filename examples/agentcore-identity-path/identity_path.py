"""Fictional, offline agent credential and action-path review; no AWS calls."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Proposal:
    caller: str
    workload: str
    provider: str
    tool: str
    repair: str
    operation: str


@dataclass(frozen=True)
class Credential:
    flow: str  # 3LO user delegation or M2M autonomous credential
    user: str | None
    workload: str
    provider: str
    scopes: frozenset[str]
    downstream_accepts: bool


@dataclass(frozen=True)
class TrustedState:
    authenticated_caller: str
    allowed_workloads: frozenset[str]
    allowed_providers: frozenset[str]
    current_repair_owner: str
    current_repair: str
    approved_operation: str
    grant_active: bool


def decide(proposal: Proposal, credential: Credential, state: TrustedState,
           completed: frozenset[str]) -> tuple[bool, str]:
    """Check separate gates; a successful result is still only a local decision."""
    if proposal.caller != state.authenticated_caller:
        return False, "caller identity mismatch"
    if proposal.workload not in state.allowed_workloads:
        return False, "workload identity not allowed"
    if proposal.provider not in state.allowed_providers:
        return False, "credential provider not allowed"
    if credential.workload != proposal.workload or credential.provider != proposal.provider:
        return False, "credential bound to different workload or provider"
    if credential.flow != "3LO" or credential.user != proposal.caller:
        return False, "user-delegated credential for this caller required"
    if "calendar.write" not in credential.scopes:
        return False, "required downstream scope absent"
    if proposal.tool != "schedule_pickup":
        return False, "tool not allowed for this workflow"
    if not state.grant_active or proposal.repair != state.current_repair or state.current_repair_owner != proposal.caller:
        return False, "current repair grant absent"
    if proposal.operation != state.approved_operation:
        return False, "current operation approval absent"
    if proposal.operation in completed:
        return False, "operation already completed; reconcile before retry"
    if not credential.downstream_accepts:
        return False, "downstream provider rejected token"
    return True, "local gates passed; provider action not performed"


def fixture() -> tuple[Proposal, Credential, TrustedState]:
    proposal = Proposal("Maya", "repair-agent", "calendar-oauth", "schedule_pickup", "repair-17", "op-17")
    credential = Credential("3LO", "Maya", "repair-agent", "calendar-oauth",
                            frozenset({"calendar.write"}), True)
    state = TrustedState("Maya", frozenset({"repair-agent"}), frozenset({"calendar-oauth"}),
                         "Maya", "repair-17", "op-17", True)
    return proposal, credential, state


def demonstrate() -> None:
    proposal, credential, state = fixture()
    cases = (
        ("approved fixture", proposal, credential, state, frozenset()),
        ("Leo's token", proposal, replace(credential, user="Leo"), state, frozenset()),
        ("grant revoked", proposal, credential, replace(state, grant_active=False), frozenset()),
        ("provider revokes token", proposal, replace(credential, downstream_accepts=False), state, frozenset()),
        ("replayed booking", proposal, credential, state, frozenset({"op-17"})),
    )
    for name, call, token, trusted, done in cases:
        print(name, "→", decide(call, token, trusted, done))


if __name__ == "__main__":
    demonstrate()
