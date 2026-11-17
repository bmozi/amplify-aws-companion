import unittest

from note_boundary_lab import get, local_api


class NoteBoundaryTests(unittest.TestCase):
    def test_empty_list_can_hide_a_direct_read_leak(self):
        with local_api(enforce_owner=False) as base:
            status, listed = get(base, "/notes", "bob")
            self.assertEqual((status, listed), (200, {"items": []}))
            status, direct = get(base, "/notes/note-1", "bob")
            self.assertEqual(status, 200)
            self.assertEqual(direct["text"], "Alice's synthetic note")

    def test_server_owner_check_rejects_other_user_and_anonymous_read(self):
        with local_api(enforce_owner=True) as base:
            self.assertEqual(get(base, "/notes/note-1", "bob")[0], 403)
            self.assertEqual(get(base, "/notes/note-1")[0], 401)
            status, own = get(base, "/notes/note-1", "alice")
            self.assertEqual((status, own["owner"]), (200, "alice"))
            self.assertEqual(get(base, "/notes/unknown", "alice")[0], 404)

    def test_fixture_actor_header_is_not_authentication(self):
        with local_api(enforce_owner=True) as base:
            # Nothing in this local fixture proves who sent the claimed header.
            self.assertEqual(get(base, "/notes/note-1", "alice")[0], 200)
            self.assertEqual(get(base, "/notes/note-1", "bob")[0], 403)

    def test_denied_and_unknown_ids_reveal_different_fixture_responses(self):
        with local_api(enforce_owner=True) as base:
            self.assertEqual(get(base, "/notes/note-1", "bob"),
                             (403, {"error": "owner check denied"}))
            self.assertEqual(get(base, "/notes/not-a-note", "bob"),
                             (404, {"error": "unknown note"}))

    def test_matching_response_preserves_owner_access_but_not_identity(self):
        with local_api(enforce_owner=True, conceal_existence=True) as base:
            forbidden = get(base, "/notes/note-1", "bob")
            missing = get(base, "/notes/not-a-note", "bob")
            self.assertEqual(forbidden, (404, {"error": "unknown note"}))
            self.assertEqual(forbidden, missing)
            self.assertEqual(get(base, "/notes/note-1", "alice")[0], 200)
            self.assertEqual(get(base, "/notes/note-1")[0], 401)
            # Anyone can forge this fixture's Alice label.
            self.assertEqual(get(base, "/notes/note-1", "alice")[1]["owner"], "alice")

    def test_concealment_cannot_be_enabled_without_owner_check(self):
        with self.assertRaisesRegex(ValueError, "requires the owner check"):
            with local_api(enforce_owner=False, conceal_existence=True):
                pass


if __name__ == "__main__":
    unittest.main()
