"""Fictional minute-bucket FIFO trace; no AWS calls or performance claims."""

from collections import deque


ARRIVALS = {
    "even": (6, 6, 6, 6, 6, 6),
    "burst": (0, 0, 18, 18, 0, 0),
}
CASES = {
    "even": (ARRIVALS["even"], 10, 10),
    "burst": (ARRIVALS["burst"], 10, 10),
    "more_workers_only": (ARRIVALS["burst"], 12, 10),
    "both_stages_reviewed": (ARRIVALS["burst"], 12, 12),
}


def trace(arrivals: tuple[int, ...], workers_per_minute: int,
          saves_per_minute: int) -> dict:
    if not arrivals or any(type(n) is not int or n < 0 for n in arrivals):
        raise ValueError("Arrivals must be a nonempty sequence of nonnegative integers")
    if any(type(n) is not int or n <= 0 for n in (workers_per_minute, saves_per_minute)):
        raise ValueError("Both capacities must be positive integers")
    queue = deque()
    rows = []
    late = 0
    completed = 0
    minute = 0
    while minute < len(arrivals) or queue:
        incoming = arrivals[minute] if minute < len(arrivals) else 0
        queue.extend([minute] * incoming)
        done = min(len(queue), workers_per_minute, saves_per_minute)
        for _ in range(done):
            accepted_at = queue.popleft()
            if minute - accepted_at > 1:
                late += 1
        completed += done
        rows.append({"minute": minute, "arrivals": incoming, "completed": done,
                     "unfinished": len(queue)})
        minute += 1
    return {"accepted": sum(arrivals), "completed": completed,
            "peak_unfinished": max(row["unfinished"] for row in rows),
            "late_over_one_bucket": late, "rows": rows}


def main() -> None:
    print("Fictional FIFO minute buckets; a job is late if completion is more than")
    print("one numbered bucket after its arrival. This is not elapsed latency.\n")
    for name, (arrivals, workers, saves) in CASES.items():
        result = trace(arrivals, workers, saves)
        print(f"{name}: accepted={result['accepted']} completed={result['completed']} "
              f"peak_unfinished={result['peak_unfinished']} "
              f"late={result['late_over_one_bucket']} "
              f"worker_cap={workers}/min save_cap={saves}/min")
        print("  minute arrivals completed unfinished")
        for row in result["rows"]:
            print(f"  {row['minute']:>6} {row['arrivals']:>8} "
                  f"{row['completed']:>9} {row['unfinished']:>10}")
        print()


if __name__ == "__main__":
    main()
