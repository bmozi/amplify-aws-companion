"""Illustrative hourly commitment arithmetic; no AWS prices or API calls."""

from decimal import Decimal


DISCOUNT = Decimal("0.25")
COMMITMENT = Decimal("0.40")
STEADY = [Decimal("0.80")] * 6
FALLING = [Decimal("0.80")] * 3 + [Decimal("0.20"), Decimal("0"), Decimal("0")]


def compare(hourly_on_demand, commitment=COMMITMENT, discount=DISCOUNT):
    if not hourly_on_demand or commitment < 0 or not 0 <= discount < 1:
        raise ValueError("Provide hours, a nonnegative commitment and a discount below 1")
    if any(amount < 0 for amount in hourly_on_demand):
        raise ValueError("Hourly use cannot be negative")
    covered_on_demand = commitment / (1 - discount)
    without_plan = sum(hourly_on_demand, Decimal("0"))
    with_plan = sum(
        (commitment + max(Decimal("0"), amount - covered_on_demand)
         for amount in hourly_on_demand),
        Decimal("0"),
    )
    return without_plan, with_plan, without_plan - with_plan


if __name__ == "__main__":
    for name, hours in (("steady", STEADY), ("falling", FALLING)):
        without, with_plan, difference = compare(hours)
        print(f"{name}: On-Demand ${without:.4f}; plan model ${with_plan:.4f}; "
              f"plan savings ${difference:.4f}")
