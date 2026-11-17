"""Local pre-deadline work discovery and sweep-health decision; no AWS calls."""

import json

from deadline_lab import PROMISE_SECONDS, accept, database, record_contact, second


def read_contact_watchlist(connection, now, lead_seconds=900, limit=20, after=None):
    """Read uncontacted work nearing or past its original one-hour deadline.

    This is one local keyset pass, not a concurrent snapshot or an alert.
    """
    second(now)
    if type(lead_seconds) is not int or not 1 <= lead_seconds <= PROMISE_SECONDS:
        raise ValueError("Lead time must be 1–3600 whole seconds")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("Use a 1–100 item limit")
    if after is not None:
        if (not isinstance(after, tuple) or len(after) != 2
                or type(after[0]) is not int or after[0] < 0
                or not isinstance(after[1], str) or not after[1]):
            raise ValueError("Use a (deadline_at, request_id) cursor")
    cursor_clause = "" if after is None else "AND (r.accepted_at + ?, r.request_id) > (?, ?)"
    args = [now, PROMISE_SECONDS, now + lead_seconds]
    if after is not None:
        args.extend([PROMISE_SECONDS, after[0], after[1]])
    args.append(limit + 1)
    rows = connection.execute(
        f"""SELECT r.request_id, r.accepted_at
            FROM requests AS r LEFT JOIN contacts AS c USING (request_id)
            WHERE c.request_id IS NULL AND r.accepted_at <= ?
              AND r.accepted_at + ? <= ? {cursor_clause}
            ORDER BY r.accepted_at, r.request_id LIMIT ?""",
        args,
    ).fetchall()
    visible = rows[:limit]
    items = [{"request_id": request_id, "accepted_at": accepted_at,
              "deadline_at": accepted_at + PROMISE_SECONDS,
              "state": "overdue" if now > accepted_at + PROMISE_SECONDS else "due_soon"}
             for request_id, accepted_at in visible]
    next_cursor = ((visible[-1][1] + PROMISE_SECONDS, visible[-1][0])
                   if len(rows) > limit else None)
    return {"items": items, "next_cursor": next_cursor}


def sweep_health(now, last_complete_at, maximum_gap_seconds=300):
    """Assess supplied completion evidence, not whether a real scheduler ran."""
    second(now)
    if type(maximum_gap_seconds) is not int or maximum_gap_seconds < 1:
        raise ValueError("Use a positive whole-second gap")
    if last_complete_at is None:
        return {"state": "unknown", "reason": "no complete-sweep receipt"}
    second(last_complete_at)
    if last_complete_at > now:
        raise ValueError("A sweep cannot finish in the future")
    age = now - last_complete_at
    return {"state": "stale" if age > maximum_gap_seconds else "recent",
            "age_seconds": age}


def last_complete_pass(connection):
    """Read the latest local traversal receipt, if a pass reached its last page."""
    connection.execute("""CREATE TABLE IF NOT EXISTS watchlist_passes (
        pass_id INTEGER PRIMARY KEY, completed_at INTEGER NOT NULL,
        page_count INTEGER NOT NULL, item_count INTEGER NOT NULL)""")
    row = connection.execute(
        """SELECT completed_at, page_count, item_count FROM watchlist_passes
           ORDER BY pass_id DESC LIMIT 1"""
    ).fetchone()
    return (None if row is None else
            {"completed_at": row[0], "page_count": row[1], "item_count": row[2]})


def run_watchlist_pass(connection, now, completed_at, lead_seconds=900, limit=20,
                       after_page=None):
    """Walk every local page before writing a receipt; still not a snapshot.

    after_page is a fixture hook for an interruption or concurrent local write.
    Both times are supplied teaching clocks, not authenticated scheduler evidence.
    """
    second(now)
    second(completed_at)
    if completed_at < now:
        raise ValueError("Completion cannot precede the watchlist read")
    last_complete_pass(connection)
    cursor = None
    page_count = 0
    items = []
    while True:
        page = read_contact_watchlist(connection, now, lead_seconds, limit, cursor)
        page_count += 1
        items.extend(page["items"])
        next_cursor = page["next_cursor"]
        if after_page is not None:
            after_page(page_count, page)
        if next_cursor is None:
            break
        if cursor is not None and next_cursor <= cursor:
            raise RuntimeError("Watchlist cursor did not advance")
        cursor = next_cursor
    with connection:
        connection.execute(
            "INSERT INTO watchlist_passes (completed_at, page_count, item_count) VALUES (?, ?, ?)",
            (completed_at, page_count, len(items)),
        )
    return {"items": items, "receipt": last_complete_pass(connection)}


def compare_watchlist_passes(connection, now, first_completed_at,
                            second_completed_at, lead_seconds=900, limit=20,
                            after_first_page=None):
    """Repeat discovery from the beginning and expose changed observations.

    A second complete traversal can find a key inserted behind the first
    cursor. Matching sets still do not establish a concurrent snapshot or
    that a person contacted the customer.
    """
    second(first_completed_at)
    second(second_completed_at)
    if second_completed_at < first_completed_at:
        raise ValueError("The repeat pass cannot finish before the first")
    first = run_watchlist_pass(connection, now, first_completed_at,
                               lead_seconds, limit, after_first_page)
    repeat = run_watchlist_pass(connection, now, second_completed_at,
                                lead_seconds, limit)
    first_ids = {item["request_id"] for item in first["items"]}
    repeat_ids = {item["request_id"] for item in repeat["items"]}
    return {
        "first_receipt": first["receipt"],
        "repeat_receipt": repeat["receipt"],
        "first_only": sorted(first_ids - repeat_ids),
        "repeat_only": sorted(repeat_ids - first_ids),
        "same_observed_ids": first_ids == repeat_ids,
        "customer_contact_observed": False,
        "concurrent_snapshot_proven": False,
    }


def run():
    with database() as connection:
        accept(connection, "maya-risk", 0)
        accept(connection, "maya-on-time", 0)
        at_45_minutes = read_contact_watchlist(connection, 2700)
        on_time = record_contact(connection, "maya-on-time", 3600)
        at_deadline = read_contact_watchlist(connection, 3600)
        after_deadline = read_contact_watchlist(connection, 3601)
        missing_sweep = sweep_health(3601, 2700, 300)
        assert len(at_45_minutes["items"]) == 2
        assert [x["request_id"] for x in at_deadline["items"]] == ["maya-risk"]
        assert at_deadline["items"][0]["state"] == "due_soon"
        assert after_deadline["items"][0]["state"] == "overdue"
        assert missing_sweep["state"] == "stale"
        assert on_time["met_one_hour_promise"]
        def stop_after_first_page(page_count, _page):
            if page_count == 1:
                raise RuntimeError("fixture worker stopped")

        for n in range(25):
            accept(connection, f"bulk-{n:02d}", 0)
        try:
            run_watchlist_pass(connection, 3601, 3605, limit=20,
                               after_page=stop_after_first_page)
        except RuntimeError:
            pass
        assert last_complete_pass(connection) is None
        resumed = run_watchlist_pass(connection, 3601, 3606, limit=20)
        assert resumed["receipt"]["page_count"] == 2
        assert resumed["receipt"]["item_count"] == 26
        def insert_behind_first_cursor(page_count, _page):
            if page_count == 1:
                accept(connection, "arrived-during-repeat-demo", 0)

        comparison = compare_watchlist_passes(
            connection, 3601, 3607, 3608, limit=20,
            after_first_page=insert_behind_first_cursor)
        assert comparison["first_receipt"]["item_count"] == 26
        assert comparison["repeat_receipt"]["item_count"] == 27
        assert comparison["repeat_only"] == ["arrived-during-repeat-demo"]
        print(json.dumps({"at_45_minutes": at_45_minutes,
                          "at_deadline": at_deadline,
                          "after_deadline_before_contact": after_deadline,
                          "stale_sweep_receipt": missing_sweep,
                          "interrupted_pass_receipt": None,
                          "resumed_pass_receipt": resumed["receipt"],
                          "repeat_pass_comparison": comparison,
                          "on_time_fixture_contact": on_time,
                          "human_contact_observed": False,
                          "aws_called": False}, indent=2))


if __name__ == "__main__":
    run()
