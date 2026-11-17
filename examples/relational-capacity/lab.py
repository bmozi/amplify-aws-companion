"""Fictional relational storage demand arithmetic; no database or AWS calls."""

from dataclasses import dataclass
from fractions import Fraction
import json


@dataclass(frozen=True)
class Window:
    name: str
    reads_per_second: int
    writes_per_second: int
    kib_per_read: int
    kib_per_write: int
    fictional_iops_ceiling: int = 3000
    fictional_mib_per_second_ceiling: int = 125


def calculate(window: Window) -> dict:
    values = (window.reads_per_second, window.writes_per_second,
              window.kib_per_read, window.kib_per_write,
              window.fictional_iops_ceiling, window.fictional_mib_per_second_ceiling)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("all rates and sizes must be nonnegative integer inputs")
    if not window.fictional_iops_ceiling or not window.fictional_mib_per_second_ceiling:
        raise ValueError("fictional ceilings must be positive")
    if window.reads_per_second and not window.kib_per_read:
        raise ValueError("a completed read needs its stated byte size")
    if window.writes_per_second and not window.kib_per_write:
        raise ValueError("a completed write needs its stated byte size")
    iops = window.reads_per_second + window.writes_per_second
    kib_per_second = (window.reads_per_second * window.kib_per_read +
                      window.writes_per_second * window.kib_per_write)
    mib_per_second = Fraction(kib_per_second, 1024)
    return {
        "window": window.name,
        "operations_per_second": iops,
        "mib_per_second": float(mib_per_second),
        "above_fictional_iops_ceiling": iops > window.fictional_iops_ceiling,
        "above_fictional_throughput_ceiling": mib_per_second > window.fictional_mib_per_second_ceiling,
        "scope": "Arithmetic for stated completed operations and average KiB; not measured storage I/O, a selected RDS configuration, or a performance recommendation",
    }


def examples() -> list[Window]:
    return [
        Window("large reads", 1000, 200, 128, 16),
        Window("small busy reads", 2500, 300, 4, 4),
        Window("many tiny reads", 3100, 100, 4, 4),
    ]


if __name__ == "__main__":
    if not __debug__:
        raise SystemExit("Run without Python optimization")
    print(json.dumps([calculate(window) for window in examples()], indent=2))
