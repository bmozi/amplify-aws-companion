"""Emulated AWS tests. These do not establish real AWS concurrency or IAM behavior."""
import json
import importlib
import os
import sys
import unittest
from unittest.mock import patch
from pathlib import Path
import boto3
from botocore.exceptions import EndpointConnectionError
from moto import mock_aws
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from domain import Lab


@mock_aws
class DomainTests(unittest.TestCase):
    def setUp(self):
        self.db = boto3.resource('dynamodb', region_name='us-east-2').meta.client
        self.db.create_table(TableName='test-lab', KeySchema=[{'AttributeName': 'pk', 'KeyType': 'HASH'}],
                             AttributeDefinitions=[{'AttributeName': 'pk', 'AttributeType': 'S'},
                                                   {'AttributeName': 'due_partition', 'AttributeType': 'S'},
                                                   {'AttributeName': 'expires_at', 'AttributeType': 'N'}],
                             GlobalSecondaryIndexes=[{'IndexName': 'due-holds',
                                                      'KeySchema': [{'AttributeName': 'due_partition', 'KeyType': 'HASH'},
                                                                    {'AttributeName': 'expires_at', 'KeyType': 'RANGE'}],
                                                      'Projection': {'ProjectionType': 'KEYS_ONLY'}}],
                             BillingMode='PAY_PER_REQUEST')
        self.sqs = boto3.client('sqs', region_name='us-east-2')
        self.queue = self.sqs.create_queue(QueueName='test-lab')['QueueUrl']
        self.lab = Lab(self.db, 'test-lab', self.sqs, self.queue)

    def seed(self, seats=1):
        self.db.put_item(TableName='test-lab', Item={'pk': 'course#intro', 'remaining': seats})

    def seed_holds(self, seats=1):
        self.db.put_item(TableName='test-lab', Item={'pk': 'course#intro', 'remaining': seats,
                                                    'capacity': seats, 'mode': 'holds'})

    def test_replay_and_changed_payload(self):
        first = self.lab.submit('alice', 'r1', 'heater', now=100)
        self.assertEqual(100, first['accepted_at'])
        self.assertEqual(first, self.lab.submit('alice', 'r1', 'heater', now=3600))
        with self.assertRaises(ValueError):
            self.lab.submit('alice', 'r1', 'different', now=7200)
        self.assertEqual('heater', self.lab.get(first['pk'])['text'])
        self.assertEqual(100, self.lab.get(first['pk'])['accepted_at'])

    def test_lost_acceptance_reply_preserves_first_clock(self):
        write = self.db.transact_write_items

        def commit_without_reply(**kwargs):
            write(**kwargs)
            raise EndpointConnectionError(endpoint_url='https://fixture.invalid')

        with patch.object(self.db, 'transact_write_items', side_effect=commit_without_reply):
            with self.assertRaises(EndpointConnectionError):
                self.lab.submit('alice', 'r1', 'heater', now=100)
        recovered = self.lab.submit('alice', 'r1', 'heater', now=3700)
        self.assertEqual(100, recovered['accepted_at'])
        self.assertEqual('ACCEPTED', recovered['status'])
        self.assertFalse(self.lab.get('outbox#' + recovered['pk'])['sent'])

    def test_retry_of_legacy_request_does_not_invent_acceptance_time(self):
        first = self.lab.submit('alice', 'r1', 'heater', now=100)
        self.db.update_item(TableName='test-lab', Key={'pk': first['pk']},
                            UpdateExpression='REMOVE accepted_at')
        recovered = self.lab.submit('alice', 'r1', 'heater', now=3700)
        self.assertNotIn('accepted_at', recovered)
        self.assertEqual('ACCEPTED', recovered['status'])

    def test_bad_server_clock_does_not_accept_request(self):
        for now in (True, -1, 1.5):
            with self.assertRaises(ValueError):
                self.lab.submit('alice', 'r1', 'heater', now=now)
        self.assertIsNone(self.lab.get('request#alice#r1'))

    def test_contact_deadline_and_lost_check_reply(self):
        request = self.lab.submit('alice', 'r1', 'heater', now=0)
        self.assertEqual([], self.lab.check_contact_due(3600)['newly_opened'])
        first = self.lab.check_contact_due(3601)
        self.assertEqual([request['pk']], [row['request'] for row in first['newly_opened']])
        self.assertEqual([], self.lab.check_contact_due(3602)['newly_opened'])
        open_page = self.lab.read_open_contacts()
        self.assertEqual([request['pk']], [row['request'] for row in open_page['items']])
        self.assertEqual(3601, open_page['items'][0]['opened_at'])
        contact = self.lab.record_first_contact('alice', 'r1', 4 * 3600)
        self.assertFalse(contact['met_one_hour_promise'])
        self.assertEqual(4 * 3600, self.lab.record_first_contact('alice', 'r1', 5 * 3600)['first_contact_at'])
        self.assertEqual([], self.lab.read_open_contacts()['items'])
        self.assertIsNotNone(self.lab.get('escalation#' + request['pk']))

    def test_on_time_contact_prevents_opening_and_late_contact_keeps_history(self):
        self.lab.submit('alice', 'ontime', 'heater', now=20)
        self.assertTrue(self.lab.record_first_contact('alice', 'ontime', 3620)['met_one_hour_promise'])
        self.lab.submit('alice', 'late', 'door', now=0)
        self.assertFalse(self.lab.record_first_contact('alice', 'late', 4000)['met_one_hour_promise'])
        opened = self.lab.check_contact_due(4001)['newly_opened']
        self.assertEqual(['request#alice#late'], [row['request'] for row in opened])
        self.assertEqual([], self.lab.read_open_contacts()['items'])

    def test_contact_scan_requires_every_page_and_reports_legacy_unknown(self):
        for i in range(25):
            self.lab.submit('alice', f'r{i:02}', 'heater', now=0)
        self.db.update_item(TableName='test-lab', Key={'pk': 'request#alice#r24'},
                            UpdateExpression='REMOVE accepted_at')
        cursor, opened, unknown = None, [], []
        for _ in range(10):
            page = self.lab.check_contact_due(3601, cursor)
            opened += page['newly_opened']
            unknown += page['unknown_acceptance_time']
            cursor = page.get('next_cursor')
            if not cursor:
                break
        else:
            self.fail('Manual due scan did not finish')
        self.assertEqual(24, len(opened))
        self.assertEqual(['request#alice#r24'], unknown)
        cursor, work = None, []
        for _ in range(10):
            page = self.lab.read_open_contacts(cursor)
            work += page['items']
            cursor = page.get('next_cursor')
            if not cursor:
                break
        else:
            self.fail('Manual open-worklist scan did not finish')
        self.assertEqual({row['request'] for row in opened}, {row['request'] for row in work})

    def test_contact_input_and_missing_request_are_rejected(self):
        for now in (True, -1, 1.5):
            with self.assertRaises(ValueError):
                self.lab.check_contact_due(now)
            with self.assertRaises(ValueError):
                self.lab.record_first_contact('alice', 'r1', now)
        with self.assertRaises(ValueError):
            self.lab.record_first_contact('alice', 'r1', 10)
        self.lab.submit('alice', 'r1', 'heater', now=10)
        with self.assertRaises(ValueError):
            self.lab.record_first_contact('alice', 'r1', 9)

    def test_dispatch_crash_can_duplicate_without_duplicate_effect(self):
        req = self.lab.submit('alice', 'r1', 'heater')
        with self.assertRaises(RuntimeError):
            self.lab.dispatch(fail_after_send=True)
        self.assertFalse(self.lab.get('outbox#' + req['pk'])['sent'])
        self.assertEqual({'sent': 1}, self.lab.dispatch())
        # Inspect the actual emulated queue payloads, not just two manual worker calls.
        messages = self.sqs.receive_message(QueueUrl=self.queue, MaxNumberOfMessages=10,
                                           WaitTimeSeconds=0, VisibilityTimeout=30).get('Messages', [])
        self.assertEqual(2, len(messages))
        self.assertEqual(2, len({message['MessageId'] for message in messages}))
        payloads = [json.loads(message['Body']) for message in messages]
        self.assertEqual([{'request': req['pk']}] * 2, payloads)
        self.assertEqual(['created', 'duplicate'],
                         [self.lab.process(payload['request']) for payload in payloads])
        self.assertEqual('DONE', self.lab.get(req['pk'])['status'])
        appointments = [x for x in self.db.scan(TableName='test-lab')['Items'] if x.get('kind') == 'appointment']
        self.assertEqual(1, len(appointments))

    def test_dispatch_exposes_cursor_when_first_page_has_no_pending_work(self):
        for n in range(22):
            self.db.put_item(TableName='test-lab', Item={'pk': f'filler#{n}', 'kind': 'fixture'})
        self.lab.submit('alice', 'late', 'heater')
        page = self.lab.dispatch()
        self.assertEqual(0, page['sent'])
        self.assertIn('next_cursor', page)
        sent = 0
        for _ in range(5):
            page = self.lab.dispatch(cursor=page['next_cursor'])
            sent += page['sent']
            if 'next_cursor' not in page:
                break
        else:
            self.fail('Dispatcher did not finish the bounded fixture')
        self.assertEqual(1, sent)

    def test_failed_dependency_is_recoverable(self):
        req = self.lab.submit('alice', 'r1', 'heater')
        self.db.put_item(TableName='test-lab', Item={'pk': 'control#scheduler', 'unavailable': True})
        record = {'messageId': 'm1', 'body': json.dumps({'request': req['pk']})}
        self.assertEqual([{'itemIdentifier': 'm1'}], self.lab.batch([record])['batchItemFailures'])
        self.assertEqual('ACCEPTED', self.lab.get(req['pk'])['status'])
        self.assertIsNone(self.lab.get('appointment#' + req['pk']))
        self.db.delete_item(TableName='test-lab', Key={'pk': 'control#scheduler'})
        self.assertEqual([], self.lab.batch([record])['batchItemFailures'])

    def test_batch_keeps_successful_record_when_neighbor_fails(self):
        req = self.lab.submit('alice', 'r1', 'heater')
        result = self.lab.batch([{'messageId': 'bad', 'body': 'invalid json'},
                                {'messageId': 'good', 'body': json.dumps({'request': req['pk']})}])
        self.assertEqual([{'itemIdentifier': 'bad'}], result['batchItemFailures'])
        self.assertEqual('DONE', self.lab.get(req['pk'])['status'])

    def test_last_seat_and_idempotent_retry(self):
        self.seed()
        self.assertEqual('CONFIRMED', self.lab.reserve('intro', 'alice')['status'])
        self.assertTrue(self.lab.reserve('intro', 'alice')['replayed'])
        self.assertEqual('SOLD_OUT', self.lab.reserve('intro', 'bob')['status'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])
        self.assertIsNone(self.lab.get('reservation#intro#bob'))

    def test_unknown_course_and_bad_input_do_not_create_records(self):
        with self.assertRaises(ValueError): self.lab.reserve('missing', 'alice')
        self.assertIsNone(self.lab.get('reservation#missing#alice'))
        with self.assertRaises(ValueError): self.lab.submit('alice#bob', 'r1', 'x')
        with self.assertRaises(ValueError): self.lab.submit('alice', 'r1', 'x' * 501)
        self.assertEqual([], self.db.scan(TableName='test-lab')['Items'])

    def test_reservation_reply_lost_after_commit_recovers_without_second_seat(self):
        self.seed(seats=2)
        write = self.db.transact_write_items

        def commit_without_reply(**kwargs):
            write(**kwargs)
            raise EndpointConnectionError(endpoint_url='https://fixture.invalid')

        with patch.object(self.db, 'transact_write_items', side_effect=commit_without_reply):
            with self.assertRaises(EndpointConnectionError):
                self.lab.reserve('intro', 'alice')
        # The caller saw failure, but the emulator contains the committed outcome.
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertEqual('alice', self.lab.get('reservation#intro#alice')['actor'])
        restarted = Lab(self.db, 'test-lab', self.sqs, self.queue)
        result = restarted.reserve('intro', 'alice')
        self.assertEqual({'status': 'CONFIRMED', 'replayed': True,
                          'reservation': 'reservation#intro#alice'}, result)
        self.assertEqual(1, restarted.get('course#intro')['remaining'])
        self.assertEqual('CONFIRMED', restarted.reserve('intro', 'bob')['status'])
        self.assertEqual('SOLD_OUT', restarted.reserve('intro', 'carol')['status'])
        self.assertEqual(0, restarted.get('course#intro')['remaining'])
        reservations = [row for row in self.db.scan(TableName='test-lab')['Items']
                        if row.get('kind') == 'reservation']
        self.assertEqual({'alice', 'bob'}, {row['actor'] for row in reservations})
        self.assertEqual(2, len(reservations))

    def test_reservation_failure_before_write_is_not_sold_out(self):
        self.seed()
        with patch.object(self.db, 'transact_write_items',
                          side_effect=EndpointConnectionError(endpoint_url='https://fixture.invalid')):
            with self.assertRaises(EndpointConnectionError):
                self.lab.reserve('intro', 'alice')
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertIsNone(self.lab.get('reservation#intro#alice'))
        self.assertEqual('CONFIRMED', self.lab.reserve('intro', 'alice')['status'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])

    def test_exhausted_conflicts_preserve_capacity_and_surface_failure(self):
        self.seed()
        conflict = self.db.exceptions.TransactionCanceledException(
            {'Error': {'Code': 'TransactionCanceledException', 'Message': 'Injected conflict'},
             'CancellationReasons': [{'Code': 'TransactionConflict'}, {'Code': 'None'}]},
            'TransactWriteItems')
        with patch.object(self.db, 'transact_write_items', side_effect=conflict) as writer, \
                patch('domain.time.sleep'):
            with self.assertRaises(self.db.exceptions.TransactionCanceledException):
                self.lab.reserve('intro', 'alice')
        self.assertEqual(5, writer.call_count)
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertIsNone(self.lab.get('reservation#intro#alice'))

    def test_hold_expiry_releases_once_and_allows_new_attempt(self):
        self.seed_holds()
        first = self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual('HELD', first['status'])
        self.assertTrue(self.lab.acquire_hold('intro', 'alice', 'a1', 10, 8)['replayed'])
        self.assertEqual('SOLD_OUT', self.lab.acquire_hold('intro', 'bob', 'b1', 10, 9)['status'])
        self.assertEqual('NOT_DUE', self.lab.transition_hold('intro', 'a1', 'expire', 9)['status'])
        self.assertEqual('EXPIRED', self.lab.transition_hold('intro', 'a1', 'expire', 10)['status'])
        self.assertTrue(self.lab.transition_hold('intro', 'a1', 'expire', 10)['replayed'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertIsNone(self.lab.get('claim#intro#alice'))
        self.assertEqual('HELD', self.lab.acquire_hold('intro', 'bob', 'b1', 10, 10)['status'])
        self.assertEqual('CONFIRMED', self.lab.transition_hold('intro', 'b1', 'confirm', 11)['status'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])
        self.assertEqual('EXPIRED', self.lab.acquire_hold('intro', 'alice', 'a1', 10, 12)['status'])
        self.assertEqual('ACTIVE_CLAIM', self.lab.acquire_hold('intro', 'bob', 'b2', 10, 12)['status'])

    def test_confirm_then_cancel_preserves_capacity(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual('CONFIRMED', self.lab.transition_hold('intro', 'a1', 'confirm', 9)['status'])
        self.assertEqual('CONFIRMED', self.lab.transition_hold('intro', 'a1', 'cancel', 9)['status'])
        self.assertEqual('CONFIRMED', self.lab.transition_hold('intro', 'a1', 'expire', 100)['status'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])
        self.assertEqual('CONFIRMED', self.lab.get('claim#intro#alice')['status'])

    def test_cancel_then_confirm_releases_once(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual('CANCELLED', self.lab.transition_hold('intro', 'a1', 'cancel', 9)['status'])
        self.assertEqual('CANCELLED', self.lab.transition_hold('intro', 'a1', 'confirm', 9)['status'])
        self.assertEqual('CANCELLED', self.lab.transition_hold('intro', 'a1', 'expire', 10)['status'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertIsNone(self.lab.get('claim#intro#alice'))

    def test_expired_confirmation_needs_separate_release(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual('EXPIRED_NEEDS_RELEASE', self.lab.transition_hold('intro', 'a1', 'confirm', 10)['status'])
        self.assertEqual('EXPIRED_NEEDS_RELEASE', self.lab.transition_hold('intro', 'a1', 'cancel', 10)['status'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])
        self.assertEqual('EXPIRED', self.lab.transition_hold('intro', 'a1', 'expire', 10)['status'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_hold_identity_and_intent_are_stable(self):
        self.seed_holds(seats=2)
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        with self.assertRaises(ValueError):
            self.lab.acquire_hold('intro', 'bob', 'a1', 10, 1)
        with self.assertRaises(ValueError):
            self.lab.acquire_hold('intro', 'alice', 'a1', 20, 1)
        self.assertEqual('ACTIVE_CLAIM', self.lab.acquire_hold('intro', 'alice', 'a2', 10, 1)['status'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        for args in [('intro', 'alice', 'a3', 0, 0), ('intro', 'alice', 'a3', 601, 0),
                     ('intro', 'alice', 'a3', 10, True)]:
            with self.assertRaises(ValueError):
                self.lab.acquire_hold(*args)

    def test_hold_reply_lost_after_commit_recovers_without_second_seat(self):
        self.seed_holds()
        write = self.db.transact_write_items
        def commit_without_reply(**kwargs):
            write(**kwargs)
            raise EndpointConnectionError(endpoint_url='https://fixture.invalid')
        with patch.object(self.db, 'transact_write_items', side_effect=commit_without_reply):
            with self.assertRaises(EndpointConnectionError):
                self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        restarted = Lab(self.db, 'test-lab', self.sqs, self.queue)
        self.assertTrue(restarted.acquire_hold('intro', 'alice', 'a1', 10, 1)['replayed'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])

    def test_courses_cannot_mix_immediate_and_hold_contracts(self):
        self.seed()
        with self.assertRaises(ValueError):
            self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.db.update_item(TableName='test-lab', Key={'pk': 'course#intro'},
                            UpdateExpression='SET #m = :holds',
                            ExpressionAttributeNames={'#m': 'mode'},
                            ExpressionAttributeValues={':holds': 'holds'})
        with self.assertRaises(ValueError):
            self.lab.reserve('intro', 'alice')
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_expiry_reply_lost_after_commit_does_not_release_twice(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        write = self.db.transact_write_items
        def commit_without_reply(**kwargs):
            write(**kwargs)
            raise EndpointConnectionError(endpoint_url='https://fixture.invalid')
        with patch.object(self.db, 'transact_write_items', side_effect=commit_without_reply):
            with self.assertRaises(EndpointConnectionError):
                self.lab.transition_hold('intro', 'a1', 'expire', 10)
        restarted = Lab(self.db, 'test-lab', self.sqs, self.queue)
        result = restarted.transition_hold('intro', 'a1', 'expire', 10)
        self.assertEqual({'status': 'EXPIRED', 'replayed': True}, result)
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_release_refuses_corrupt_capacity_instead_of_incrementing(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.db.update_item(TableName='test-lab', Key={'pk': 'course#intro'},
                            UpdateExpression='SET remaining = :one',
                            ExpressionAttributeValues={':one': 1})
        with self.assertRaises(RuntimeError):
            self.lab.transition_hold('intro', 'a1', 'expire', 10)
        self.assertEqual('HELD', self.lab.get('hold#intro#a1')['status'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_hold_transition_refuses_changed_course_mode(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.db.update_item(TableName='test-lab', Key={'pk': 'course#intro'},
                            UpdateExpression='SET #m = :immediate',
                            ExpressionAttributeNames={'#m': 'mode'},
                            ExpressionAttributeValues={':immediate': 'immediate'})
        for action, now in [('confirm', 9), ('expire', 10)]:
            with self.assertRaises(RuntimeError):
                self.lab.transition_hold('intro', 'a1', action, now)
        self.assertEqual('HELD', self.lab.get('hold#intro#a1')['status'])
        self.assertEqual(0, self.lab.get('course#intro')['remaining'])

    def test_missing_hold_capacity_is_not_reported_sold_out(self):
        self.db.put_item(TableName='test-lab', Item={'pk': 'course#intro',
                                                    'remaining': 1, 'mode': 'holds'})
        with self.assertRaisesRegex(RuntimeError, 'no configured capacity'):
            self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertIsNone(self.lab.get('hold#intro#a1'))

    def test_sweep_pages_past_empty_filter_results_and_releases_once(self):
        self.seed_holds()
        for n in range(22):
            self.db.put_item(TableName='test-lab', Item={'pk': f'filler#{n}', 'kind': 'fixture'})
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        first = self.lab.sweep_due_holds(10)
        self.assertEqual(0, first['matched'])
        self.assertLessEqual(first['evaluated'], 5)
        self.assertIsNotNone(first['scan_capacity_units'])
        self.assertIn('next_cursor', first)
        cursor, expired = first['next_cursor'], 0
        for _ in range(10):
            page = self.lab.sweep_due_holds(10, cursor)
            self.assertLessEqual(page['evaluated'], 5)
            expired += page['expired']
            cursor = page.get('next_cursor')
            if not cursor:
                break
        else:
            self.fail('Bounded sweep did not finish the small fixture')
        self.assertEqual(1, expired)
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])
        self.assertEqual('EXPIRED', self.lab.get('hold#intro#a1')['status'])
        self.assertEqual(0, self.lab.sweep_due_holds(10)['expired'])

    def test_sweep_does_not_release_early_or_confirmed_holds(self):
        self.seed_holds(seats=2)
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.lab.acquire_hold('intro', 'bob', 'b1', 10, 0)
        self.lab.transition_hold('intro', 'b1', 'confirm', 9)
        self.assertEqual(0, self.lab.sweep_due_holds(9)['expired'])
        self.assertEqual(1, self.lab.sweep_due_holds(10)['expired'])
        self.assertEqual('CONFIRMED', self.lab.get('hold#intro#b1')['status'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_indexed_due_lookup_ignores_unrelated_items_and_releases_once(self):
        self.seed_holds()
        for n in range(22):
            self.db.put_item(TableName='test-lab', Item={'pk': f'filler#{n}', 'kind': 'fixture'})
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.assertEqual(0, self.lab.query_due_holds(9)['index_items'])
        result = self.lab.query_due_holds(10)
        self.assertEqual(1, result['index_items'])
        self.assertEqual(1, result['expired'])
        self.assertIsNotNone(result['query_capacity_units'])
        self.assertNotIn('due_partition', self.lab.get('hold#intro#a1'))
        self.assertEqual(0, self.lab.query_due_holds(10)['index_items'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_indexed_result_rechecks_base_after_other_worker_releases(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        query = self.db.query
        def other_worker_releases(**kwargs):
            page = query(**kwargs)
            self.lab.transition_hold('intro', 'a1', 'expire', 10)
            return page
        with patch.object(self.db, 'query', side_effect=other_worker_releases):
            result = self.lab.query_due_holds(10)
        self.assertEqual(0, result['expired'])
        self.assertEqual(1, result['already_changed'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_indexed_due_lookup_follows_page_cursor(self):
        self.seed_holds(seats=7)
        for n in range(7):
            self.lab.acquire_hold('intro', f'actor{n}', f'h{n}', 10, 0)
        first = self.lab.query_due_holds(10)
        self.assertEqual(5, first['index_items'])
        self.assertIn('next_cursor', first)
        second = self.lab.query_due_holds(10, first['next_cursor'])
        self.assertEqual(2, second['index_items'])
        self.assertNotIn('next_cursor', second)
        self.assertEqual(7, first['expired'] + second['expired'])
        self.assertEqual(7, self.lab.get('course#intro')['remaining'])

    def test_bounded_index_tick_reaches_three_pages_then_requires_another_pass(self):
        self.seed_holds(seats=16)
        for n in range(16):
            self.lab.acquire_hold('intro', f'actor{n}', f'h{n}', 10, 0)
        first = self.lab.query_due_tick(10)
        self.assertEqual(3, first['pages'])
        self.assertEqual(15, first['index_items'])
        self.assertEqual(15, first['expired'])
        self.assertTrue(first['page_limit_reached'])
        self.assertEqual(15, self.lab.get('course#intro')['remaining'])
        second = self.lab.query_due_tick(10)
        self.assertEqual(1, second['expired'])
        self.assertFalse(second['page_limit_reached'])
        self.assertEqual(16, self.lab.get('course#intro')['remaining'])

    def test_index_tick_failure_does_not_report_complete_and_retry_is_safe(self):
        self.seed_holds(seats=7)
        for n in range(7):
            self.lab.acquire_hold('intro', f'actor{n}', f'h{n}', 10, 0)
        process = self.lab._process_due_index_page
        calls = 0

        def fail_second_page(page, now):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError('Injected second-page failure')
            return process(page, now)

        with patch.object(self.lab, '_process_due_index_page', side_effect=fail_second_page):
            with self.assertRaisesRegex(RuntimeError, 'second-page failure'):
                self.lab.query_due_tick(10)
        self.assertEqual(5, self.lab.get('course#intro')['remaining'])
        retry = self.lab.query_due_tick(10)
        self.assertEqual(2, retry['expired'])
        self.assertFalse(retry['page_limit_reached'])
        self.assertEqual(7, self.lab.get('course#intro')['remaining'])

    def test_pre_index_hold_requires_reconciliation_scan(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.db.update_item(TableName='test-lab', Key={'pk': 'hold#intro#a1'},
                            UpdateExpression='REMOVE due_partition')
        self.assertEqual(0, self.lab.query_due_holds(10)['index_items'])
        cursor, expired = None, 0
        for _ in range(4):
            page = self.lab.sweep_due_holds(10, cursor)
            expired += page['expired']
            cursor = page.get('next_cursor')
            if not cursor:
                break
        self.assertEqual(1, expired)
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_second_sweeper_observes_first_release_after_scan(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        scan = self.db.scan
        def other_worker_releases(**kwargs):
            page = scan(**kwargs)
            self.lab.transition_hold('intro', 'a1', 'expire', 10)
            return page
        with patch.object(self.db, 'scan', side_effect=other_worker_releases):
            result = self.lab.sweep_due_holds(10)
        self.assertEqual(0, result['expired'])
        self.assertEqual(1, result['already_changed'])
        self.assertEqual(1, self.lab.get('course#intro')['remaining'])

    def test_sweep_failure_stops_before_reporting_page_complete(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 0)
        self.db.update_item(TableName='test-lab', Key={'pk': 'course#intro'},
                            UpdateExpression='SET remaining = :one',
                            ExpressionAttributeValues={':one': 1})
        with self.assertRaises(RuntimeError):
            self.lab.sweep_due_holds(10)
        self.assertEqual('HELD', self.lab.get('hold#intro#a1')['status'])
        self.db.update_item(TableName='test-lab', Key={'pk': 'course#intro'},
                            UpdateExpression='SET remaining = :zero',
                            ExpressionAttributeValues={':zero': 0})
        self.assertEqual(1, self.lab.sweep_due_holds(10)['expired'])

    def test_private_handler_uses_its_clock_not_event_clock(self):
        self.seed_holds()
        with patch.dict(os.environ, {'TABLE_NAME': 'test-lab', 'QUEUE_URL': self.queue,
                                     'EXPIRES_AT_EPOCH': '1000', 'AWS_DEFAULT_REGION': 'us-east-2'}):
            handlers = importlib.import_module('handlers')
            with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=100):
                result = handlers.reservation({'action': 'acquire_hold', 'course': 'intro',
                                               'actor': 'alice', 'hold_id': 'a1',
                                               'duration_seconds': 10, 'now': 0}, None)
                self.assertEqual('HELD', result['status'])
                self.assertEqual(110, self.lab.get('hold#intro#a1')['expires_at'])
            with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=110):
                self.assertEqual('EXPIRED_NEEDS_RELEASE',
                                 handlers.reservation({'action': 'confirm', 'course': 'intro',
                                                       'hold_id': 'a1', 'now': 101}, None)['status'])
                self.assertEqual(1, handlers.reservation({'action': 'sweep_due', 'now': 0}, None)['expired'])
                self.assertEqual(1, self.lab.get('course#intro')['remaining'])
            sys.modules.pop('handlers', None)

    def test_private_query_tick_uses_handler_clock_not_event_clock(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 100)
        with patch.dict(os.environ, {'TABLE_NAME': 'test-lab', 'QUEUE_URL': self.queue,
                                     'EXPIRES_AT_EPOCH': '1000', 'AWS_DEFAULT_REGION': 'us-east-2'}):
            handlers = importlib.import_module('handlers')
            with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=109):
                self.assertEqual(0, handlers.reservation({'action': 'query_due_tick', 'now': 999}, None)['expired'])
            with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=110):
                result = handlers.reservation({'action': 'query_due_tick', 'now': 0}, None)
                self.assertEqual(1, result['expired'])
                self.assertFalse(result['page_limit_reached'])
                self.assertEqual(1, self.lab.get('course#intro')['remaining'])
            sys.modules.pop('handlers', None)

    def test_dedicated_scheduled_handler_uses_its_clock_and_releases_once(self):
        self.seed_holds()
        self.lab.acquire_hold('intro', 'alice', 'a1', 10, 100)
        with patch.dict(os.environ, {'TABLE_NAME': 'test-lab', 'QUEUE_URL': self.queue,
                                     'EXPIRES_AT_EPOCH': '1000', 'AWS_DEFAULT_REGION': 'us-east-2'}):
            handlers = importlib.import_module('handlers')
            with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=110):
                self.assertEqual(1, handlers.due_tick({'now': 0}, None)['expired'])
                self.assertEqual(0, handlers.due_tick({'now': 999}, None)['expired'])
            self.assertEqual(1, self.lab.get('course#intro')['remaining'])
            sys.modules.pop('handlers', None)

    def test_private_contact_handler_uses_server_clock_and_keeps_work_after_lost_reply(self):
        request = self.lab.submit('alice', 'r1', 'heater', now=100)
        with patch.dict(os.environ, {'TABLE_NAME': 'test-lab', 'QUEUE_URL': self.queue,
                                     'EXPIRES_AT_EPOCH': '5000', 'AWS_DEFAULT_REGION': 'us-east-2'}):
            handlers = importlib.import_module('handlers')
            try:
                with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=3700):
                    self.assertEqual([], handlers.contact_worklist(
                        {'action': 'check_due', 'now': 999999}, None)['newly_opened'])
                with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=3701):
                    self.assertEqual([request['pk']], [row['request'] for row in
                        handlers.contact_worklist({'action': 'check_due', 'now': 0}, None)['newly_opened']])
                    self.assertEqual([], handlers.contact_worklist(
                        {'action': 'check_due'}, None)['newly_opened'])
                    self.assertEqual([request['pk']], [row['request'] for row in
                        handlers.contact_worklist({'action': 'read_open'}, None)['items']])
                    with self.assertRaises(ValueError):
                        handlers.contact_worklist({'action': 'record_contact', 'actor': 'alice'}, None)
                with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=5000):
                    with self.assertRaisesRegex(RuntimeError, 'Lab expired'):
                        handlers.contact_worklist({'action': 'read_open'}, None)
            finally:
                sys.modules.pop('handlers', None)

    def test_private_contact_handler_follows_empty_and_nonempty_scan_pages(self):
        for number in range(25):
            self.lab.submit('alice', f'r{number:02}', 'heater', now=0)
        with patch.dict(os.environ, {'TABLE_NAME': 'test-lab', 'QUEUE_URL': self.queue,
                                     'EXPIRES_AT_EPOCH': '5000', 'AWS_DEFAULT_REGION': 'us-east-2'}):
            handlers = importlib.import_module('handlers')
            try:
                with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=3601):
                    cursor, opened, checks = None, [], 0
                    while True:
                        page = handlers.contact_worklist({'action': 'check_due', 'cursor': cursor}, None)
                        checks += 1
                        opened.extend(page['newly_opened'])
                        cursor = page.get('next_cursor')
                        if cursor is None:
                            break
                        json.dumps(cursor)  # The next private invocation can carry this cursor.
                    self.assertGreater(checks, 1)
                    self.assertEqual(25, len(opened))
                    self.assertEqual(25, len({row['request'] for row in opened}))
                    cursor, work, reads = None, [], 0
                    while True:
                        page = handlers.contact_worklist({'action': 'read_open', 'cursor': cursor}, None)
                        reads += 1
                        work.extend(page['items'])
                        cursor = page.get('next_cursor')
                        if cursor is None:
                            break
                    self.assertGreater(reads, 1)
                    self.assertEqual({row['request'] for row in opened},
                                     {row['request'] for row in work})
            finally:
                sys.modules.pop('handlers', None)

    def test_contact_worklist_does_not_fetch_request_description(self):
        request = self.lab.submit('alice', 'private', 'invented sensitive repair detail', now=0)
        scan = self.db.scan
        get_item = self.db.get_item

        def checked_scan(**kwargs):
            response = scan(**kwargs)
            self.assertTrue(all('text' not in item for item in response['Items']))
            return response

        def checked_get(**kwargs):
            response = get_item(**kwargs)
            self.assertNotIn('text', response.get('Item', {}))
            return response

        with patch.object(self.db, 'scan', side_effect=checked_scan), \
                patch.object(self.db, 'get_item', side_effect=checked_get):
            self.assertEqual([request['pk']], [row['request'] for row in
                self.lab.check_contact_due(3601)['newly_opened']])
            self.assertEqual([request['pk']], [row['request'] for row in
                self.lab.read_open_contacts()['items']])

    def test_contact_capacity_trace_counts_attempts_without_customer_text(self):
        request = self.lab.submit('alice', 'private', 'invented sensitive repair detail', now=0)
        due_trace = []
        first = self.lab.check_contact_due(3601, trace=due_trace)
        self.assertEqual([request['pk']], [row['request'] for row in first['newly_opened']])
        self.assertEqual(['contact_due_scan', 'contact_due_transaction'],
                         [row['operation'] for row in due_trace])
        repeated_trace = []
        self.assertEqual([], self.lab.check_contact_due(3602, trace=repeated_trace)['newly_opened'])
        self.assertEqual('canceled', repeated_trace[-1]['outcome'])
        work_trace = []
        self.assertEqual([request['pk']], [row['request'] for row in
                         self.lab.read_open_contacts(trace=work_trace)['items']])
        self.assertEqual(['contact_worklist_scan', 'contact_worklist_contact_read',
                          'contact_worklist_request_read'],
                         [row['operation'] for row in work_trace])
        for row in due_trace + repeated_trace + work_trace:
            self.assertLessEqual(set(row), {'operation', 'outcome', 'reported',
                                            'total_capacity_units', 'read_capacity_units',
                                            'write_capacity_units'})
            self.assertNotIn('invented sensitive repair detail', str(row))
        contact_trace = []
        self.lab.record_first_contact('alice', 'private', 4000, trace=contact_trace)
        self.assertEqual(['first_contact_request_read', 'first_contact_transaction',
                          'first_contact_confirm_read'],
                         [row['operation'] for row in contact_trace])

    def test_missing_capacity_is_unknown_and_reported_amounts_are_numeric(self):
        trace = []
        self.lab.record_capacity(trace, 'contact_due_transaction', {}, 'canceled')
        self.assertEqual({'operation': 'contact_due_transaction', 'outcome': 'canceled',
                          'reported': False}, trace[0])
        self.lab.record_capacity(trace, 'contact_due_transaction',
                                 {'ConsumedCapacity': [{'CapacityUnits': 2,
                                                        'ReadCapacityUnits': 1,
                                                        'WriteCapacityUnits': 1}]})
        self.assertEqual('2', trace[1]['total_capacity_units'])
        self.assertTrue(trace[1]['reported'])
        self.lab.record_capacity(trace, 'contact_due_scan', {'ConsumedCapacity': {}})
        self.assertFalse(trace[2]['reported'])

    def test_private_contact_handler_returns_scoped_capacity_observations(self):
        self.lab.submit('alice', 'private', 'invented sensitive repair detail', now=0)
        with patch.dict(os.environ, {'TABLE_NAME': 'test-lab', 'QUEUE_URL': self.queue,
                                     'EXPIRES_AT_EPOCH': '5000', 'AWS_DEFAULT_REGION': 'us-east-2'}):
            handlers = importlib.import_module('handlers')
            try:
                with patch.object(handlers, 'lab', self.lab), patch('handlers.time.time', return_value=3601):
                    result = handlers.contact_worklist({'action': 'check_due'}, None)
                    self.assertEqual(['contact_due_scan', 'contact_due_transaction'],
                                     [row['operation'] for row in result['capacity_observations']])
                    self.assertNotIn('invented sensitive repair detail', json.dumps(result))
                    work = handlers.contact_worklist({'action': 'read_open'}, None)
                    self.assertEqual(['contact_worklist_scan', 'contact_worklist_contact_read',
                                      'contact_worklist_request_read'],
                                     [row['operation'] for row in work['capacity_observations']])
                    json.dumps(work)
            finally:
                sys.modules.pop('handlers', None)


if __name__ == '__main__':
    unittest.main()
