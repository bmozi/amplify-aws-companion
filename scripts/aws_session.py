"""Refreshable temporary credentials via an isolated, credential-free config file."""
import json,os,pathlib,re,subprocess,sys,tempfile
from contextlib import contextmanager
def deployment_profile():
 profile=os.environ.get('AWS_LAB_DEPLOY_PROFILE','').strip()
 if not profile:raise RuntimeError('Set AWS_LAB_DEPLOY_PROFILE to an approved assumed-role profile; no root fallback')
 return profile

def require_deployment_role(identity):
 if identity.get('Account')!='111111111111':raise RuntimeError('Unexpected AWS account')
 role=os.environ.get('AWS_LAB_DEPLOY_ROLE','').strip()
 if not role or not re.fullmatch(r'[\w+=,.@-]+',role):
  raise RuntimeError('Set AWS_LAB_DEPLOY_ROLE to the reviewed role name')
 expected=r'arn:aws:sts::111111111111:assumed-role/'+re.escape(role)+r'/[^/]+'
 if not re.fullmatch(expected,identity.get('Arn','')):
  raise RuntimeError('Expected the selected assumed-role session; root, IAM users and other roles are rejected')
 # This checks identity only. The role policy and downstream execution roles need separate review.

@contextmanager
def session_environment():
 raise RuntimeError('Inspection-only source: live AWS sessions are disabled in this companion.')
 profile=deployment_profile()
 identity=json.loads(subprocess.check_output(['aws','sts','get-caller-identity','--profile',profile,'--output','json'],text=True))
 require_deployment_role(identity)
 env=os.environ.copy()
 for name in ['AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN','AWS_DEFAULT_PROFILE']:env.pop(name,None)
 env['AWS_LAB_SOURCE_CONFIG_FILE']=env.get('AWS_CONFIG_FILE',os.path.expanduser('~/.aws/config'))
 with tempfile.TemporaryDirectory(prefix='amplify-credential-config-') as directory:
  config=pathlib.Path(directory)/'config'
  helper=pathlib.Path(__file__).with_name('credential-process.py')
  config.write_text(f'[profile amplify-session]\nregion = us-east-2\ncredential_process = {sys.executable} {helper}\n')
  config.chmod(0o600)
  env.update(AWS_CONFIG_FILE=str(config),AWS_PROFILE='amplify-session',AWS_REGION='us-east-2',AWS_DEFAULT_REGION='us-east-2',AWS_SDK_LOAD_CONFIG='1',AWS_EC2_METADATA_DISABLED='true')
  yield env
