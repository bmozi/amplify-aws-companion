import sqlite3
import tempfile
import unittest
from pathlib import Path

from external_effect_lab import initialize, prepare, publish, reconcile
from two_reviewer_lab import admit, digest, review
from visitor_path import (DESTINATION, NEW, OLD, action, initialize_site, promote, run)


class VisitorPathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.local, self.provider, self.site = (root / name for name in ("local.db", "provider.db", "site.db"))
        self.proposed = action()
        initialize(self.local, self.provider, self.proposed)
        initialize_site(self.site)

    def approved(self):
        for actor in ("A", "B"):
            self.assertEqual(review(self.local, self.proposed["id"], actor,
                                    digest(self.proposed), 10, 100), "reviewed")
        self.assertEqual(admit(self.local, self.proposed["id"], 20), "admitted")
        return prepare(self.local, self.proposed)

    def test_http_visitor_remains_stale_until_separate_promotion(self):
        result = run()
        self.assertEqual(result["after_provider_commit"], OLD.decode().strip())
        self.assertEqual(result["pre_reconciliation_promotion"], "NO_GO_UNCONFIRMED")
        self.assertEqual(result["visitor_after_promotion"], NEW.decode().strip())
        self.assertEqual(result["wrong_destination_http"], 404)

    def test_wrong_content_or_target_cannot_use_approved_receipt(self):
        operation = self.approved()
        publish(self.provider, operation, self.proposed)
        self.assertEqual(reconcile(self.local, self.provider, operation), "confirmed")
        self.assertEqual(promote(self.local, self.provider, self.site, self.proposed, b"wrong"),
                         "NO_GO_CONTENT_OR_TARGET")
        self.assertEqual(promote(self.local, self.provider, self.site,
                                 {**self.proposed, "destination": "public-site"}, NEW),
                         "NO_GO_CONTENT_OR_TARGET")
        with sqlite3.connect(self.site) as db:
            self.assertEqual(db.execute("SELECT body FROM current WHERE destination=?",
                                        (DESTINATION,)).fetchone()[0], OLD)

    def test_changed_provider_receipt_stops_promotion(self):
        operation = self.approved()
        publish(self.provider, operation, self.proposed)
        self.assertEqual(reconcile(self.local, self.provider, operation), "confirmed")
        with sqlite3.connect(self.provider) as db:
            db.execute("UPDATE effects SET artifact='other' WHERE operation=?", (operation,))
        self.assertEqual(promote(self.local, self.provider, self.site, self.proposed, NEW),
                         "NO_GO_PROVIDER_MISMATCH")


if __name__ == "__main__":
    unittest.main()
