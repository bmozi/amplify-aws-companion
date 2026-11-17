"""Cloud-free SaaS entitlement and tenant-boundary decision exercise.

All actors, plans, times and usage are fictional. No payment or AWS API is called.
"""

import json
from pathlib import Path
import sqlite3
import tempfile


FEATURE_TIERS = {"read_note": {"standard", "premium"},
                 "premium_export": {"premium"}}


class Portal:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE tenants (
                tenant TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                active_until INTEGER NOT NULL,
                revision INTEGER NOT NULL,
                status TEXT NOT NULL
            );
            CREATE TABLE memberships (
                actor TEXT NOT NULL,
                tenant TEXT NOT NULL,
                active INTEGER NOT NULL,
                PRIMARY KEY (actor, tenant)
            );
            CREATE TABLE accepted_usage (
                tenant TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                feature TEXT NOT NULL,
                PRIMARY KEY (tenant, operation_id)
            );
        """)

    def seed(self):
        self.db.executemany("INSERT INTO tenants VALUES (?, ?, ?, ?, ?)", [
            ("shop-a", "premium", 100, 1, "active"),
            ("shop-b", "premium", 200, 1, "active"),
        ])
        self.db.executemany("INSERT INTO memberships VALUES (?, ?, 1)", [
            ("alice", "shop-a"), ("bob", "shop-b"),
        ])
        self.db.commit()

    def apply_change(self, tenant, revision, tier, active_until, status):
        if tier not in {"standard", "premium"} or status not in {"active", "closed"}:
            raise ValueError("Invalid fictional plan change")
        if not isinstance(revision, int) or revision < 1 or not isinstance(active_until, int):
            raise ValueError("Invalid revision or expiry")
        with self.db:
            row = self.db.execute(
                "SELECT tier, active_until, revision, status FROM tenants WHERE tenant=?",
                (tenant,)).fetchone()
            if row is None:
                raise ValueError("Unknown tenant")
            old_tier, old_until, old_revision, old_status = row
            if revision < old_revision:
                return "stale_ignored"
            if revision == old_revision:
                if (tier, active_until, status) == (old_tier, old_until, old_status):
                    return "duplicate_ignored"
                return "same_revision_conflict"
            if old_status == "closed" and status != "closed":
                return "closed_requires_new_onboarding_review"
            self.db.execute(
                "UPDATE tenants SET tier=?, active_until=?, revision=?, status=? WHERE tenant=?",
                (tier, active_until, revision, status, tenant))
            return "applied"

    def use(self, actor, requested_tenant, feature, operation_id, now):
        if feature not in FEATURE_TIERS or not operation_id or not isinstance(now, int):
            raise ValueError("Invalid fictional request")
        with self.db:
            member = self.db.execute(
                "SELECT active FROM memberships WHERE actor=? AND tenant=?",
                (actor, requested_tenant)).fetchone()
            if member != (1,):
                return "tenant_denied"
            tier, active_until, status = self.db.execute(
                "SELECT tier, active_until, status FROM tenants WHERE tenant=?",
                (requested_tenant,)).fetchone()
            if status != "active":
                return "tenant_closed"
            previous = self.db.execute(
                "SELECT feature FROM accepted_usage WHERE tenant=? AND operation_id=?",
                (requested_tenant, operation_id)).fetchone()
            if previous:
                return "same_operation" if previous[0] == feature else "operation_conflict"
            if now >= active_until:
                return "entitlement_expired"
            if tier not in FEATURE_TIERS[feature]:
                return "feature_denied"
            self.db.execute(
                "INSERT INTO accepted_usage VALUES (?, ?, ?)",
                (requested_tenant, operation_id, feature))
            return "accepted_locally"

    def usage_count(self, tenant):
        return self.db.execute(
            "SELECT COUNT(*) FROM accepted_usage WHERE tenant=?", (tenant,)).fetchone()[0]

    def close(self):
        self.db.close()


def demonstration():
    with tempfile.TemporaryDirectory(prefix="tenant-entitlement-") as folder:
        portal = Portal(Path(folder) / "portal.sqlite")
        try:
            portal.seed()
            observations = {
                "alice_before_expiry": portal.use("alice", "shop-a", "premium_export", "x1", 99),
                "alice_stale_premium_claim_after_expiry": portal.use(
                    "alice", "shop-a", "premium_export", "x2", 101),
                "bob_independent_tenant": portal.use("bob", "shop-b", "premium_export", "x1", 101),
                "forged_shop_b": portal.use("alice", "shop-b", "premium_export", "x3", 101),
                "shop_a_downgrade": portal.apply_change("shop-a", 3, "standard", 180, "active"),
                "delayed_old_plan": portal.apply_change("shop-a", 2, "premium", 180, "active"),
                "duplicate_downgrade": portal.apply_change("shop-a", 3, "standard", 180, "active"),
                "premium_after_downgrade": portal.use("alice", "shop-a", "premium_export", "x4", 110),
                "standard_read": portal.use("alice", "shop-a", "read_note", "x5", 110),
                "repeat_standard_read": portal.use("alice", "shop-a", "read_note", "x5", 110),
                "shop_a_closure": portal.apply_change("shop-a", 4, "standard", 180, "closed"),
                "read_after_closure": portal.use("alice", "shop-a", "read_note", "x6", 110),
                "shop_a_local_usage_receipts": portal.usage_count("shop-a"),
                "shop_b_local_usage_receipts": portal.usage_count("shop-b"),
            }
            assert observations == {
                "alice_before_expiry": "accepted_locally",
                "alice_stale_premium_claim_after_expiry": "entitlement_expired",
                "bob_independent_tenant": "accepted_locally",
                "forged_shop_b": "tenant_denied",
                "shop_a_downgrade": "applied",
                "delayed_old_plan": "stale_ignored",
                "duplicate_downgrade": "duplicate_ignored",
                "premium_after_downgrade": "feature_denied",
                "standard_read": "accepted_locally",
                "repeat_standard_read": "same_operation",
                "shop_a_closure": "applied",
                "read_after_closure": "tenant_closed",
                "shop_a_local_usage_receipts": 2,
                "shop_b_local_usage_receipts": 1,
            }
            return observations
        finally:
            portal.close()


if __name__ == "__main__":
    print(json.dumps({"observations": demonstration(),
                      "scope": "Synthetic membership and billing revisions in temporary SQLite; no payment provider, AWS identity, distributed worker, invoice or cloud spend"}, indent=2))
