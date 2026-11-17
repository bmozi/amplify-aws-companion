"""Exercise field-specific canonical keys and a durable SQLite uniqueness rule."""

import json
from pathlib import Path
import sqlite3
import tempfile
import unicodedata


COMPOSED = "Caf\u00e9"
DECOMPOSED = "Cafe\u0301"


def key_for_label(raw):
    if not isinstance(raw, str) or not raw:
        raise ValueError("supplier label must be nonempty text")
    return unicodedata.normalize("NFC", raw)


def insert_supplier(connection, supplier_id, label):
    # The caller stores both the display spelling and the contract's key.
    # The database constraint, not a prior SELECT, arbitrates concurrent writes.
    connection.execute(
        "INSERT INTO suppliers (supplier_id, label_raw, label_key) VALUES (?, ?, ?)",
        (supplier_id, label, key_for_label(label)),
    )
    connection.commit()


def run():
    assert COMPOSED != DECOMPOSED
    assert key_for_label(COMPOSED) == key_for_label(DECOMPOSED)
    with tempfile.TemporaryDirectory() as directory:
        database = Path(directory) / "labels.sqlite3"
        first = sqlite3.connect(database, timeout=2)
        second = sqlite3.connect(database, timeout=2)
        try:
            first.execute("CREATE TABLE raw_only ("
                          "supplier_id TEXT PRIMARY KEY, label_raw TEXT NOT NULL UNIQUE)")
            first.executemany(
                "INSERT INTO raw_only (supplier_id, label_raw) VALUES (?, ?)",
                [("supplier-A", COMPOSED), ("supplier-B", DECOMPOSED)],
            )
            raw_only_count = first.execute("SELECT COUNT(*) FROM raw_only").fetchone()[0]
            assert raw_only_count == 2
            first.execute("CREATE TABLE suppliers ("
                          "supplier_id TEXT PRIMARY KEY, "
                          "label_raw TEXT NOT NULL UNIQUE, "
                          "label_key TEXT NOT NULL UNIQUE)")
            first.commit()

            # Both independently look first. This is intentionally insufficient.
            first_seen = first.execute(
                "SELECT supplier_id FROM suppliers WHERE label_key = ?",
                (key_for_label(COMPOSED),),
            ).fetchone()
            second_seen = second.execute(
                "SELECT supplier_id FROM suppliers WHERE label_key = ?",
                (key_for_label(DECOMPOSED),),
            ).fetchone()
            assert first_seen is second_seen is None

            insert_supplier(first, "supplier-A", COMPOSED)
            try:
                insert_supplier(second, "supplier-B", DECOMPOSED)
            except sqlite3.IntegrityError as error:
                second.rollback()
                assert "label_key" in str(error)
                collision = "rejected by label_key UNIQUE"
            else:
                raise AssertionError("Equivalent second label was accepted")

            # A second spelling can still name the original record for lookup;
            # it must never silently turn supplier-B into supplier-A.
            found = second.execute(
                "SELECT supplier_id, label_raw FROM suppliers WHERE label_key = ?",
                (key_for_label(DECOMPOSED),),
            ).fetchone()
            assert found == ("supplier-A", COMPOSED)
            rows = second.execute(
                "SELECT supplier_id, label_raw, label_key FROM suppliers"
            ).fetchall()
            assert rows == [("supplier-A", COMPOSED, key_for_label(COMPOSED))]
        finally:
            first.close()
            second.close()

    print(json.dumps({
        "raw_only_distinct_rows": raw_only_count,
        "both_prior_reads_empty": True,
        "second_insert": collision,
        "stored_supplier_ids": [row[0] for row in rows],
        "lookup_with_second_spelling": found[0],
        "rule": "NFC only for human-entered supplier label; not identity or authorization",
        "scope": "Temporary local SQLite, ordered connections; no AWS or distributed race",
    }))


if __name__ == "__main__":
    run()
