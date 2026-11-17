import unittest

from lab import FairQueue, drain, run, virtual_timeline


class FairQueueTests(unittest.TestCase):
    def test_bursty_tenant_does_not_take_every_early_slot(self):
        result = run()
        self.assertEqual(result['quiet_job_fifo_slot'], 5)
        self.assertEqual(result['quiet_job_fair_slot'], 2)
        self.assertEqual(result['quiet_job_fair_virtual_finish_s'], 601)
        self.assertEqual(result['quiet_job_fifo_virtual_finish_s'], 2401)

    def test_short_second_slot_still_waits_behind_long_first_job(self):
        order = [('a', 'long'), ('b', 'short')]
        timeline = virtual_timeline(order, {('a', 'long'): 600, ('b', 'short'): 1})
        self.assertEqual(timeline[1]['start_s'], 600)
        self.assertEqual(timeline[1]['finish_s'], 601)

    def test_virtual_time_rejects_zero_duration(self):
        with self.assertRaises(ValueError):
            virtual_timeline([('a', 'bad')], {('a', 'bad'): 0})

    def test_limit_is_per_tenant_and_rejected_job_is_not_dispatched(self):
        queue = FairQueue(2)
        self.assertTrue(queue.submit('a', 'a1'))
        self.assertTrue(queue.submit('a', 'a2'))
        self.assertFalse(queue.submit('a', 'a3'))
        self.assertTrue(queue.submit('b', 'b1'))
        self.assertEqual(drain(queue), [('a', 'a1'), ('b', 'b1'), ('a', 'a2')])

    def test_each_tenant_keeps_its_own_order_across_rounds(self):
        queue = FairQueue()
        for tenant, job in [('a', 'a1'), ('b', 'b1'), ('a', 'a2'),
                            ('b', 'b2'), ('c', 'c1'), ('a', 'a3')]:
            queue.submit(tenant, job)
        self.assertEqual(drain(queue), [('a', 'a1'), ('b', 'b1'), ('c', 'c1'),
                                        ('a', 'a2'), ('b', 'b2'), ('a', 'a3')])
        self.assertIsNone(queue.dispatch())

    def test_new_work_after_empty_queue_is_schedulable(self):
        queue = FairQueue(1)
        queue.submit('a', 'first')
        self.assertEqual(queue.dispatch(), ('a', 'first'))
        queue.submit('a', 'second')
        self.assertEqual(queue.dispatch(), ('a', 'second'))

    def test_late_arrival_waits_for_already_ready_tenant(self):
        queue = FairQueue()
        for number in range(1, 4):
            queue.submit('a', f'a{number}')
        self.assertEqual(queue.dispatch(), ('a', 'a1'))
        queue.submit('b', 'b1')
        self.assertEqual(drain(queue), [('a', 'a2'), ('b', 'b1'), ('a', 'a3')])

    def test_invalid_inputs_do_not_enter_queue(self):
        queue = FairQueue()
        for tenant, job in [('', 'j'), ('a', '')]:
            with self.assertRaises(ValueError):
                queue.submit(tenant, job)
        self.assertIsNone(queue.dispatch())
        with self.assertRaises(ValueError):
            FairQueue(0)


if __name__ == '__main__':
    unittest.main()
