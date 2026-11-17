import importlib.util
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location('scaling_policy_model', Path(__file__).with_name('lab.py'))
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)


class ScalingModelTests(unittest.TestCase):
    def test_wait_target_and_candidate_task_count(self):
        target = model.target_backlog_per_task(10, 0.1)
        self.assertEqual(target, 100)
        self.assertEqual(model.backlog_per_task(1500, 10), 150)
        self.assertEqual(model.candidate_tasks(1500, target), 15)

    def test_extra_workers_do_not_raise_dependency_ceiling(self):
        before = model.processing_capacity(20, 8)
        after = model.processing_capacity(40, 8)
        self.assertEqual((before, after), (8, 8))
        self.assertEqual(model.completions_for_new_arrivals(12, after), 8)
        self.assertEqual(model.backlog_change_per_second(12, 8), 4)

    def test_verified_save_capacity_can_drain_existing_backlog(self):
        capacity = model.processing_capacity(20, 16)
        self.assertEqual(capacity, 16)
        self.assertEqual(model.completions_for_new_arrivals(12, capacity), 12)
        self.assertEqual(model.backlog_clear_seconds(1440, 12, capacity), 360)

    def test_no_surplus_capacity_cannot_clear_backlog(self):
        self.assertIsNone(model.backlog_clear_seconds(100, 12, 12))
        self.assertEqual(model.backlog_clear_seconds(0, 12, 12), 0)

    def test_zero_tasks_does_not_invent_a_backlog_per_task(self):
        with self.assertRaisesRegex(ValueError, 'undefined'):
            model.backlog_per_task(25, 0)

    def test_invalid_or_boolean_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            model.candidate_tasks(True, 100)
        with self.assertRaises(ValueError):
            model.target_backlog_per_task(10, 0)
        with self.assertRaises(ValueError):
            model.processing_capacity(20, -1)


if __name__ == '__main__':
    unittest.main()
