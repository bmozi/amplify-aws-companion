"""Exercise real Terraform lifecycle in a disposable local directory. No AWS provider."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def run(folder):
    shutil.copyfile(Path(__file__).with_name('main.tf'),folder/'main.tf')
    cli=folder/'terraform.rc';cli.write_text('disable_checkpoint = true\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TF_', 'AWS_'))}
    env.update(TF_CLI_CONFIG_FILE=str(cli),TF_IN_AUTOMATION='1',CHECKPOINT_DISABLE='1')
    def tf(*args, allowed=(0,)):
        result=subprocess.run(['terraform',*args],cwd=folder,env=env,text=True,capture_output=True,timeout=60)
        if result.returncode not in allowed:
            raise RuntimeError(f'Terraform {args[0]} failed: {result.stderr}\n{result.stdout}')
        return result
    def plan(name,revision=1,generation=1):
        tf('plan','-input=false','-no-color',f'-var=revision={revision}',f'-var=generation={generation}',f'-out={name}')
        data=json.loads(tf('show','-json',name).stdout)
        changes=[r for r in data.get('resource_changes',[]) if r['address']=='terraform_data.lesson']
        return changes[0]['change']['actions'] if changes else []
    def apply(name):tf('apply','-input=false','-no-color',name)
    tf('init','-input=false','-no-color')
    tf('validate','-no-color')
    assert plan('create.tfplan')==['create'];apply('create.tfplan')
    initial=json.loads(tf('show','-json').stdout)['values']['root_module']['resources'][0]['values']['id']
    assert plan('unchanged.tfplan')==['no-op']
    assert plan('stale.tfplan',revision=2)==['update']
    assert plan('update.tfplan',revision=3)==['update'];apply('update.tfplan')
    state=json.loads(tf('show','-json').stdout)
    assert state['values']['outputs']['selected_revision']['value']==3
    assert state['values']['root_module']['resources'][0]['values']['id']==initial
    stale=tf('apply','-input=false','-no-color','stale.tfplan',allowed=(1,))
    assert 'Saved plan is stale' in stale.stderr + stale.stdout
    assert plan('replace.tfplan',revision=3,generation=2)==['delete','create'];apply('replace.tfplan')
    state=json.loads(tf('show','-json').stdout)
    assert state['values']['root_module']['resources'][0]['values']['id']!=initial
    replacement_id=state['values']['root_module']['resources'][0]['values']['id']
    # A source-label refactor is not automatically a state-address migration.
    config=folder/'main.tf'
    renamed=config.read_text().replace('"terraform_data" "lesson"','"terraform_data" "renamed"').replace('terraform_data.lesson.output','terraform_data.renamed.output')
    config.write_text(renamed)
    tf('plan','-input=false','-no-color','-var=revision=3','-var=generation=2','-out=unsafe-rename.tfplan')
    unsafe=json.loads(tf('show','-json','unsafe-rename.tfplan').stdout)
    actions={r['address']:r['change']['actions'] for r in unsafe['resource_changes']}
    assert actions=={'terraform_data.lesson':['delete'],'terraform_data.renamed':['create']}
    # Inspect but never apply the destructive refactor control.
    config.write_text(renamed+'\nmoved {\n  from = terraform_data.lesson\n  to = terraform_data.renamed\n}\n')
    tf('plan','-input=false','-no-color','-var=revision=3','-var=generation=2','-out=move.tfplan')
    moved=json.loads(tf('show','-json','move.tfplan').stdout)['resource_changes']
    assert len(moved)==1 and moved[0]['address']=='terraform_data.renamed'
    assert moved[0]['previous_address']=='terraform_data.lesson'
    assert moved[0]['change']['actions']==['no-op']
    apply('move.tfplan')
    assert tf('state','list').stdout.strip()=='terraform_data.renamed'
    moved_state=json.loads(tf('show','-json').stdout)['values']['root_module']['resources']
    assert len(moved_state)==1 and moved_state[0]['values']['id']==replacement_id
    assert moved_state[0]['values']['output']['revision']==3
    tf('plan','-destroy','-input=false','-no-color','-var=revision=3','-var=generation=2','-out=destroy.tfplan')
    deletion=json.loads(tf('show','-json','destroy.tfplan').stdout)
    assert deletion['resource_changes'][0]['change']['actions']==['delete'];apply('destroy.tfplan')
    assert tf('state','list').stdout.strip()==''
    return {'create':'passed','unchanged':'no-op','update_preserves_id':True,
            'stale_plan_rejected':True,'replacement_changes_id':True,'destroy_leaves_empty_state':True,
            'rename_without_mapping':actions,'mapped_rename_preserves_id_and_revision':True,
            'scope':'Terraform built-in terraform_data only; no remote resource drift, AWS APIs or remote locking tested'}


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='amplify-tf-lesson-') as temporary:
        folder=Path(temporary);result=run(folder)
    from state_recovery import run as recover_state
    result['state_record_recovery']=recover_state()
    result['temporary_directory_removed']=not folder.exists()
    assert result['temporary_directory_removed']
    print(json.dumps(result,indent=2))
