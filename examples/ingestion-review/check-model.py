"""Invented sequential ingestion deadline arithmetic, not a throughput benchmark."""
from decimal import Decimal
import sys


def deadline_seconds(interval_seconds, megabytes, megabits_per_second,
                     processing_seconds, publication_seconds):
    values = [Decimal(str(v)) for v in (interval_seconds, megabytes, megabits_per_second,
                                        processing_seconds, publication_seconds)]
    if any(not v.is_finite() or v < 0 for v in values) or values[2] == 0:
        raise ValueError('Finite nonnegative quantities and positive throughput required')
    interval, size, rate, processing, publication = values
    # Decimal MB -> bits / decimal Mb per second. No overlap among modeled stages.
    transfer = size * Decimal(8) / rate
    return transfer, interval + transfer + processing + publication


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O')
    for interval, size, expected_transfer, expected_total, meets in [
        (300, 30, 24, 375, False), (180, 30, 24, 255, True),
        (180, 60, 48, 279, True), (180, 90, 72, 303, False),
    ]:
        transfer, total = deadline_seconds(interval, size, 10, 45, 6)
        assert (transfer, total) == (Decimal(expected_transfer), Decimal(expected_total))
        assert (total <= 300) is meets
        print('Fictional interval=', interval, 's; size=', size, 'MB; transfer=', transfer,
              's; total=', total, 's; within 300 s=', meets)
    for rate in [0, -1, 'NaN', 'Infinity']:
        try:
            deadline_seconds(180, 30, rate, 45, 6)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid throughput accepted')
    print('PASS: decimal-unit sequential model; no jitter, overlap, retries, billing or AWS measurement')


if __name__ == '__main__':
    run()
