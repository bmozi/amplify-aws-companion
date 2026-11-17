"""Cloud-free ideal transfer lower bound; never a throughput or cutover promise."""

from dataclasses import dataclass
from fractions import Fraction

SECONDS_PER_DAY = 24 * 60 * 60
BYTES_PER_TIB = 1024**4


@dataclass(frozen=True)
class TransferQuestion:
    total_tib: Fraction
    spare_mbps: Fraction
    deadline_days: Fraction

    def __post_init__(self):
        if min(self.total_tib, self.spare_mbps, self.deadline_days) <= 0:
            raise ValueError("Size, spare bandwidth and deadline must all be positive")

    @property
    def ideal_days(self) -> Fraction:
        return self.total_tib * BYTES_PER_TIB * 8 / (self.spare_mbps * 1_000_000 * SECONDS_PER_DAY)

    @property
    def ideal_required_mbps(self) -> Fraction:
        return self.total_tib * BYTES_PER_TIB * 8 / (self.deadline_days * SECONDS_PER_DAY * 1_000_000)

    @property
    def verdict(self) -> str:
        return "impossible_on_stated_path" if self.ideal_days > self.deadline_days else "unproven_even_if_bound_fits"


def main():
    case = TransferQuestion(Fraction(8), Fraction(80), Fraction(5))
    assert case.verdict == "impossible_on_stated_path"
    assert Fraction(10) < case.ideal_days < Fraction(11)
    assert Fraction(162) < case.ideal_required_mbps < Fraction(164)
    faster = TransferQuestion(Fraction(8), Fraction(1000), Fraction(20))
    assert faster.verdict == "unproven_even_if_bound_fits"
    assert faster.ideal_days < faster.deadline_days
    # Any additional approved source changes increase work; the arithmetic must not hide them.
    assert TransferQuestion(Fraction(9), Fraction(80), Fraction(5)).ideal_days > case.ideal_days
    for bad in ((0, 80, 5), (8, 0, 5), (8, 80, 0)):
        try:
            TransferQuestion(*(Fraction(value) for value in bad))
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid transfer input was accepted")
    print(f"8 TiB / 80 Mbit/s: ideal lower bound {float(case.ideal_days):.2f} days; "
          f"ideal five-day requirement {float(case.ideal_required_mbps):.2f} Mbit/s; {case.verdict}")
    print("8 TiB / 1 Gbit/s / 20 days: bound fits, but scan, change, verification and cutover remain unproven")


if __name__ == "__main__":
    main()
