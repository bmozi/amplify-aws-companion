"""Read-only absence checks for exact isolated-lab resources. Not an account-wide audit."""
import argparse
import json
from pathlib import Path
import sys
import boto3
from botocore.config import Config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    parser.add_argument('--outputs', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.outputs.read_text())
    if not data['name'].startswith('amplify-patterns-'):
        raise ValueError('Unexpected lab namespace')
    session = boto3.Session(profile_name=args.profile, region_name=data['region'])
    settings = Config(connect_timeout=3, read_timeout=10, retries={'mode': 'standard', 'total_max_attempts': 2})
    if session.client('sts', config=settings).get_caller_identity()['Account'] != data['account']:
        raise RuntimeError('Wrong account')
    db, fn, sqs, iam, logs = [session.client(s, config=settings) for s in ['dynamodb', 'lambda', 'sqs', 'iam', 'logs']]
    remaining = []
    try:
        db.describe_table(TableName=data['table'])
        remaining.append('table')
    except db.exceptions.ResourceNotFoundException:
        pass
    for name in data['functions'].values():
        try:
            fn.get_function(FunctionName=name)
            remaining.append(name)
        except fn.exceptions.ResourceNotFoundException:
            pass
        try:
            iam.get_role(RoleName=name)
            remaining.append('role:' + name)
        except iam.exceptions.NoSuchEntityException:
            pass
        group = '/aws/lambda/' + name
        for page in logs.get_paginator('describe_log_groups').paginate(logGroupNamePrefix=group):
            remaining.extend('logs:' + g['logGroupName'] for g in page['logGroups'] if g['logGroupName'] == group)
        for page in fn.get_paginator('list_event_source_mappings').paginate(FunctionName=name):
            remaining.extend('mapping:' + m['UUID'] for m in page['EventSourceMappings'])
    for key in ['queue', 'failed_queue']:
        name = data[key].rsplit('/', 1)[-1]
        try:
            sqs.get_queue_url(QueueName=name, QueueOwnerAWSAccountId=data['account'])
            remaining.append('queue:' + name)
        except sqs.exceptions.QueueDoesNotExist:
            pass
    print(json.dumps({'scope': 'Exact lab table, functions, execution roles, log groups, queues and mappings',
                      'remaining': remaining, 'billing': 'Check delayed billing separately'}, indent=2))
    return 1 if remaining else 0


if __name__ == '__main__':
    sys.exit(main())
