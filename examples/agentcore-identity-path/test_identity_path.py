import unittest
from dataclasses import replace

from identity_path import decide, fixture


class IdentityPathTests(unittest.TestCase):
    def test_fictional_approved_path_is_only_candidate(self):
        call, token, state = fixture()
        self.assertEqual(decide(call, token, state, frozenset()),
                         (True, "local gates passed; provider action not performed"))

    def test_wrong_user_and_machine_credential_cannot_use_personal_calendar(self):
        call, token, state = fixture()
        self.assertFalse(decide(call, replace(token, user="Leo"), state, frozenset())[0])
        self.assertFalse(decide(call, replace(token, flow="M2M", user=None), state, frozenset())[0])

    def test_wrong_workload_provider_and_tool_are_separate_denials(self):
        call, token, state = fixture()
        for changed in (replace(call, workload="catalog-agent"),
                        replace(call, provider="supplier-key"),
                        replace(call, tool="export_all_calendars")):
            self.assertFalse(decide(changed, token, state, frozenset())[0])

    def test_revoked_grant_or_downstream_token_fails(self):
        call, token, state = fixture()
        self.assertEqual(decide(call, token, replace(state, grant_active=False), frozenset())[1],
                         "current repair grant absent")
        self.assertEqual(decide(call, replace(token, downstream_accepts=False), state, frozenset())[1],
                         "downstream provider rejected token")

    def test_expanded_scope_does_not_grant_resource_or_replay(self):
        call, token, state = fixture()
        broad = replace(token, scopes=frozenset({"calendar.write", "calendar.read"}))
        self.assertFalse(decide(replace(call, repair="repair-99"), broad, state, frozenset())[0])
        self.assertEqual(decide(call, broad, state, frozenset({"op-17"}))[1],
                         "operation already completed; reconcile before retry")


if __name__ == "__main__":
    unittest.main()
