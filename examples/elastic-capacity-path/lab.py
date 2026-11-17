"""Arithmetic for one fictional steady-state request path; no AWS calls."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Path:
    requests_per_second: Decimal
    write_fraction: Decimal
    cache_hit_fraction_of_all_requests: Decimal
    ready_workers: int
    requests_per_worker: Decimal
    database_reads_per_second: Decimal
    database_writes_per_second: Decimal


def evaluate(path: Path) -> dict[str, object]:
    r, w, hit = path.requests_per_second, path.write_fraction, path.cache_hit_fraction_of_all_requests
    if r < 0 or not 0 <= w <= 1 or not 0 <= hit <= 1 - w:
        raise ValueError("Traffic and cache fractions must be nonnegative; writes cannot be cache hits")
    if path.ready_workers < 0 or any(v < 0 for v in (path.requests_per_worker, path.database_reads_per_second, path.database_writes_per_second)):
        raise ValueError("Capacity inputs must be nonnegative")
    writes = r * w
    reads = r * (1 - w - hit)
    origin = writes + reads
    ceilings = {
        "application": Decimal(path.ready_workers) * path.requests_per_worker,
        "database_reads": path.database_reads_per_second,
        "database_writes": path.database_writes_per_second,
    }
    offered = {"application": origin, "database_reads": reads, "database_writes": writes}
    exceeded = tuple(name for name in ceilings if offered[name] > ceilings[name])
    return {"cache_hits": r * hit, "origin_requests": origin, "database_reads": reads,
            "database_writes": writes, "offered": offered, "ceilings": ceilings,
            "exceeded": exceeded, "fits_steady_snapshot": not exceeded}


if __name__ == "__main__":
    baseline = Path(Decimal(60), Decimal("0.1"), Decimal("0.4"), 2,
                    Decimal(20), Decimal(28), Decimal(8))
    for label, candidate in (
        ("baseline", baseline),
        ("third worker", Path(Decimal(60), Decimal("0.1"), Decimal("0.4"), 3, Decimal(20), Decimal(28), Decimal(8))),
        ("safe extra cache hits", Path(Decimal(60), Decimal("0.1"), Decimal("0.5"), 2, Decimal(20), Decimal(28), Decimal(8))),
    ):
        result = evaluate(candidate)
        print(f"{label}: cache={result['cache_hits']}/s origin={result['origin_requests']}/s "
              f"db-read={result['database_reads']}/s db-write={result['database_writes']}/s "
              f"exceeded={result['exceeded'] or 'none'}")
