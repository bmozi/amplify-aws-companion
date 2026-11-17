"""Fictional single-request and EBS-limit arithmetic; no AWS calls or benchmarks."""

from fractions import Fraction


def request_total(stages_ms: dict[str, int]) -> int:
    if not stages_ms or any(not isinstance(value, int) or value < 0 for value in stages_ms.values()):
        raise ValueError("Provide nonnegative integer durations from one correlated request")
    return sum(stages_ms.values())


def candidate_total(stages_ms: dict[str, int], stage: str, saved_ms: int) -> int:
    if stage not in stages_ms or not isinstance(saved_ms, int) or saved_ms < 0 or saved_ms > stages_ms[stage]:
        raise ValueError("A candidate may reduce only one observed stage by a feasible amount")
    return request_total(stages_ms) - saved_ms


def ebs_ceiling_screen(
    operations_per_second: int,
    kib_per_operation: int,
    volume_iops: int,
    volume_mib_per_second: int,
    instance_iops: int,
    instance_mib_per_second: int,
) -> dict:
    values = [
        operations_per_second, kib_per_operation, volume_iops,
        volume_mib_per_second, instance_iops, instance_mib_per_second,
    ]
    if any(not isinstance(value, int) or value <= 0 for value in values):
        raise ValueError("Supply positive integer fictional demand and ceilings")
    demand_mib_per_second = Fraction(operations_per_second * kib_per_operation, 1024)
    return {
        "demand_mib_per_second": demand_mib_per_second,
        "volume_iops_exceeded": operations_per_second > volume_iops,
        "volume_throughput_exceeded": demand_mib_per_second > volume_mib_per_second,
        "instance_iops_exceeded": operations_per_second > instance_iops,
        "instance_throughput_exceeded": demand_mib_per_second > instance_mib_per_second,
    }


def main() -> None:
    stages = {"app_cpu": 110, "file_wait": 260, "database_wait": 420, "other": 90}
    print("single fictional request:", request_total(stages), "ms; target: 600 ms")
    print("halve file wait:", candidate_total(stages, "file_wait", 130), "ms")
    print("reduce database wait by 300 ms:", candidate_total(stages, "database_wait", 300), "ms")
    for label, inputs in [
        ("volume IOPS screen", (6000, 4, 3000, 125, 7000, 100)),
        ("instance IOPS screen", (3500, 4, 5000, 125, 3000, 100)),
        ("both throughput ceilings", (4000, 256, 8000, 750, 8000, 900)),
    ]:
        print(label + ":", ebs_ceiling_screen(*inputs))


if __name__ == "__main__":
    main()
