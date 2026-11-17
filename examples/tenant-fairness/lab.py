"""Deterministic local worker-slot scheduling; trusted tenant labels are fixture inputs."""

from collections import defaultdict, deque
import json


class FairQueue:
    def __init__(self, per_tenant_limit=4):
        if per_tenant_limit < 1:
            raise ValueError('Limit must be positive')
        self.limit = per_tenant_limit
        self.queues = defaultdict(deque)
        self.ready = deque()

    def submit(self, tenant, job):
        if not tenant or not job:
            raise ValueError('Trusted tenant and job ID are required')
        queue = self.queues[tenant]
        if len(queue) >= self.limit:
            return False
        if not queue:
            self.ready.append(tenant)
        queue.append(job)
        return True

    def dispatch(self):
        if not self.ready:
            return None
        tenant = self.ready.popleft()
        job = self.queues[tenant].popleft()
        if self.queues[tenant]:
            self.ready.append(tenant)
        else:
            del self.queues[tenant]
        return tenant, job


def drain(queue):
    result = []
    while (job := queue.dispatch()) is not None:
        result.append(job)
    return result


def virtual_timeline(order, seconds_by_job):
    """Model one non-preemptive worker; these are assumed durations, not measurements."""
    clock = 0
    timeline = []
    for tenant, job in order:
        duration = seconds_by_job[(tenant, job)]
        if not isinstance(duration, int) or isinstance(duration, bool) or duration <= 0:
            raise ValueError('Each job needs a positive whole-second assumed duration')
        timeline.append({'tenant': tenant, 'job': job, 'start_s': clock,
                         'finish_s': clock + duration})
        clock += duration
    return timeline


def run():
    fair = FairQueue(per_tenant_limit=4)
    fifo = deque()
    for number in range(1, 5):
        job = ('shop-a', f'a-{number}')
        assert fair.submit(*job)
        fifo.append(job)
    assert not fair.submit('shop-a', 'a-5')
    quiet = ('shop-b', 'b-1')
    assert fair.submit(*quiet)
    fifo.append(quiet)
    selected = drain(fair)
    assert selected == [('shop-a', 'a-1'), quiet, ('shop-a', 'a-2'),
                        ('shop-a', 'a-3'), ('shop-a', 'a-4')]
    assert list(fifo).index(quiet) == 4
    assumed_seconds = {('shop-a', f'a-{number}'): 600 for number in range(1, 5)}
    assumed_seconds[quiet] = 1
    fair_timeline = virtual_timeline(selected, assumed_seconds)
    fifo_timeline = virtual_timeline(fifo, assumed_seconds)
    fair_b = next(row for row in fair_timeline if row['job'] == 'b-1')
    fifo_b = next(row for row in fifo_timeline if row['job'] == 'b-1')
    assert (fair_b['start_s'], fair_b['finish_s']) == (600, 601)
    assert (fifo_b['start_s'], fifo_b['finish_s']) == (2400, 2401)
    return {'fifo_dispatch_order': list(fifo), 'fair_dispatch_order': selected,
            'quiet_job_fifo_slot': 5, 'quiet_job_fair_slot': 2,
            'assumed_job_seconds': {'each_shop_a_job': 600, 'shop_b_job': 1},
            'quiet_job_fifo_virtual_start_s': fifo_b['start_s'],
            'quiet_job_fifo_virtual_finish_s': fifo_b['finish_s'],
            'quiet_job_fair_virtual_start_s': fair_b['start_s'],
            'quiet_job_fair_virtual_finish_s': fair_b['finish_s'],
            'shop_a_fifth_job_rejected': True,
            'scope': 'One deterministic process, one non-preemptive worker, assumed durations and fixture tenant labels; no measured latency, authentication, distributed queue, database-capacity or AWS evidence'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
