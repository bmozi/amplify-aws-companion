"""Cloud-free EBS cost-shape exercise; all rates are invented teaching inputs."""

from dataclasses import dataclass
from decimal import Decimal
import argparse
import json


@dataclass(frozen=True)
class Case:
    data_gib: int = 600
    sustained_iops: int = 6000
    sequential_mib_s: int = 200
    instance_iops_ceiling: int = 8000
    instance_mib_s_ceiling: int = 300


# Fictional 30-day rates. Never use these as an account or Region quote.
RATES = {
    "gp2_gib": Decimal("0.10"),
    "gp3_gib": Decimal("0.08"),
    "gp3_extra_iops": Decimal("0.005"),
    "gp3_extra_mib_s": Decimal("0.06"),
    "io2_gib": Decimal("0.125"),
    "io2_iops_first_tier": Decimal("0.065"),
}


def evaluate(case: Case) -> dict:
    if min(case.data_gib, case.sustained_iops, case.sequential_mib_s,
           case.instance_iops_ceiling, case.instance_mib_s_ceiling) <= 0:
        raise ValueError("All capacity and performance inputs must be positive")
    if case.sustained_iops > 32000:
        raise ValueError("The fictional io2 price model covers only the first 32,000 IOPS tier")

    instance_holds = (case.sustained_iops > case.instance_iops_ceiling or
                      case.sequential_mib_s > case.instance_mib_s_ceiling)
    gp2_size = max(case.data_gib, (case.sustained_iops + 2) // 3)
    gp2_baseline = min(16000, max(100, 3 * gp2_size))
    gp2_feasible = (not instance_holds and gp2_size <= 16384 and
                    case.sequential_mib_s <= 250 and
                    case.sustained_iops <= gp2_baseline)

    gp3_iops = max(3000, case.sustained_iops)
    gp3_mib_s = max(125, case.sequential_mib_s)
    gp3_feasible = (not instance_holds and case.data_gib <= 65536 and
                    gp3_iops <= 80000 and gp3_mib_s <= 2000 and
                    gp3_iops <= 500 * case.data_gib and
                    gp3_mib_s <= Decimal("0.25") * gp3_iops)

    gp2_cost = Decimal(gp2_size) * RATES["gp2_gib"]
    gp3_cost = (Decimal(case.data_gib) * RATES["gp3_gib"] +
                Decimal(gp3_iops - 3000) * RATES["gp3_extra_iops"] +
                Decimal(gp3_mib_s - 125) * RATES["gp3_extra_mib_s"])
    io2_cost = (Decimal(case.data_gib) * RATES["io2_gib"] +
                Decimal(case.sustained_iops) * RATES["io2_iops_first_tier"])
    return {
        "case": case.__dict__,
        "instance_holds": instance_holds,
        "gp2": {"provisioned_gib_for_sustained_iops": gp2_size,
                "baseline_iops": gp2_baseline, "shape_feasible": gp2_feasible,
                "fictional_monthly_usd": str(gp2_cost)},
        "gp3": {"provisioned_gib": case.data_gib, "provisioned_iops": gp3_iops,
                "provisioned_mib_s": gp3_mib_s, "shape_feasible": gp3_feasible,
                "fictional_monthly_usd": str(gp3_cost)},
        "io2": {"provisioned_gib": case.data_gib,
                "provisioned_iops": case.sustained_iops,
                "fictional_monthly_usd_first_tier_only": str(io2_cost),
                "selection_status": "requires measured latency, service and instance checks"},
        "limit": "Fictional rates and simple shapes; no EC2, snapshot, tax, credit or live AWS quote",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iops", type=int, default=6000)
    parser.add_argument("--throughput", type=int, default=200,
                        help="MiB/s in a separate sequential peak")
    parser.add_argument("--instance-iops", type=int, default=8000)
    args = parser.parse_args()
    print(json.dumps(evaluate(Case(sustained_iops=args.iops,
                                   sequential_mib_s=args.throughput,
                                   instance_iops_ceiling=args.instance_iops)), indent=2))


if __name__ == "__main__":
    main()
