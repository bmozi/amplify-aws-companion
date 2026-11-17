"""Controlled local concurrency: duplicate cold reads versus per-key coalescing."""

from concurrent.futures import Future, ThreadPoolExecutor
from threading import Barrier, Condition, Event, Lock
import sys


class HeldSource:
    """A fake source held at a known point so the concurrent schedule is observable."""

    def __init__(self, fail=False):
        self.condition = Condition()
        self.release = Event()
        self.reads = 0
        self.fail = fail

    def read(self, key):
        with self.condition:
            self.reads += 1
            self.condition.notify_all()
        if not self.release.wait(5):
            raise TimeoutError('teaching source was not released')
        if self.fail:
            raise RuntimeError('source unavailable')
        return f'{key}:approved-display'

    def wait_for_reads(self, count):
        with self.condition:
            if not self.condition.wait_for(lambda: self.reads >= count, timeout=5):
                raise TimeoutError(f'expected {count} source reads')


class NaiveCache:
    def __init__(self, source):
        self.source = source
        self.lock = Lock()
        self.entries = {}

    def get(self, key):
        with self.lock:
            if key in self.entries:
                return self.entries[key]
        value = self.source.read(key)
        with self.lock:
            self.entries[key] = value
        return value


class SingleFlightCache:
    """One load per key at a time, within this one process only."""

    def __init__(self, source):
        self.source = source
        self.condition = Condition()
        self.entries = {}
        self.inflight = {}
        self.joiners = 0

    def get(self, key):
        with self.condition:
            if key in self.entries:
                return self.entries[key]
            flight = self.inflight.get(key)
            owner = flight is None
            if owner:
                flight = Future()
                self.inflight[key] = flight
            else:
                self.joiners += 1
                self.condition.notify_all()
        if not owner:
            return flight.result(timeout=5)
        try:
            value = self.source.read(key)
        except Exception as error:
            with self.condition:
                del self.inflight[key]
                flight.set_exception(error)
            raise
        with self.condition:
            self.entries[key] = value
            del self.inflight[key]
            flight.set_result(value)
        return value

    def wait_for_joiners(self, count):
        with self.condition:
            if not self.condition.wait_for(lambda: self.joiners >= count, timeout=5):
                raise TimeoutError(f'expected {count} waiting callers')


def run():
    if sys.flags.optimize:
        raise SystemExit('Run without -O: assertions are the exercise checks')

    source = HeldSource()
    cache = NaiveCache(source)
    gate = Barrier(9)
    def naive_request():
        gate.wait(timeout=5)
        return cache.get('tenant-a:repair-17')
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(naive_request) for _ in range(8)]
        gate.wait(timeout=5)
        source.wait_for_reads(8)
        assert source.reads == 8
        source.release.set()
        assert {future.result(timeout=5) for future in futures} == {'tenant-a:repair-17:approved-display'}
    print('PASS: eight simultaneous naive misses caused eight source reads')

    source = HeldSource()
    cache = SingleFlightCache(source)
    gate = Barrier(9)
    def shared_request():
        gate.wait(timeout=5)
        return cache.get('tenant-a:repair-17')
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(shared_request) for _ in range(8)]
        gate.wait(timeout=5)
        source.wait_for_reads(1)
        cache.wait_for_joiners(7)
        assert source.reads == 1
        source.release.set()
        assert {future.result(timeout=5) for future in futures} == {'tenant-a:repair-17:approved-display'}
    assert cache.get('tenant-a:repair-17') == 'tenant-a:repair-17:approved-display'
    assert source.reads == 1
    print('PASS: eight same-key misses shared one source read in one process')

    source = HeldSource(fail=True)
    cache = SingleFlightCache(source)
    gate = Barrier(5)
    def failing_request():
        gate.wait(timeout=5)
        return cache.get('tenant-a:repair-17')
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(failing_request) for _ in range(4)]
        gate.wait(timeout=5)
        source.wait_for_reads(1)
        cache.wait_for_joiners(3)
        source.release.set()
        for future in futures:
            try:
                future.result(timeout=5)
            except RuntimeError as error:
                assert str(error) == 'source unavailable'
            else:
                raise AssertionError('failed source must not become a successful cache entry')
    assert not cache.entries and not cache.inflight and source.reads == 1
    source.fail = False
    assert cache.get('tenant-a:repair-17') == 'tenant-a:repair-17:approved-display'
    assert source.reads == 2
    print('PASS: a failed shared load is not cached and a later request can retry')


if __name__ == '__main__':
    run()
