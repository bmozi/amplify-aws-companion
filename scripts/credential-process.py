"""AWS credential_process protocol. Stdout is credentials: never run for display."""

raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import os,subprocess,sys
from aws_session import deployment_profile
source=os.environ.copy()
for name in ['AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN','AWS_PROFILE','AWS_DEFAULT_PROFILE']:
 source.pop(name,None)
source['AWS_CONFIG_FILE']=source.get('AWS_LAB_SOURCE_CONFIG_FILE',os.path.expanduser('~/.aws/config'))
p=subprocess.run(['aws','configure','export-credentials','--profile',deployment_profile(),'--format','process'],env=source,capture_output=True)
if p.returncode:
 sys.stderr.write('Unable to refresh AWS CLI credentials. Refresh the selected deployment-role session.\n');sys.exit(p.returncode)
sys.stdout.buffer.write(p.stdout)
