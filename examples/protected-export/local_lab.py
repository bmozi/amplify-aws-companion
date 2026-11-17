"""Cloud-free A15 export contract model; not an AWS policy evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


class ExportDenied(Exception):
    """The local export contract refuses the action."""


@dataclass(frozen=True)
class Candidate:
    key: str
    version: str
    payload: bytes
    digest: str


class ExportLedger:
    """Owner-held candidate/approval records and a separate supplier-copy shelf."""

    def __init__(self, approval_owner: str) -> None:
        if not approval_owner:
            raise ValueError("approval owner is required")
        self.approval_owner = approval_owner
        self.candidates: dict[tuple[str, str], Candidate] = {}
        self.approvals: dict[tuple[str, str], str] = {}
        self.withdrawn: set[tuple[str, str]] = set()
        self.supplier_copies: dict[tuple[str, str, str], bytes] = {}

    def stage(self, key: str, version: str, rows: list[dict]) -> Candidate:
        identity = (key, version)
        if not key or not version or identity in self.candidates:
            raise ValueError("key and version must be new, nonempty identifiers")
        if not rows:
            raise ValueError("export needs at least one row")
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"part_number", "quantity"}:
                raise ValueError("export row must contain only part_number and quantity")
            if not isinstance(row["part_number"], str) or not row["part_number"].strip():
                raise ValueError("part_number must be a nonempty string")
            if type(row["quantity"]) is not int or row["quantity"] < 1:
                raise ValueError("quantity must be a positive integer")
        payload = (json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n").encode()
        candidate = Candidate(key, version, payload, sha256(payload).hexdigest())
        self.candidates[identity] = candidate
        return candidate

    def approve(self, key: str, version: str, digest: str, supplier: str, actor: str) -> None:
        identity = (key, version)
        candidate = self.candidates.get(identity)
        if actor != self.approval_owner:
            raise ExportDenied("only the named fixture owner may approve")
        if candidate is None or digest != candidate.digest or not supplier or identity in self.withdrawn:
            raise ExportDenied("approval must bind an existing exact version and recipient")
        if identity in self.approvals:
            raise ExportDenied("an approved version cannot be silently reassigned")
        self.approvals[identity] = supplier

    def owner_read_for_supplier(self, key: str, version: str, supplier: str) -> bytes:
        identity = (key, version)
        if identity in self.withdrawn or self.approvals.get(identity) != supplier:
            raise ExportDenied("no current grant for this supplier and exact version")
        return self.candidates[identity].payload

    def deliver_copy(self, key: str, version: str, supplier: str) -> bytes:
        payload = self.owner_read_for_supplier(key, version, supplier)
        self.supplier_copies[(key, version, supplier)] = payload
        return payload

    def withdraw(self, key: str, version: str, actor: str) -> None:
        if actor != self.approval_owner:
            raise ExportDenied("only the named fixture owner may withdraw")
        identity = (key, version)
        if identity not in self.candidates:
            raise ExportDenied("unknown export version")
        self.withdrawn.add(identity)

    def supplier_copy(self, key: str, version: str, supplier: str) -> bytes:
        try:
            return self.supplier_copies[(key, version, supplier)]
        except KeyError as exc:
            raise ExportDenied("no copy on this supplier shelf") from exc


def run_demo() -> None:
    ledger = ExportLedger("Maya")
    v1 = ledger.stage("weekly-parts", "v1", [{"part_number": "P-7", "quantity": 2}])
    ledger.approve(v1.key, v1.version, v1.digest, "Supplier P", "Maya")
    print("Approved v1 digest:", v1.digest)

    v2 = ledger.stage("weekly-parts", "v2", [{"part_number": "P-7", "quantity": 3}])
    for label, action in [
        ("unapproved replacement", lambda: ledger.owner_read_for_supplier(v2.key, v2.version, "Supplier P")),
        ("different supplier", lambda: ledger.owner_read_for_supplier(v1.key, v1.version, "Supplier Q")),
    ]:
        try:
            action()
        except ExportDenied:
            print(label + ": denied")

    delivered = ledger.deliver_copy(v1.key, v1.version, "Supplier P")
    print("Approved v1 delivered bytes:", delivered.decode().strip())
    ledger.withdraw(v1.key, v1.version, "Maya")
    try:
        ledger.owner_read_for_supplier(v1.key, v1.version, "Supplier P")
    except ExportDenied:
        print("future owner read after withdrawal: denied")
    print("supplier-held copy after withdrawal: still present =",
          ledger.supplier_copy(v1.key, v1.version, "Supplier P") == delivered)


if __name__ == "__main__":
    run_demo()
