"""Publish the built static app; keep presigned upload URL out of logs."""

raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import json,pathlib,subprocess,urllib.request,zipfile,time
from aws_session import deployment_profile, require_deployment_role
profile=deployment_profile()
base=pathlib.Path(__file__).resolve().parents[1]
def aws(*args):
 return json.loads(subprocess.check_output(['aws',*args,'--profile',profile,'--region','us-east-2','--output','json','--no-cli-pager'],text=True))
require_deployment_role(aws('sts','get-caller-identity'))
app_id=subprocess.check_output(['terraform',f'-chdir={base}/infra/hosting','output','-raw','app_id'],text=True).strip()
dist=base/'app/dist';assert (dist/'index.html').is_file()
archive=base/'evidence/live/frontend.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in dist.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(dist))
deployment=aws('amplify','create-deployment','--app-id',app_id,'--branch-name','lab')
request=urllib.request.Request(deployment['zipUploadUrl'],data=archive.read_bytes(),method='PUT',headers={'Content-Type':'application/zip'})
with urllib.request.urlopen(request,timeout=60) as response: assert response.status==200
aws('amplify','start-deployment','--app-id',app_id,'--branch-name','lab','--job-id',deployment['jobId'])
for _ in range(60):
 job=aws('amplify','get-job','--app-id',app_id,'--branch-name','lab','--job-id',deployment['jobId'])
 status=job['job']['summary']['status'];print('Hosting deployment:',status,flush=True)
 if status in ['SUCCEED','FAILED','CANCELLED']:
  (base/'evidence/live/hosting-job-summary.json').write_text(json.dumps(job['job']['summary'],indent=2))
  if status!='SUCCEED':raise SystemExit('Hosting deployment did not succeed')
  break
 time.sleep(10)
else:raise SystemExit('Timed out waiting for hosting job')
print(f'https://lab.{app_id}.amplifyapp.com')
