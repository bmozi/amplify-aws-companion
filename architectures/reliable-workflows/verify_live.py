"""Bounded live checks for an isolated lab. Creates synthetic data; no production inputs."""

if __name__ == '__main__':
    raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import uuid
import boto3
from botocore.config import Config
from run import require_deployment_role


def claim_outage(db, table, owner):
    """Do not overwrite another operator's outage control."""
    db.put_item(TableName=table,
                Item={'pk': 'control#scheduler', 'unavailable': True, 'test_owner': owner},
                ConditionExpression='attribute_not_exists(pk)')


def release_outage(db, table, owner):
    """A lost claim reply still permits cleanup, but only of our own marker."""
    try:
        db.delete_item(TableName=table, Key={'pk': 'control#scheduler'},
                       ConditionExpression='test_owner = :owner',
                       ExpressionAttributeValues={':owner': owner})
    except db.exceptions.ConditionalCheckFailedException:
        return False  # Absent or owned by somebody else; leave it alone.
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--outputs', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads(args.outputs.read_text())
    if not cfg['name'].startswith('amplify-patterns-'):
        raise ValueError('Unexpected lab namespace')
    if cfg['expires_at_epoch'] - time.time() < 600:
        raise ValueError('At least ten minutes must remain; review expiry before testing')
    session = boto3.Session(profile_name=args.profile, region_name=cfg['region'])
    settings = Config(connect_timeout=3, read_timeout=20, retries={'mode': 'standard', 'total_max_attempts': 4})
    require_deployment_role(session.client('sts', config=settings).get_caller_identity(), cfg['account'])
    fn = session.client('lambda', config=settings)
    sqs = session.client('sqs', config=settings)
    # The table is used by the test operator only; concurrent threads invoke Lambda, not this resource.
    db = session.resource('dynamodb', config=settings).meta.client
    run = uuid.uuid4().hex[:10]
    results = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        results.append({'name': name, 'passed': True})
        print('PASS', name, flush=True)

    def invoke(name, data, expect_error=False):
        response = fn.invoke(FunctionName=cfg['functions'][name], Payload=json.dumps(data).encode())
        payload = json.loads(response['Payload'].read())
        if expect_error:
            check('injected failure surfaced', bool(response.get('FunctionError')))
        elif response.get('FunctionError'):
            raise RuntimeError(payload)
        return payload

    def get(pk):
        return db.get_item(TableName=cfg['table'], Key={'pk': pk}, ConsistentRead=True).get('Item')

    def wait_until(label, predicate, limit=300):
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            value = predicate()
            if value:
                return value
            time.sleep(5)
        raise TimeoutError(label)

    try:
        request = {'actor': 'reader', 'request_id': run, 'text': 'Synthetic heater request'}
        first = invoke('intake', request)
        check('repeated intake retains one request', invoke('intake', request)['pk'] == first['pk'])
        invoke('intake', dict(request, text='changed'), expect_error=True)
        invoke('dispatcher', {'fail_after_send': True}, expect_error=True)
        check('outbox remains pending after send/ack failure', get('outbox#' + first['pk'])['sent'] is False)
        invoke('dispatcher', {})
        wait_until('request completion', lambda: get(first['pk'])['status'] == 'DONE')
        result = invoke('worker', {'Records': [{'messageId': 'replay', 'body': json.dumps({'request': first['pk']})}]})
        check('worker replay succeeds', result['batchItemFailures'] == [])
        check('one durable simulated appointment exists', get('appointment#' + first['pk']) is not None)
        bad = invoke('worker', {'Records': [{'messageId': 'bad', 'body': '{'}, {'messageId': 'good', 'body': json.dumps({'request': first['pk']})}]})
        check('partial batch reports only bad message', bad['batchItemFailures'] == [{'itemIdentifier': 'bad'}])
        course = 'class-' + run
        db.put_item(TableName=cfg['table'], Item={'pk': 'course#' + course, 'remaining': 1}, ConditionExpression='attribute_not_exists(pk)')
        with ThreadPoolExecutor(max_workers=2) as pool:
            contenders = list(pool.map(lambda actor: invoke('reservation', {'course': course, 'actor': actor}), ['alice', 'bob']))
        check('two simultaneous requests produce one winner', sorted(x['status'] for x in contenders) == ['CONFIRMED', 'SOLD_OUT'])
        winner = ['alice', 'bob'][next(i for i, r in enumerate(contenders) if r['status'] == 'CONFIRMED')]
        check('winner replay does not consume a second seat', invoke('reservation', {'course': course, 'actor': winner})['replayed'])
        check('capacity never went negative', int(get('course#' + course)['remaining']) == 0)
        claim_outage(db, cfg['table'], run)
        failed = invoke('intake', dict(request, request_id=run + '-outage'))
        invoke('dispatcher', {})

        def failed_message():
            messages = sqs.receive_message(QueueUrl=cfg['failed_queue'], MaxNumberOfMessages=1, WaitTimeSeconds=1, VisibilityTimeout=300).get('Messages', [])
            if messages:
                msg = messages[0]
                if json.loads(msg['Body']).get('request') != failed['pk']:
                    sqs.change_message_visibility(QueueUrl=cfg['failed_queue'], ReceiptHandle=msg['ReceiptHandle'], VisibilityTimeout=0)
                    raise RuntimeError('Unexpected pre-existing failed work; use a fresh lab')
                return msg
        message = wait_until('bounded retries reach failed-work queue', failed_message)
        check('failed request remains accepted, with no appointment', get(failed['pk'])['status'] == 'ACCEPTED' and get('appointment#' + failed['pk']) is None)
        if not release_outage(db, cfg['table'], run):
            raise RuntimeError('Outage marker ownership changed; stop and inspect the isolated lab')
        sqs.send_message(QueueUrl=cfg['queue'], MessageBody=message['Body'])
        wait_until('recovered request completion', lambda: get(failed['pk'])['status'] == 'DONE')
        sqs.delete_message(QueueUrl=cfg['failed_queue'], ReceiptHandle=message['ReceiptHandle'])
        check('operator replay recovers failed work', get('appointment#' + failed['pk']) is not None)
    finally:
        cleanup = 'unverified'
        try:
            cleanup = 'removed own marker' if release_outage(db, cfg['table'], run) else 'absent or not owned; unchanged'
        finally:
            # Preserve partial evidence even if cleanup itself fails. A cleanup
            # failure still propagates; the receipt is not a successful run claim.
            args.evidence.parent.mkdir(parents=True, exist_ok=True)
            args.evidence.write_text(json.dumps({'at': datetime.now(timezone.utc).isoformat(), 'run': run,
                'scope': 'Private IAM-invoked functions; synthetic actor labels; simulated appointment in DynamoDB',
                'results': results, 'outage_cleanup': cleanup,
                'cleanup': 'Run Terraform destroy and verify absence separately'}, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
