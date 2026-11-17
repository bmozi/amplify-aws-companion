"""Read-only AWS validation/simulation of the candidate document; never attach or deploy."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE=Path(__file__).resolve().parents[2]
POLICY=Path(__file__).with_name('permissions.json')
TERRAFORM=BASE/'infra/github-publisher/main.tf'


def check_source_alignment(policy, terraform_source):
    """Fail closed when the review snapshot no longer matches this Terraform source shape."""
    branch='arn:aws:amplify:us-east-2:111111111111:apps/d000000000000/branches/lab'
    expected={
        'CreateAndStartDeploymentForOneBranch':
            ({'amplify:CreateDeployment','amplify:StartDeployment'},branch),
        'ReadJobsForOneBranch':({'amplify:GetJob'},branch+'/jobs/*'),
        'ReadCurrentFreePlanForPublicationGate':({'freetier:GetAccountPlanState'},'*'),
        'ReadOneMonthlyCostBudgetForPublicationGate':
            ({'budgets:ViewBudget'},'arn:aws:budgets::111111111111:budget/AWS-Learning-Monthly-Cost'),
    }
    if policy.get('Version')!='2012-10-17' or not isinstance(policy.get('Statement'),list):
        raise ValueError('Review policy is not the expected IAM document')
    statements=policy['Statement']
    if len(statements)!=len(expected) or {row.get('Sid') for row in statements}!=set(expected):
        raise ValueError('Review policy statements differ from the Terraform candidate')
    for row in statements:
        actions=row['Action'] if isinstance(row.get('Action'),list) else [row.get('Action')]
        wanted_actions,wanted_resource=expected[row['Sid']]
        if (row.get('Effect')!='Allow' or set(actions)!=wanted_actions or
                row.get('Resource')!=wanted_resource or set(row)!={'Sid','Effect','Action','Resource'}):
            raise ValueError('Review policy action, resource or condition changed')

    expected_branch=r'^\s*branch_arn\s*=\s*"arn:aws:amplify:\$\{var\.region\}:\$\{var\.account_id\}:apps/\$\{var\.amplify_app_id\}/branches/\$\{var\.amplify_branch\}"\s*$'
    if not re.search(expected_branch, terraform_source, re.M):
        raise ValueError('Terraform branch ARN construction changed; review it again')
    match=re.search(r'data "aws_iam_policy_document" "publish" \{(.*?)\n\}\n\nresource "aws_iam_role_policy"',terraform_source,re.S)
    if not match:
        raise ValueError('Terraform publish policy source shape changed')
    blocks=re.findall(r'(?ms)^  statement \{\n(.*?)^  \}',match.group(1))
    if len(blocks)!=len(expected):
        raise ValueError('Terraform publish policy statement count changed')
    hcl_expected={
        'CreateAndStartDeploymentForOneBranch':
            ({'amplify:CreateDeployment','amplify:StartDeployment'},'local.branch_arn'),
        'ReadJobsForOneBranch':({'amplify:GetJob'},'"${local.branch_arn}/jobs/*"'),
        'ReadCurrentFreePlanForPublicationGate':({'freetier:GetAccountPlanState'},'"*"'),
        'ReadOneMonthlyCostBudgetForPublicationGate':
            ({'budgets:ViewBudget'},'"arn:aws:budgets::${var.account_id}:budget/${var.budget_name}"'),
    }
    seen=set()
    for block in blocks:
        sid=re.search(r'(?m)^    sid\s*=\s*"([^"]+)"$',block)
        actions=re.search(r'(?m)^    actions\s*=\s*\[([^\]]+)\]$',block)
        resource=re.search(r'(?m)^    resources\s*=\s*\[([^\]]+)\]$',block)
        if not (sid and actions and resource) or sid.group(1) not in hcl_expected:
            raise ValueError('Terraform publish policy field changed')
        name=sid.group(1)
        if name in seen:
            raise ValueError('Duplicate Terraform policy statement')
        seen.add(name)
        wanted_actions,wanted_resource=hcl_expected[name]
        observed_actions=set(re.findall(r'"([^"]+)"',actions.group(1)))
        if observed_actions!=wanted_actions or resource.group(1).strip()!=wanted_resource:
            raise ValueError('Terraform publish policy diverges from the review snapshot')
        fields=set(re.findall(r'(?m)^    ([a-z_]+)\s*=',block))
        if fields!={'sid','effect','actions','resources'} or not re.search(r'(?m)^    effect\s*=\s*"Allow"$',block):
            raise ValueError('Terraform policy effect or field needs new review')
    if seen!=set(expected):
        raise ValueError('Terraform publish policy is incomplete')


def check_selected_target(policy, terraform_dir):
    """Compare the private Terraform input's exact branch with the review JSON."""
    if not (terraform_dir/'terraform.tfvars').is_file():
        raise ValueError('Private Terraform target values are unavailable')
    process=subprocess.run(
        ['terraform','console','-var-file=terraform.tfvars'],
        input='local.branch_arn\n',cwd=terraform_dir,capture_output=True,text=True,
        timeout=25,check=False,
    )
    if process.returncode:
        raise ValueError('Terraform could not resolve the selected branch target')
    try:
        selected=json.loads(process.stdout.strip())
    except json.JSONDecodeError as error:
        raise ValueError('Terraform branch target was not a known string') from error
    branch=next(row['Resource'] for row in policy['Statement']
                if row['Sid']=='CreateAndStartDeploymentForOneBranch')
    if selected!=branch:
        raise ValueError('Terraform-selected app/branch differs from the review policy')
    budget_process=subprocess.run(
        ['terraform','console','-var-file=terraform.tfvars'],
        input='var.budget_name\n',cwd=terraform_dir,capture_output=True,text=True,
        timeout=25,check=False,
    )
    if budget_process.returncode:
        raise ValueError('Terraform could not resolve the selected budget')
    try:
        budget_name=json.loads(budget_process.stdout.strip())
    except json.JSONDecodeError as error:
        raise ValueError('Terraform budget name was not a known string') from error
    reviewed_budget=next(row['Resource'] for row in policy['Statement']
                         if row['Sid']=='ReadOneMonthlyCostBudgetForPublicationGate')
    if reviewed_budget!='arn:aws:budgets::111111111111:budget/'+budget_name:
        raise ValueError('Terraform-selected budget differs from the review policy')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',help='Authorized profile with policy validation/simulation access')
    parser.add_argument('--offline',action='store_true',help='Check source and private Terraform target without AWS calls')
    args=parser.parse_args()
    policy=json.loads(POLICY.read_text())
    check_source_alignment(policy,TERRAFORM.read_text())
    check_selected_target(policy,TERRAFORM.parent)
    if args.offline:
        print(json.dumps({'source_and_selected_target':'match',
                          'policy_sha256':hashlib.sha256(POLICY.read_bytes()).hexdigest(),
                          'scope':'Local source/target shape only; no IAM evaluation or AWS read'},indent=2))
        return
    if not args.profile:
        parser.error('--profile is required for AWS validation and simulation')
    def aws(*parts):
        return json.loads(subprocess.check_output(['aws',*parts,'--profile',args.profile,
            '--region','us-east-2','--output','json','--no-cli-pager'],text=True))
    identity=aws('sts','get-caller-identity')
    if identity['Account']!='111111111111':raise SystemExit('Unexpected AWS account')
    validation=aws('accessanalyzer','validate-policy','--policy-document','file://'+str(POLICY),
                   '--policy-type','IDENTITY_POLICY')
    if validation.get('nextToken'):raise RuntimeError('Validation paginated; inspect remaining findings')
    if validation['findings']:raise RuntimeError('Policy findings require review: '+json.dumps(validation['findings']))
    branch='arn:aws:amplify:us-east-2:111111111111:apps/d000000000000/branches/lab'
    other=branch.rsplit('/',1)[0]+'/unrelated'
    resources=[branch,branch+'/jobs/1',other,other+'/jobs/1',
               branch.split('/branches/')[0],'arn:aws:iam::111111111111:role/UnrelatedExample']
    actions=['amplify:CreateDeployment','amplify:StartDeployment','amplify:GetJob','amplify:DeleteApp','iam:PassRole']
    result=aws('iam','simulate-custom-policy','--policy-input-list',json.dumps([POLICY.read_text()]),
               '--action-names',*actions,'--resource-arns',*resources)
    if result.get('IsTruncated'):raise RuntimeError('Simulation paginated; inspect remaining decisions')
    decisions={}
    for action_result in result['EvaluationResults']:
        if action_result.get('MissingContextValues'):raise RuntimeError('Missing simulation context')
        for resource_result in action_result['ResourceSpecificResults']:
            key=(action_result['EvalActionName'],resource_result['EvalResourceName'])
            if key in decisions:raise RuntimeError('Duplicate simulation decision')
            decisions[key]=resource_result
    if set(decisions)!={(a,r) for a in actions for r in resources}:raise RuntimeError('Incomplete simulation matrix')
    for (action,resource),row in decisions.items():
        expected='allowed' if (resource==branch and action in actions[:2]) or (resource==branch+'/jobs/1' and action=='amplify:GetJob') else 'implicitDeny'
        if row['EvalResourceDecision']!=expected or row.get('MissingContextValues'):
            raise RuntimeError('Unexpected or incomplete decision: '+json.dumps(row))
    free_plan=aws('iam','simulate-custom-policy','--policy-input-list',json.dumps([POLICY.read_text()]),
                  '--action-names','freetier:GetAccountPlanState','--resource-arns','*')
    if free_plan.get('IsTruncated') or len(free_plan.get('EvaluationResults',[]))!=1:
        raise RuntimeError('Free-plan simulation result is incomplete')
    plan_row=free_plan['EvaluationResults'][0]
    if (plan_row.get('EvalActionName')!='freetier:GetAccountPlanState' or
            plan_row.get('EvalDecision')!='allowed' or plan_row.get('MissingContextValues')):
        raise RuntimeError('Free-plan read was not allowed by the reviewed document')
    budget_arn='arn:aws:budgets::111111111111:budget/AWS-Learning-Monthly-Cost'
    other_budget='arn:aws:budgets::111111111111:budget/OtherBudget'
    budget_read=aws('iam','simulate-custom-policy','--policy-input-list',json.dumps([POLICY.read_text()]),
                    '--action-names','budgets:ViewBudget','--resource-arns',budget_arn,other_budget)
    budget_rows={row['EvalResourceName']:row['EvalResourceDecision']
                 for row in budget_read['EvaluationResults'][0]['ResourceSpecificResults']}
    if (budget_read.get('IsTruncated') or len(budget_read.get('EvaluationResults',[]))!=1 or
            budget_rows!={budget_arn:'allowed',other_budget:'implicitDeny'}):
        raise RuntimeError('Budget read scope differs from the reviewed document')
    report={'checked_utc':datetime.now(timezone.utc).isoformat(),
      'policy_sha256':hashlib.sha256(POLICY.read_bytes()).hexdigest(),
      'caller_arn':identity['Arn'],'validation':validation,'simulation':result,
      'free_plan_simulation':free_plan,'budget_simulation':budget_read,
      'scope':'Standalone policy document validation/simulation only; not role trust, effective role permissions or live publication'}
    folder=BASE/'evidence/iam-review';folder.mkdir(parents=True,exist_ok=True)
    (folder/'frontend-publisher-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'findings':len(validation['findings']),'decisions_checked':len(decisions),
        'expected_allows':5,'expected_implicit_denies':len(decisions)-3+1,'policy_sha256':report['policy_sha256'],
        'scope':report['scope']},indent=2))

if __name__=='__main__':main()
