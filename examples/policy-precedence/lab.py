"""Fictional retrieval-to-business-rule handoff; no model, AWS or customer data."""

from datetime import date
from hashlib import sha256
import json
import sqlite3


GENERAL = "Household repair coverage is 45 days with a receipt."
BULLETIN = "Household repairs accepted from October 1 have 60 days with a receipt."
EXCLUSION = "Commercial repair equipment is excluded from this coverage."


def digest(text):
    return sha256(text.encode("utf-8")).hexdigest()


def setup():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE people(actor TEXT PRIMARY KEY, tenant TEXT NOT NULL, active INT NOT NULL);
        CREATE TABLE documents(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, version INT NOT NULL,
            body TEXT NOT NULL, retrieval_score REAL NOT NULL);
        CREATE TABLE grants(actor TEXT NOT NULL, document TEXT NOT NULL,
            PRIMARY KEY(actor, document));
        CREATE TABLE approved_rules(id TEXT PRIMARY KEY, tenant TEXT NOT NULL, document TEXT NOT NULL,
            source_version INT NOT NULL, source_digest TEXT NOT NULL,
            repair_kind TEXT NOT NULL, starts_on TEXT NOT NULL, days INT,
            priority INT NOT NULL, approved INT NOT NULL);
        INSERT INTO people VALUES ('alice','shop-a',1),('bob','shop-b',1);
    """)
    documents = [
        ("general", "shop-a", 1, GENERAL, 0.99),
        ("bulletin", "shop-a", 1, BULLETIN, 0.31),
        ("exclusion", "shop-a", 1, EXCLUSION, 0.20),
        ("other-shop", "shop-b", 1, "Commercial repairs have 365 days.", 1.00),
    ]
    db.executemany("INSERT INTO documents VALUES (?,?,?,?,?)", documents)
    db.executemany("INSERT INTO grants VALUES (?,?)",
                   [("alice", source) for source in ("general", "bulletin", "exclusion")]
                   + [("bob", "other-shop")])
    rules = [
        ("general-rule", "shop-a", "general", 1, digest(GENERAL), "household", "2026-01-01", 45, 1, 1),
        ("bulletin-rule", "shop-a", "bulletin", 1, digest(BULLETIN), "household", "2026-10-01", 60, 2, 1),
        ("commercial-rule", "shop-a", "exclusion", 1, digest(EXCLUSION), "commercial", "2026-01-01", None, 1, 1),
    ]
    db.executemany("INSERT INTO approved_rules VALUES (?,?,?,?,?,?,?,?,?,?)", rules)
    db.commit()
    return db


def discover(db, actor):
    """Simulate ranked retrieval over sources already permitted to the fixture actor."""
    return [dict(row) for row in db.execute("""
        SELECT d.id, d.retrieval_score FROM documents d
        JOIN people p ON p.tenant=d.tenant AND p.actor=? AND p.active=1
        JOIN grants g ON g.document=d.id AND g.actor=p.actor
        ORDER BY d.retrieval_score DESC, d.id
    """, (actor,))]


def decide(db, actor, repair_kind, accepted_on, has_receipt, candidates):
    """Use a trusted, manually approved rule catalog; scores never choose coverage."""
    person = db.execute("SELECT tenant FROM people WHERE actor=? AND active=1", (actor,)).fetchone()
    if person is None:
        return {"status": "deny", "reason": "unknown_or_inactive_actor"}
    if repair_kind not in ("household", "commercial") or type(has_receipt) is not bool:
        return {"status": "abstain", "reason": "missing_or_invalid_case_fact"}
    try:
        day = date.fromisoformat(accepted_on)
    except (TypeError, ValueError):
        return {"status": "abstain", "reason": "missing_or_invalid_acceptance_date"}
    if not isinstance(candidates, list) or any(not isinstance(c, dict) or not isinstance(c.get("id"), str)
                                               for c in candidates):
        return {"status": "abstain", "reason": "invalid_candidate_packet"}
    candidate_ids = {c["id"] for c in candidates}
    rules = db.execute("""
        SELECT * FROM approved_rules WHERE tenant=? AND repair_kind=? AND approved=1 AND starts_on<=?
        ORDER BY priority DESC, id
    """, (person["tenant"], repair_kind, day.isoformat())).fetchall()
    if not rules:
        return {"status": "abstain", "reason": "no_approved_applicable_rule"}
    # Every applicable approved rule must be represented and current. A missing
    # higher-priority bulletin must not silently fall back to the general rule.
    for rule in rules:
        if rule["document"] not in candidate_ids:
            return {"status": "abstain", "reason": "missing_applicable_source"}
        source = db.execute("""
            SELECT d.version,d.body FROM documents d
            JOIN grants g ON g.document=d.id AND g.actor=?
            WHERE d.id=? AND d.tenant=?
        """, (actor, rule["document"], person["tenant"])).fetchone()
        if source is None:
            return {"status": "abstain", "reason": "source_not_currently_authorized"}
        if source["version"] != rule["source_version"] or digest(source["body"]) != rule["source_digest"]:
            return {"status": "abstain", "reason": "source_or_rule_mapping_stale"}
    top = [rule for rule in rules if rule["priority"] == rules[0]["priority"]]
    if len(top) != 1:
        return {"status": "abstain", "reason": "conflicting_top_priority_rules"}
    chosen = top[0]
    if chosen["days"] is None:
        return {"status": "excluded", "source": chosen["document"]}
    if not has_receipt:
        return {"status": "abstain", "reason": "receipt_required"}
    return {"status": "answer", "days": chosen["days"], "source": chosen["document"]}


def main():
    db = setup()
    try:
        ranked = discover(db, "alice")
        cases = [
            ("before_bulletin", "household", "2026-09-30", True),
            ("after_bulletin", "household", "2026-10-02", True),
            ("no_receipt", "household", "2026-10-02", False),
            ("commercial", "commercial", "2026-10-02", False),
        ]
        print(json.dumps({"fictional_ranked_candidates": ranked,
                          "results": {label: decide(db, "alice", kind, when, receipt, ranked)
                                      for label, kind, when, receipt in cases},
                          "scope": "Local approved-rule fixture, not text understanding, model, Bedrock or AWS"}, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
