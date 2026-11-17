"""One-shot custom backend deployment with refreshable AWS CLI credentials."""

raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import pathlib,subprocess,sys
from aws_session import session_environment
base=pathlib.Path(__file__).resolve().parents[1]
app_id=subprocess.check_output(['terraform',f'-chdir={base}/infra/hosting','output','-raw','app_id'],text=True).strip()
command = ['npx','cdk','bootstrap','aws://111111111111/us-east-2'] if '--bootstrap' in sys.argv else ['npx','ampx','pipeline-deploy','--branch','lab','--app-id',app_id]
with session_environment() as env:
 env['CI']='true'
 raise SystemExit(subprocess.run(command,cwd=base/'app',env=env).returncode)
