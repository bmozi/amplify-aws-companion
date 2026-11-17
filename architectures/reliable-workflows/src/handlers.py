"""IAM-invoked lab handlers; no public endpoint or customer authentication layer."""
import os
import time
import boto3
from botocore.config import Config
from domain import Lab

config = Config(connect_timeout=2, read_timeout=3,
                retries={'mode': 'standard', 'total_max_attempts': 2})
db = boto3.resource('dynamodb', config=config).meta.client
sqs = boto3.client('sqs', config=config)
lab = Lab(db, os.environ['TABLE_NAME'], sqs, os.environ['QUEUE_URL'])


def active():
    if time.time() >= int(os.environ["EXPIRES_AT_EPOCH"]):
        raise RuntimeError("Lab expired; destroy resources to end retained-resource charges")


def intake(event, context):
    active()
    return lab.submit(event['actor'], event['request_id'], event['text'])


def dispatcher(event, context):
    active()
    return lab.dispatch(event.get('fail_after_send', False), event.get('cursor'))


def worker(event, context):
    active()
    return lab.batch(event['Records'])


def reservation(event, context):
    active()
    action = event.get('action', 'reserve')
    if action == 'acquire_hold':
        return lab.acquire_hold(event['course'], event['actor'], event['hold_id'],
                                event['duration_seconds'], int(time.time()))
    if action in {'confirm', 'expire', 'cancel'}:
        return lab.transition_hold(event['course'], event['hold_id'], action, int(time.time()))
    if action == 'sweep_due':
        return lab.sweep_due_holds(int(time.time()), event.get('cursor'))
    if action == 'query_due':
        return lab.query_due_holds(int(time.time()), event.get('cursor'))
    if action == 'query_due_tick':
        return lab.query_due_tick(int(time.time()))
    if action != 'reserve':
        raise ValueError('Unknown reservation action')
    return lab.reserve(event['course'], event['actor'])


def due_tick(event, context):
    """Private scheduled target: never accept a caller-supplied business clock."""
    active()
    return lab.query_due_tick(int(time.time()))


def contact_worklist(event, context):
    """Private manual contact review; no customer message or contact assertion."""
    active()
    action = event.get('action')
    capacity_observations = []
    if action == 'check_due':
        # A caller cannot move the deadline by supplying an event clock.
        result = lab.check_contact_due(int(time.time()), event.get('cursor'),
                                       trace=capacity_observations)
        return {**result, 'capacity_observations': capacity_observations}
    if action == 'read_open':
        result = lab.read_open_contacts(event.get('cursor'), trace=capacity_observations)
        return {**result, 'capacity_observations': capacity_observations}
    raise ValueError('Use check_due or read_open for the private contact worklist')
