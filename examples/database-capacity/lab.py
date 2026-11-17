"""Capacity arithmetic for stated item sizes; no DynamoDB requests or pricing model."""
from fractions import Fraction
import json


def blocks(size, block):
    if type(size) is not int or size <= 0:
        raise ValueError('Supply a positive integer item size in bytes')
    return (size + block - 1) // block


def read_units(item_bytes, consistency='strong'):
    factors = {'strong': Fraction(1), 'eventual': Fraction(1, 2), 'transactional': Fraction(2)}
    if consistency not in factors:
        raise ValueError('Unknown consistency mode')
    return blocks(item_bytes, 4096) * factors[consistency]


def write_units(before_bytes, after_bytes, transactional=False):
    if any(type(x) is not int or x < 0 for x in [before_bytes, after_bytes]):
        raise ValueError('Supply nonnegative integer item sizes')
    if type(transactional) is not bool:
        raise ValueError('transactional must be boolean')
    return blocks(max(before_bytes, after_bytes), 1024) * (2 if transactional else 1)


def main():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    # Explicit expected values straddle the billing-size boundaries.
    assert read_units(4096) == 1
    assert read_units(4097) == 2
    assert read_units(4097, 'eventual') == 1
    assert read_units(4097, 'transactional') == 4
    assert write_units(0, 1024) == 1
    assert write_units(0, 1025) == 2
    assert write_units(0, 1025, True) == 4
    assert write_units(3000, 500) == 3  # shrinking does not erase the old item size
    reads = read_units(4097) * 100
    writes = write_units(0, 1025) * 40
    assert (reads, writes) == (200, 80)
    assert (reads * 5, writes * 5) == (1000, 400)
    assert read_units(1) + read_units(8191) == 3
    assert read_units((1 + 8191) // 2) * 2 == 2  # wrong average-first estimate
    assert (read_units(4097) * 100 * Fraction(3, 2)) == 300
    for operation in [lambda: read_units(0), lambda: read_units(-1),
                      lambda: read_units(True), lambda: read_units(4.5),
                      lambda: read_units(1, 'unknown'), lambda: write_units(-1, 2),
                      lambda: write_units(0, 0), lambda: write_units(1, 2, 'yes')]:
        try:
            operation()
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid arithmetic input accepted')
    print(json.dumps({'base_read_units_per_second': int(reads),
                      'base_write_units_per_second': writes,
                      'fivefold_peak': {'read': int(reads * 5), 'write': writes * 5},
                      'mixed_size_correct_reads': 3, 'average_first_wrong_reads': 2,
                      'scope': 'Fictional successful single-item work; no indexes, failed calls, cloud measurements, headroom or prices'}, indent=2))


if __name__ == '__main__':
    main()
