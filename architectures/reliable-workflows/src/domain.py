"""Private teaching services. Actor labels are trusted operator fixtures, not login identities."""
import hashlib
import json
import re
import time
import random
from decimal import Decimal


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', value):
        raise ValueError('Identifiers must contain 1–64 letters, digits, underscores or hyphens')
    return value


class Lab:
    def __init__(self, db, table, sqs, queue):
        self.db, self.table, self.sqs, self.queue = db, table, sqs, queue

    @staticmethod
    def record_capacity(trace, operation, response, outcome='succeeded'):
        """Keep only numeric meter evidence; missing capacity is not zero."""
        if trace is None:
            return
        raw = response.get('ConsumedCapacity') if isinstance(response, dict) else None
        rows = raw if isinstance(raw, list) else [raw] if isinstance(raw, dict) else []
        record = {'operation': operation, 'outcome': outcome, 'reported': False}
        if rows:
            for source, target in (('CapacityUnits', 'total_capacity_units'),
                                   ('ReadCapacityUnits', 'read_capacity_units'),
                                   ('WriteCapacityUnits', 'write_capacity_units')):
                values = [Decimal(str(row[source])) for row in rows if source in row]
                if values:
                    record[target] = str(sum(values))
                    record['reported'] = True
        trace.append(record)

    def get(self, pk, *, trace=None, operation='get_item'):
        parameters = {'TableName': self.table, 'Key': {'pk': pk}, 'ConsistentRead': True}
        if trace is not None:
            parameters['ReturnConsumedCapacity'] = 'TOTAL'
        response = self.db.get_item(**parameters)
        self.record_capacity(trace, operation, response)
        return response.get('Item')

    def put(self, item):
        return {'Put': {'TableName': self.table, 'Item': item,
                        'ConditionExpression': 'attribute_not_exists(pk)'}}

    def transaction(self, items, *, trace=None, operation='transaction'):
        # A transaction conflict is transient. A failed business condition is not.
        for attempt in range(5):
            try:
                parameters = {'TransactItems': items}
                if trace is not None:
                    parameters['ReturnConsumedCapacity'] = 'TOTAL'
                response = self.db.transact_write_items(**parameters)
                self.record_capacity(trace, operation, response)
                return True
            except self.db.exceptions.TransactionCanceledException as exc:
                self.record_capacity(trace, operation, exc.response, 'canceled')
                codes = {r.get('Code') for r in exc.response.get('CancellationReasons', [])}
                if 'ConditionalCheckFailed' in codes:
                    return False
                if 'TransactionConflict' not in codes or attempt == 4:
                    raise
                time.sleep(random.uniform(0.02, 0.06) * (2 ** attempt))

    def submit(self, actor, request_id, text, now=None):
        actor, request_id = identifier(actor), identifier(request_id)
        if not isinstance(text, str) or not 1 <= len(text.encode()) <= 500:
            raise ValueError('Use 1–500 UTF-8 bytes of invented request text')
        # Sample on the trusted server before the acceptance transaction.
        # This is an authored clock, not proof of the remote commit instant.
        if now is None:
            now = int(time.time())
        if type(now) is not int or now < 0:
            raise ValueError('Use a trusted nonnegative integer second')
        key = f'request#{actor}#{request_id}'
        fingerprint = hashlib.sha256(text.encode()).hexdigest()
        item = {'pk': key, 'kind': 'request', 'fingerprint': fingerprint,
                'status': 'ACCEPTED', 'actor': actor, 'text': text,
                'accepted_at': now}
        if not self.transaction([self.put(item), self.put({
            'pk': 'outbox#' + key, 'kind': 'outbox', 'request': key, 'sent': False})]):
            existing = self.get(key)
            if not existing or existing['fingerprint'] != fingerprint:
                raise ValueError('Request ID already used with different content')
        return self.get(key)

    def record_first_contact(self, actor, request_id, now, *, trace=None):
        """Private operator fixture; a stored time does not prove human contact."""
        actor, request_id = identifier(actor), identifier(request_id)
        if type(now) is not int or now < 0:
            raise ValueError('Use a trusted nonnegative integer second')
        request_key = f'request#{actor}#{request_id}'
        request = self.get(request_key, trace=trace, operation='first_contact_request_read')
        if not request or request.get('kind') != 'request' or 'accepted_at' not in request:
            raise ValueError('Contact requires a timestamped accepted request')
        accepted_at = int(request['accepted_at'])
        if now < accepted_at:
            raise ValueError('Contact cannot precede acceptance')
        contact_key = 'contact#' + request_key
        self.transaction([self.put({'pk': contact_key, 'kind': 'contact',
                                    'request': request_key, 'contacted_at': now})],
                         trace=trace, operation='first_contact_transaction')
        first = int(self.get(contact_key, trace=trace,
                             operation='first_contact_confirm_read')['contacted_at'])
        return {'request': request_key, 'first_contact_at': first,
                'met_one_hour_promise': first <= accepted_at + 3600}

    def check_contact_due(self, now, cursor=None, *, trace=None):
        """Manual page of newly opened work; an empty page may have a cursor."""
        if type(now) is not int or now < 0:
            raise ValueError('Use a trusted nonnegative integer second')
        parameters = {'TableName': self.table, 'Limit': 20, 'ConsistentRead': True,
                      'FilterExpression': '#k = :request',
                      'ProjectionExpression': 'pk,accepted_at',
                      'ExpressionAttributeNames': {'#k': 'kind'},
                      'ExpressionAttributeValues': {':request': 'request'}}
        if trace is not None:
            parameters['ReturnConsumedCapacity'] = 'TOTAL'
        if cursor:
            parameters['ExclusiveStartKey'] = cursor
        page = self.db.scan(**parameters)
        self.record_capacity(trace, 'contact_due_scan', page)
        opened, unknown = [], []
        for request in page['Items']:
            key = request['pk']
            if 'accepted_at' not in request:
                unknown.append(key)
                continue
            accepted_at = int(request['accepted_at'])
            deadline = accepted_at + 3600
            if now <= deadline:
                continue
            # Recheck contact in the write transaction, so an on-time contact
            # committed before the check cannot also open overdue work.
            created = self.transaction([
                {'ConditionCheck': {'TableName': self.table,
                                    'Key': {'pk': 'contact#' + key},
                                    'ConditionExpression': 'attribute_not_exists(pk) OR contacted_at > :deadline',
                                    'ExpressionAttributeValues': {':deadline': deadline}}},
                self.put({'pk': 'escalation#' + key, 'kind': 'escalation',
                          'request': key, 'opened_at': now})],
                                       trace=trace, operation='contact_due_transaction')
            if created:
                opened.append({'request': key, 'accepted_at': accepted_at,
                               'deadline_at': deadline})
        result = {'newly_opened': opened, 'unknown_acceptance_time': unknown}
        if page.get('LastEvaluatedKey'):
            result['next_cursor'] = page['LastEvaluatedKey']
        return result

    def read_open_contacts(self, cursor=None, *, trace=None):
        """Independent worklist read after a lost check reply or a restart."""
        parameters = {'TableName': self.table, 'Limit': 20, 'ConsistentRead': True,
                      'FilterExpression': '#k = :escalation',
                      'ProjectionExpression': '#r,opened_at',
                      'ExpressionAttributeNames': {'#k': 'kind', '#r': 'request'},
                      'ExpressionAttributeValues': {':escalation': 'escalation'}}
        if trace is not None:
            parameters['ReturnConsumedCapacity'] = 'TOTAL'
        if cursor:
            parameters['ExclusiveStartKey'] = cursor
        page = self.db.scan(**parameters)
        self.record_capacity(trace, 'contact_worklist_scan', page)
        open_items = []
        for escalation in page['Items']:
            if self.get('contact#' + escalation['request'], trace=trace,
                        operation='contact_worklist_contact_read'):
                continue
            # This operator view needs the clock, not the customer's free text.
            parameters = {'TableName': self.table, 'Key': {'pk': escalation['request']},
                          'ConsistentRead': True, 'ProjectionExpression': 'accepted_at'}
            if trace is not None:
                parameters['ReturnConsumedCapacity'] = 'TOTAL'
            response = self.db.get_item(**parameters)
            self.record_capacity(trace, 'contact_worklist_request_read', response)
            request = response.get('Item')
            if not request or 'accepted_at' not in request:
                raise RuntimeError('Escalation lacks its timestamped request; investigate')
            accepted_at = int(request['accepted_at'])
            open_items.append({'request': escalation['request'], 'accepted_at': accepted_at,
                               'deadline_at': accepted_at + 3600,
                               'opened_at': int(escalation['opened_at'])})
        result = {'items': open_items}
        if page.get('LastEvaluatedKey'):
            result['next_cursor'] = page['LastEvaluatedKey']
        return result

    def dispatch(self, fail_after_send=False, cursor=None):
        # One bounded page of evaluated items. Follow next_cursor explicitly.
        parameters = {'TableName': self.table, 'Limit': 20, 'ConsistentRead': True,
                      'ReturnConsumedCapacity': 'TOTAL',
                      'FilterExpression': '#k = :k AND sent = :false',
                      'ExpressionAttributeNames': {'#k': 'kind'},
                      'ExpressionAttributeValues': {':k': 'outbox', ':false': False}}
        if cursor:
            parameters['ExclusiveStartKey'] = cursor
        page = self.db.scan(**parameters)
        count = 0
        for item in page['Items']:
            self.sqs.send_message(QueueUrl=self.queue, MessageBody=json.dumps({'request': item['request']}))
            if fail_after_send:
                raise RuntimeError('Teaching failure after send, before outbox acknowledgement')
            self.db.update_item(TableName=self.table, Key={'pk': item['pk']},
                                UpdateExpression='SET sent = :yes',
                                ExpressionAttributeValues={':yes': True})
            count += 1
        result = {'sent': count}
        if page.get('LastEvaluatedKey'):
            result['next_cursor'] = page['LastEvaluatedKey']
        return result

    def process(self, request_key):
        item = self.get(request_key)
        if not item or item.get('kind') != 'request':
            raise ValueError('Unknown request')
        if item['status'] == 'DONE':
            return 'duplicate'
        control = self.get('control#scheduler')
        if control and control.get('unavailable'):
            raise RuntimeError('Simulated scheduling dependency unavailable')
        # The appointment is a SIMULATED business effect in this SAME transaction.
        # A real external scheduler needs its own idempotency/reconciliation contract.
        ok = self.transaction([
            self.put({'pk': 'appointment#' + request_key, 'kind': 'appointment', 'request': request_key}),
            {'Update': {'TableName': self.table, 'Key': {'pk': request_key},
                        'UpdateExpression': 'SET #s = :done', 'ConditionExpression': '#s = :accepted',
                        'ExpressionAttributeNames': {'#s': 'status'},
                        'ExpressionAttributeValues': {':done': 'DONE', ':accepted': 'ACCEPTED'}}}])
        if not ok and self.get(request_key)['status'] != 'DONE':
            raise RuntimeError('Unexpected request state; investigation required')
        return 'created' if ok else 'duplicate'

    def batch(self, records):
        failures = []
        for record in records:
            try:
                self.process(json.loads(record['body'])['request'])
            except Exception as exc:
                # SQS needs failed message IDs, not a falsely successful whole batch.
                print(json.dumps({'event': 'work_failed', 'error_type': type(exc).__name__}))
                failures.append({'itemIdentifier': record['messageId']})
        return {'batchItemFailures': failures}

    def reserve(self, course, actor):
        course, actor = identifier(course), identifier(actor)
        key = f'reservation#{course}#{actor}'
        existing = self.get(key)
        if existing:
            return {'status': 'CONFIRMED', 'replayed': True, 'reservation': key}
        ok = self.transaction([
            {'Update': {'TableName': self.table, 'Key': {'pk': 'course#' + course},
                        'UpdateExpression': 'SET remaining = remaining - :one',
                        'ConditionExpression': 'remaining >= :one AND (attribute_not_exists(#m) OR #m = :immediate)',
                        'ExpressionAttributeNames': {'#m': 'mode'},
                        'ExpressionAttributeValues': {':one': 1, ':immediate': 'immediate'}}},
            self.put({'pk': key, 'kind': 'reservation', 'course': course, 'actor': actor})])
        if ok:
            return {'status': 'CONFIRMED', 'replayed': False, 'reservation': key}
        if self.get(key):
            return {'status': 'CONFIRMED', 'replayed': True, 'reservation': key}
        course_item = self.get('course#' + course)
        if not course_item:
            raise ValueError('Unknown course')
        if course_item.get('mode', 'immediate') != 'immediate':
            raise ValueError('Course does not use immediate reservations')
        if course_item['remaining'] < 1:
            return {'status': 'SOLD_OUT'}
        raise RuntimeError('Reservation condition failed with capacity available; investigate')

    # The hold contract is separate from reserve(): it has a different key and state.
    # now is supplied by a trusted handler/test, never by a customer event.
    def acquire_hold(self, course, actor, hold_id, duration_seconds, now):
        course, actor, hold_id = identifier(course), identifier(actor), identifier(hold_id)
        if type(now) is not int or now < 0 or type(duration_seconds) is not int or not 1 <= duration_seconds <= 600:
            raise ValueError('Use trusted nonnegative seconds and a 1–600 second hold')
        key, claim = f'hold#{course}#{hold_id}', f'claim#{course}#{actor}'
        existing = self.get(key)
        if existing:
            if existing['actor'] != actor or existing['duration_seconds'] != duration_seconds:
                raise ValueError('Hold ID reused with different intent')
            return {'status': existing['status'], 'hold': key, 'replayed': True}
        ok = self.transaction([
            {'Update': {'TableName': self.table, 'Key': {'pk': 'course#' + course},
                        'UpdateExpression': 'SET remaining = remaining - :one',
                        'ConditionExpression': 'remaining >= :one AND #m = :holds AND attribute_exists(#cap)',
                        'ExpressionAttributeNames': {'#m': 'mode', '#cap': 'capacity'},
                        'ExpressionAttributeValues': {':one': 1, ':holds': 'holds'}}},
            self.put({'pk': key, 'kind': 'hold', 'due_partition': 'HELD',
                      'course': course, 'actor': actor,
                      'hold_id': hold_id, 'duration_seconds': duration_seconds,
                      'expires_at': now + duration_seconds, 'status': 'HELD'}),
            self.put({'pk': claim, 'kind': 'claim', 'hold': key, 'status': 'HELD'})])
        if ok:
            return {'status': 'HELD', 'hold': key, 'replayed': False}
        existing = self.get(key)
        if existing:
            if existing['actor'] != actor or existing['duration_seconds'] != duration_seconds:
                raise ValueError('Hold ID reused with different intent')
            return {'status': existing['status'], 'hold': key, 'replayed': True}
        current_claim = self.get(claim)
        if current_claim:
            return {'status': 'ACTIVE_CLAIM', 'hold': current_claim['hold']}
        course_item = self.get('course#' + course)
        if not course_item:
            raise ValueError('Unknown course')
        if course_item.get('mode') != 'holds':
            raise ValueError('Course does not use expiring holds')
        if 'capacity' not in course_item:
            raise RuntimeError('Hold course has no configured capacity')
        if course_item['remaining'] < 1:
            return {'status': 'SOLD_OUT'}
        raise RuntimeError('Hold condition failed with capacity available; investigate')

    def transition_hold(self, course, hold_id, action, now):
        course, hold_id = identifier(course), identifier(hold_id)
        if action not in {'confirm', 'expire', 'cancel'} or type(now) is not int or now < 0:
            raise ValueError('Invalid hold action or trusted time')
        key = f'hold#{course}#{hold_id}'
        hold = self.get(key)
        if not hold or hold.get('kind') != 'hold':
            raise ValueError('Unknown hold')
        if hold['status'] != 'HELD':
            return {'status': hold['status'], 'replayed': True}
        if action in {'confirm', 'cancel'} and now >= hold['expires_at']:
            return {'status': 'EXPIRED_NEEDS_RELEASE', 'replayed': False}
        if action == 'expire' and now < hold['expires_at']:
            return {'status': 'NOT_DUE', 'replayed': False}
        claim = f"claim#{course}#{hold['actor']}"
        target = {'confirm': 'CONFIRMED', 'expire': 'EXPIRED', 'cancel': 'CANCELLED'}[action]
        time_condition = ' AND expires_at > :now' if action == 'confirm' else (
            ' AND expires_at <= :now' if action == 'expire' else '')
        values = {':held': 'HELD', ':target': target}
        if time_condition:
            values[':now'] = now
        items = [{'Update': {'TableName': self.table, 'Key': {'pk': key},
                             'UpdateExpression': 'SET #s = :target REMOVE due_partition',
                             'ConditionExpression': '#s = :held' + time_condition,
                             'ExpressionAttributeNames': {'#s': 'status'},
                             'ExpressionAttributeValues': values}}]
        if action == 'confirm':
            items.append({'ConditionCheck': {'TableName': self.table, 'Key': {'pk': 'course#' + course},
                                             'ConditionExpression': '#m = :holds',
                                             'ExpressionAttributeNames': {'#m': 'mode'},
                                             'ExpressionAttributeValues': {':holds': 'holds'}}})
            items.append({'Update': {'TableName': self.table, 'Key': {'pk': claim},
                                     'UpdateExpression': 'SET #s = :target',
                                     'ConditionExpression': '#h = :hold AND #s = :held',
                                     'ExpressionAttributeNames': {'#s': 'status', '#h': 'hold'},
                                     'ExpressionAttributeValues': {':target': target, ':held': 'HELD', ':hold': key}}})
        else:
            items.extend([
                {'Update': {'TableName': self.table, 'Key': {'pk': 'course#' + course},
                            'UpdateExpression': 'SET remaining = remaining + :one',
                            'ConditionExpression': 'attribute_exists(pk) AND #m = :holds AND remaining < #cap',
                            'ExpressionAttributeNames': {'#cap': 'capacity', '#m': 'mode'},
                            'ExpressionAttributeValues': {':one': 1, ':holds': 'holds'}}},
                {'Delete': {'TableName': self.table, 'Key': {'pk': claim},
                            'ConditionExpression': '#h = :hold AND #s = :held',
                            'ExpressionAttributeNames': {'#s': 'status', '#h': 'hold'},
                            'ExpressionAttributeValues': {':hold': key, ':held': 'HELD'}}}])
        if self.transaction(items):
            return {'status': target, 'replayed': False}
        current = self.get(key)
        if not current:
            raise RuntimeError('Hold disappeared during transition; investigate')
        if current['status'] != 'HELD':
            return {'status': current['status'], 'replayed': True}
        if action in {'confirm', 'cancel'} and now >= current['expires_at']:
            return {'status': 'EXPIRED_NEEDS_RELEASE', 'replayed': False}
        raise RuntimeError('Hold transition unresolved; inspect claim and course')

    def sweep_due_holds(self, now, cursor=None):
        """Inspect one bounded table page; caller owns pagination and repeated runs."""
        if type(now) is not int or now < 0:
            raise ValueError('Use trusted nonnegative seconds')
        parameters = {'TableName': self.table, 'Limit': 5, 'ConsistentRead': True,
                      'ReturnConsumedCapacity': 'TOTAL',
                      'FilterExpression': '#k = :hold AND #s = :held AND expires_at <= :now',
                      'ExpressionAttributeNames': {'#k': 'kind', '#s': 'status'},
                      'ExpressionAttributeValues': {':hold': 'hold', ':held': 'HELD', ':now': now}}
        if cursor:
            parameters['ExclusiveStartKey'] = cursor
        page = self.db.scan(**parameters)
        consumed = page.get('ConsumedCapacity', {}).get('CapacityUnits')
        result = {'evaluated': page['ScannedCount'], 'matched': len(page['Items']),
                  'expired': 0, 'already_changed': 0,
                  'scan_capacity_units': str(consumed) if consumed is not None else None}
        for item in page['Items']:
            outcome = self.transition_hold(item['course'], item['hold_id'], 'expire', now)
            if outcome['status'] == 'EXPIRED' and not outcome['replayed']:
                result['expired'] += 1
            elif outcome['status'] in {'EXPIRED', 'CONFIRMED', 'CANCELLED'} and outcome['replayed']:
                result['already_changed'] += 1
            else:
                raise RuntimeError('Unexpected hold sweep outcome; investigate before advancing')
        if page.get('LastEvaluatedKey'):
            result['next_cursor'] = page['LastEvaluatedKey']
        return result

    def query_due_holds(self, now, cursor=None):
        """One manual sparse-index page; eventual GSI discovery needs repeat passes."""
        if type(now) is not int or now < 0:
            raise ValueError('Use trusted nonnegative seconds')
        parameters = {'TableName': self.table, 'IndexName': 'due-holds', 'Limit': 5,
                      'ReturnConsumedCapacity': 'TOTAL',
                      'KeyConditionExpression': 'due_partition = :held AND expires_at <= :now',
                      'ExpressionAttributeValues': {':held': 'HELD', ':now': now}}
        if cursor:
            parameters['ExclusiveStartKey'] = cursor
        page = self.db.query(**parameters)
        return self._process_due_index_page(page, now)

    def _process_due_index_page(self, page, now):
        """Re-read base records before applying the shared conditional release."""
        consumed = page.get('ConsumedCapacity', {}).get('CapacityUnits')
        result = {'index_items': len(page['Items']), 'expired': 0,
                  'already_changed': 0, 'not_due': 0,
                  'query_capacity_units': str(consumed) if consumed is not None else None}
        for indexed in page['Items']:
            # An index result can lag the base table. Recheck the authoritative item.
            hold = self.get(indexed['pk'])
            if not hold or hold.get('kind') != 'hold':
                raise RuntimeError('Indexed hold missing from base table; investigate')
            if hold['status'] != 'HELD':
                result['already_changed'] += 1
                continue
            if hold['expires_at'] > now:
                result['not_due'] += 1
                continue
            outcome = self.transition_hold(hold['course'], hold['hold_id'], 'expire', now)
            if outcome['status'] == 'EXPIRED' and not outcome['replayed']:
                result['expired'] += 1
            elif outcome['status'] in {'EXPIRED', 'CONFIRMED', 'CANCELLED'} and outcome['replayed']:
                result['already_changed'] += 1
            else:
                raise RuntimeError('Unexpected indexed sweep outcome; investigate before advancing')
        if page.get('LastEvaluatedKey'):
            result['next_cursor'] = page['LastEvaluatedKey']
        return result

    def query_due_tick(self, now):
        """One bounded manual tick: at most three five-key index pages."""
        if type(now) is not int or now < 0:
            raise ValueError('Use trusted nonnegative seconds')
        paginator = self.db.get_paginator('query')
        pages = paginator.paginate(
            TableName=self.table, IndexName='due-holds',
            ReturnConsumedCapacity='TOTAL',
            KeyConditionExpression='due_partition = :held AND expires_at <= :now',
            ExpressionAttributeValues={':held': 'HELD', ':now': now},
            PaginationConfig={'PageSize': 5})
        result = {'pages': 0, 'index_items': 0, 'expired': 0,
                  'already_changed': 0, 'not_due': 0,
                  'query_capacity_units': '0', 'page_limit_reached': False}
        for page in pages:
            part = self._process_due_index_page(page, now)
            result['pages'] += 1
            for name in ('index_items', 'expired', 'already_changed', 'not_due'):
                result[name] += part[name]
            if part['query_capacity_units'] is None:
                result['query_capacity_units'] = None
            elif result['query_capacity_units'] is not None:
                result['query_capacity_units'] = str(
                    Decimal(result['query_capacity_units']) + Decimal(part['query_capacity_units']))
            if result['pages'] == 3:
                result['page_limit_reached'] = 'next_cursor' in part
                break
        return result
