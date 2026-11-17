"""Plan a fictional transfer rate; this is arithmetic, not a network benchmark."""
import math


GIB_BYTES = 2 ** 30
BITS_PER_GIGABIT = 10 ** 9


def required_gbps(volume_gib, deadline_minutes, overhead_factor=1.2, target_utilization=0.70):
    values = (volume_gib, deadline_minutes, overhead_factor, target_utilization)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("inputs must be finite numbers")
    if volume_gib <= 0 or deadline_minutes <= 0:
        raise ValueError("volume and deadline must be positive")
    if overhead_factor < 1:
        raise ValueError("overhead_factor must be at least 1")
    if not 0 < target_utilization <= 1:
        raise ValueError("target_utilization must be greater than 0 and at most 1")
    payload_bits = volume_gib * GIB_BYTES * 8
    seconds = deadline_minutes * 60
    payload_gbps = payload_bits / seconds / BITS_PER_GIGABIT
    return payload_gbps * overhead_factor / target_utilization


def main():
    cases = [
        ("nightly recovery copy", 480, 120, 1.20, 0.70),
        ("regional migration", 2.4 * 1024, 120, 1.20, 0.70),
    ]
    print("Fictional planning estimates only; no throughput is measured.")
    for label, volume, deadline, overhead, utilization in cases:
        rate = required_gbps(volume, deadline, overhead, utilization)
        print(f"{label}: {volume:,.1f} GiB in {deadline} min -> {rate:.3f} Gbps planning rate")
    assert round(required_gbps(480, 120), 3) == 0.982
    assert round(required_gbps(2.4 * 1024, 120), 3) == 5.026
    invalid = [(0, 10, 1.2, .7), (10, 0, 1.2, .7), (10, 10, .9, .7), (10, 10, 1.2, 0)]
    for inputs in invalid:
        try:
            required_gbps(*inputs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid inputs accepted: {inputs}")
    print("Input guards passed; rates are estimates, not link guarantees.")


if __name__ == "__main__":
    main()
