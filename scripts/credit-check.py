"""Inspection-only credit-gate specimen; its pure local checker accepts an explicit reviewed policy. The default run_limit in assess is a fictional USD 5 test fixture, not a reader recommendation."""

if __name__ == '__main__':
    raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import argparse
from datetime import datetime,timezone
from decimal import Decimal,InvalidOperation
import json
import os
from pathlib import Path
import subprocess


def write_private_receipt(path, receipt):
    """Create owner-only before writing; refuse existing files and symlinks."""
    payload = json.dumps(receipt, indent=2) + '\n'
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as output:
        output.write(payload)


def assess(state, reserve, estimate, now, planned_end=None, run_limit=Decimal('5')):
    for number in [reserve,estimate]:
        if not number.is_finite() or number<0:raise ValueError('Amounts must be finite and nonnegative')
    if not run_limit.is_finite() or run_limit<0:raise ValueError('Run limit must be finite and nonnegative')
    if planned_end is not None and (planned_end.tzinfo is None or planned_end<=now):
        raise ValueError('Planned lab end must be a future timezone-aware timestamp')
    credit=state.get('accountPlanRemainingCredits',{})
    if credit.get('unit')!='USD':raise ValueError('No verified USD credit balance')
    remaining=Decimal(str(credit['amount']))
    if not remaining.is_finite() or remaining<0:raise ValueError('Invalid remaining credit balance')
    expiry=datetime.fromisoformat(state['accountPlanExpirationDate'].replace('Z','+00:00'))
    if expiry.tzinfo is None:raise ValueError('Expiration must include timezone')
    reasons=[]
    if state.get('accountPlanType')!='FREE' or state.get('accountPlanStatus')!='ACTIVE':reasons.append('Expected active Free plan; inspect account terms')
    if expiry<=now:reasons.append('Plan expiration reached')
    if estimate>0 and planned_end is None:reasons.append('A live estimate needs a planned lab end')
    if planned_end is not None and expiry<=planned_end:reasons.append('Free plan expires before the planned lab end')
    if remaining-estimate<reserve:reasons.append('Estimate would breach reserved credits')
    if estimate>run_limit:reasons.append('Estimate exceeds the explicitly selected run limit')
    return {'remaining_credits_usd':str(remaining),'reserve_usd':str(reserve),'estimated_run_usd':str(estimate),
            'headroom_after_estimate_usd':str(remaining-reserve-estimate),'plan_expiration':expiry.isoformat(),
            'planned_lab_end':planned_end.isoformat() if planned_end else None,
            'decision':'review_required' if reasons else 'within_credit_policy','reasons':reasons,
            'limits':'Not service-eligibility verification, real-time billing, deployment permission, or a hard spending cap'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',help='Named local profile; omit for an assumed GitHub OIDC session')
    parser.add_argument('--account-id',required=True)
    parser.add_argument('--estimated-run-usd',required=True,type=Decimal)
    parser.add_argument('--reserve-usd',type=Decimal,required=True)
    parser.add_argument('--run-limit-usd',type=Decimal,required=True)
    parser.add_argument('--planned-end-epoch',type=int,help='Required for positive live estimates; does not remove resources')
    parser.add_argument('--quiet',action='store_true',help='Print only the decision, not private credit amounts')
    parser.add_argument('--output-dir',type=Path,default=Path('evidence/billing'))
    args=parser.parse_args()
    common=['--region','us-east-1','--output','json']
    if args.profile:common=['--profile',args.profile,*common]
    identity=json.loads(subprocess.check_output(['aws','sts','get-caller-identity',*common]))
    if identity['Account']!=args.account_id:raise ValueError('Wrong account; stopped')
    state=json.loads(subprocess.check_output(['aws','freetier','get-account-plan-state',*common]))
    if state.get('accountId')!=args.account_id:raise ValueError('Plan belongs to different account')
    now=datetime.now(timezone.utc)
    planned_end=datetime.fromtimestamp(args.planned_end_epoch,timezone.utc) if args.planned_end_epoch is not None else None
    result=assess(state,args.reserve_usd,args.estimated_run_usd,now,planned_end,run_limit=args.run_limit_usd)
    result['checked_at']=now.isoformat()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    path=args.output_dir/(now.strftime('%Y%m%dT%H%M%S%fZ')+'-credits.json')
    write_private_receipt(path, {'summary':result,'source':state})
    print('Free-plan credit gate: '+result['decision'] if args.quiet else json.dumps(result,indent=2))
    return 0 if result['decision']=='within_credit_policy' else 2

if __name__=='__main__':raise SystemExit(main())
