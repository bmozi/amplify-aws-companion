import unittest
from lab import handle


class FifoBatchTests(unittest.TestCase):
    def test_middle_failure_returns_failed_and_unprocessed_tail(self):
        seen = []
        def process(record):
            seen.append(record['messageId'])
            if record['messageId'] == 'B':
                raise ValueError('dependency failed')
        event = {'Records': [{'messageId': key} for key in 'ABC']}
        result = handle(event, process)
        self.assertEqual(seen, ['A', 'B'])
        self.assertEqual(result, {'batchItemFailures': [
            {'itemIdentifier': 'B'}, {'itemIdentifier': 'C'}]})

    def test_failure_at_each_end_returns_only_failed_and_unprocessed(self):
        for failed, expected_seen, expected_retry in [
            ('A', ['A'], ['A', 'B', 'C']),
            ('C', ['A', 'B', 'C'], ['C']),
        ]:
            with self.subTest(failed=failed):
                seen = []
                def process(record):
                    seen.append(record['messageId'])
                    if record['messageId'] == failed:
                        raise ValueError('dependency failed')
                response = handle({'Records': [{'messageId': key} for key in 'ABC']}, process)
                self.assertEqual(seen, expected_seen)
                self.assertEqual([item['itemIdentifier'] for item in response['batchItemFailures']], expected_retry)

    def test_success_and_empty_batch(self):
        result = handle({'Records': [{'messageId': 'A'}]}, lambda _: None)
        self.assertEqual(result, {'batchItemFailures': []})
        self.assertEqual(handle({'Records': []}, lambda _: None), result)

    def test_unexpected_error_is_not_silently_reported_as_success(self):
        def broken(_):
            raise RuntimeError('unexpected error')
        with self.assertRaises(RuntimeError):
            handle({'Records': [{'messageId': 'A'}]}, broken)

    def test_retry_does_not_undo_or_deduplicate_side_effect(self):
        assignments = []
        def write_then_fail(record):
            assignments.append(record['messageId'])
            if record['messageId'] == 'B':
                raise ValueError('reply failed after assignment was written')
        first = handle({'Records': [{'messageId': key} for key in 'ABC']},
                       write_then_fail)
        self.assertEqual(assignments, ['A', 'B'])
        retry_ids = [item['itemIdentifier'] for item in first['batchItemFailures']]
        self.assertEqual(retry_ids, ['B', 'C'])
        second = handle({'Records': [{'messageId': key} for key in retry_ids]},
                        lambda record: assignments.append(record['messageId']))
        self.assertEqual(assignments, ['A', 'B', 'B', 'C'])
        self.assertEqual(second, {'batchItemFailures': []})
