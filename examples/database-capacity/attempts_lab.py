"""Fictional DynamoDB write-attempt worksheet; no AWS calls or price estimate."""

from dataclasses import dataclass
import json

from lab import blocks, write_units


@dataclass(frozen=True)
class Attempt:
    name: str
    count_per_second: int
    old_table_bytes: int
    proposed_table_bytes: int
    outcome: str  # applied or condition_failed
    old_index_bytes: int = 0
    new_index_bytes: int = 0
    index_key_changed: bool = False


def capacity_for_attempt(attempt: Attempt) -> dict[str, int]:
    """Account for one stated attempt on a table and one sparse GSI.

    All index projections in this worksheet are at most 1 KiB. A larger or
    differently updated projection needs its actual item-size calculation.
    """
    if type(attempt.count_per_second) is not int or attempt.count_per_second < 0:
        raise ValueError("count_per_second must be a nonnegative integer")
    sizes = (attempt.old_table_bytes, attempt.proposed_table_bytes,
             attempt.old_index_bytes, attempt.new_index_bytes)
    if any(type(size) is not int or size < 0 for size in sizes):
        raise ValueError("sizes must be nonnegative integer bytes")
    if max(attempt.old_index_bytes, attempt.new_index_bytes) > 1024:
        raise ValueError("this teaching GSI model accepts projections up to 1 KiB")
    if type(attempt.index_key_changed) is not bool:
        raise ValueError("index_key_changed must be boolean")
    if attempt.outcome not in {"applied", "condition_failed"}:
        raise ValueError("unknown attempt outcome")
    if attempt.outcome == "condition_failed":
        if (attempt.old_index_bytes != attempt.new_index_bytes or
                attempt.index_key_changed):
            raise ValueError("a failed condition cannot change the index")
        # AWS charges the existing item size, with a one-unit minimum when
        # no item exists. The proposed bytes are not a completed write.
        table = blocks(attempt.old_table_bytes or 1, 1024)
        index = 0
    else:
        if attempt.proposed_table_bytes == 0 and attempt.old_table_bytes == 0:
            raise ValueError("an applied write needs an item before or after")
        if attempt.index_key_changed and not (attempt.old_index_bytes and attempt.new_index_bytes):
            raise ValueError("a key move needs old and new index projections")
        table = write_units(attempt.old_table_bytes, attempt.proposed_table_bytes)
        if attempt.index_key_changed:
            index = 2  # delete old index entry; put new entry
        elif bool(attempt.old_index_bytes) != bool(attempt.new_index_bytes):
            index = 1  # sparse entry added or removed
        elif attempt.old_index_bytes != attempt.new_index_bytes:
            raise ValueError("projection updates are outside this small model")
        else:
            index = 0  # stated index projection is unchanged
    return {"table_write_units_per_second": table * attempt.count_per_second,
            "gsi_write_units_per_second": index * attempt.count_per_second}


def worksheet(attempts: list[Attempt]) -> dict:
    rows = [{"attempt": attempt.name, "outcome": attempt.outcome,
             "count_per_second": attempt.count_per_second,
             **capacity_for_attempt(attempt)} for attempt in attempts]
    return {"rows": rows,
            "table_write_units_per_second": sum(row["table_write_units_per_second"] for row in rows),
            "gsi_write_units_per_second": sum(row["gsi_write_units_per_second"] for row in rows),
            "scope": "Stated successful single-item writes and failed conditions; one GSI with <=1 KiB projections; no configuration, throttling, price, transaction or AWS observation"}


def example() -> list[Attempt]:
    return [
        Attempt("40 new open requests", 40, 0, 1025, "applied", 0, 900),
        Attempt("20 failed duplicate conditions", 20, 1500, 2500,
                "condition_failed", 900, 900),
        Attempt("10 open-to-confirmed changes", 10, 1500, 1500,
                "applied", 900, 900, True),
        Attempt("5 nonprojected-note edits", 5, 1500, 1500,
                "applied", 900, 900),
    ]


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without Python optimization")
    print(json.dumps(worksheet(example()), indent=2))
