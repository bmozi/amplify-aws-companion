"""Meaningful boundary and replay checks for the local agent-tool gate."""

import unittest
from unittest.mock import patch

from lab import JOBS, State, decide


def credit(**changes):
    value = {"tool": "issue_credit", "job": "repair-17", "amount_cents": 1200,
             "approval_id": "approval-17", "operation_id": "op-17"}
    value.update(changes)
    return value


def valid_state(**changes):
    return State(intents={"op-17": ("maya", "issue_credit", "repair-17", 1200)}, **changes)


class GateTests(unittest.TestCase):
    def test_authorized_read_does_not_create_credit(self):
        state = State()
        self.assertEqual(decide("lee", {"tool": "read_policy", "document": "policy-a"}, state)[0], "allow")
        self.assertEqual(state.credits, {})

    def test_cross_tenant_and_untrusted_tool_are_denied(self):
        state = State()
        self.assertEqual(decide("maya", {"tool": "read_policy", "document": "policy-b"}, state)[0], "deny")
        self.assertEqual(decide("maya", {"tool": "export_all_customer_records"}, state)[0], "deny")

    def test_proposal_cannot_choose_caller_or_approval_contents(self):
        state = State()
        self.assertEqual(decide("lee", credit(actor="maya"), state)[0], "deny")
        self.assertEqual(decide("maya", credit(approval={"actor": "maya", "expires_at": 999}), state)[0], "deny")
        self.assertEqual(decide("bob", credit(), state)[0], "deny")
        self.assertEqual(state.credits, {})

    def test_approval_binds_amount_revision_and_expiry(self):
        for proposal, now in [(credit(amount_cents=1300), 100), (credit(), 200),
                              (credit(approval_id="missing"), 100)]:
            self.assertEqual(decide("maya", proposal, valid_state(), now)[0], "deny")
        with patch.dict(JOBS, {"repair-17": {"tenant": "shop-a", "revision": 5}}):
            self.assertEqual(decide("maya", credit(), valid_state())[1], "approval_not_current_or_exact")

    def test_approval_alone_cannot_start_an_unrequested_action(self):
        state = State()
        self.assertEqual(decide("maya", credit(), state), ("deny", "no_matching_trusted_intent"))
        self.assertEqual(state.credits, {})
        state.intents["op-17"] = ("maya", "issue_credit", "repair-17", 1300)
        self.assertEqual(decide("maya", credit(), state)[1], "no_matching_trusted_intent")
        self.assertEqual(state.credits, {})

    def test_amount_type_and_bound_are_checked(self):
        for amount in (True, 0, 5001, "1200"):
            self.assertEqual(decide("maya", credit(amount_cents=amount), State())[0], "deny")

    def test_malformed_model_values_fail_closed_without_effect(self):
        state = State()
        proposals = [
            {"tool": "read_policy", "document": ["policy-a"]},
            credit(job=["repair-17"]),
            credit(approval_id=["approval-17"]),
            credit(operation_id=["op-17"]),
        ]
        for proposal in proposals:
            self.assertEqual(decide("maya", proposal, state)[0], "deny")
        self.assertEqual(state.credits, {})

    def test_same_operation_replays_and_changed_intent_conflicts(self):
        state = valid_state()
        self.assertEqual(decide("maya", credit(), state)[0], "allow")
        self.assertEqual(decide("maya", credit(), state)[0], "replay")
        self.assertEqual(decide("maya", credit(), state, now=200)[0], "replay")
        self.assertEqual(decide("maya", credit(amount_cents=1300), state)[1], "operation_conflict")
        self.assertEqual(len(state.credits), 1)

    def test_local_limit_blocks_new_work(self):
        state = valid_state(max_new_credits=1)
        state.intents["op-18"] = ("maya", "issue_credit", "repair-17", 1200)
        self.assertEqual(decide("maya", credit(), state)[0], "allow")
        self.assertEqual(decide("maya", credit(operation_id="op-18"), state)[1], "local_action_limit")
        self.assertEqual(decide("maya", credit(), state)[0], "replay")


if __name__ == "__main__":
    unittest.main()
