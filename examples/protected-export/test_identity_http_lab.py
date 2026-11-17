import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from identity_http_lab import export_server, fetch, post
from persistent_lab import OwnerLedger, SupplierShelf
from local_lab import ExportDenied


class IdentityHTTPTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.owner = OwnerLedger(root / "owner.sqlite")
        self.shelf = SupplierShelf(root / "supplier.sqlite")
        self.c = self.owner.stage("weekly-parts", "v1", [{"part_number": "P-7", "quantity": 2}])
        self.server = export_server(self.owner)
        self.url, self.owner_token, self.supplier_token, self.other_supplier_token = self.server.__enter__()
        self.approval = {"key": self.c.key, "version": self.c.version,
                         "digest": self.c.digest, "supplier": "Supplier P"}

    def tearDown(self):
        self.server.__exit__(None, None, None)
        self.temp.cleanup()

    def status(self, token, body):
        with self.assertRaises(HTTPError) as caught:
            post(self.url, "/approve", token, body)
        return caught.exception.code

    def test_body_name_cannot_turn_supplier_into_owner(self):
        self.assertEqual(self.status(self.supplier_token, {**self.approval, "actor": "Maya"}), 403)
        self.assertEqual(self.status("unrecognized", self.approval), 401)
        self.assertEqual(self.status(self.owner_token, {**self.approval, "actor": "Maya"}), 400)
        self.assertEqual(post(self.url, "/approve", self.owner_token, self.approval)["result"],
                         "approved")
        with self.assertRaises(HTTPError) as caught:
            post(self.url, "/withdraw", self.supplier_token,
                 {"key": self.c.key, "version": self.c.version, "actor": "Maya"})
        self.assertEqual(caught.exception.code, 403)

    def test_exact_version_delivery_and_withdrawal(self):
        post(self.url, "/approve", self.owner_token, self.approval)
        v2 = self.owner.stage(self.c.key, "v2", [{"part_number": "P-7", "quantity": 3}])
        with self.assertRaises(HTTPError) as caught:
            fetch(self.url, self.supplier_token, v2.key, v2.version)
        self.assertEqual(caught.exception.code, 403)
        with self.assertRaises(HTTPError) as caught:
            fetch(self.url, self.owner_token, self.c.key, self.c.version)
        self.assertEqual(caught.exception.code, 403)
        with self.assertRaises(HTTPError) as caught:
            fetch(self.url, self.other_supplier_token, self.c.key, self.c.version)
        self.assertEqual(caught.exception.code, 403)
        payload, digest = fetch(self.url, self.supplier_token, self.c.key, self.c.version)
        self.shelf.accept_bytes(self.c.key, self.c.version, "Supplier P", payload, digest)
        post(self.url, "/withdraw", self.owner_token,
             {"key": self.c.key, "version": self.c.version})
        with self.assertRaises(HTTPError) as caught:
            fetch(self.url, self.supplier_token, self.c.key, self.c.version)
        self.assertEqual(caught.exception.code, 403)
        self.assertEqual(self.shelf.lookup(self.c.key, self.c.version, "Supplier P")[1], digest)

    def test_conflicting_approval_and_bad_received_bytes_fail(self):
        post(self.url, "/approve", self.owner_token, self.approval)
        self.assertEqual(self.status(self.owner_token, {**self.approval,
                                                       "supplier": "Supplier Q"}), 403)
        with self.assertRaises(ExportDenied):
            self.shelf.accept_bytes(self.c.key, self.c.version, "Supplier P", b"wrong", self.c.digest)

    def test_missing_version_and_unauthenticated_read_fail(self):
        request = Request(self.url + "/export?" + urlencode({"key": self.c.key}),
                          headers={"Authorization": f"Bearer {self.supplier_token}"})
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 400)
        request = Request(self.url + "/export?" + urlencode({"key": self.c.key,
                                                              "version": self.c.version}))
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 401)


if __name__ == "__main__":
    unittest.main()
