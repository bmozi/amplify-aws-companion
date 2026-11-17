"""Compare targeted and full plans for two disposable terraform_data objects."""
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    with tempfile.TemporaryDirectory(prefix='amplify-target-scope-') as tmp:
        folder = Path(tmp)
        (folder / 'terraform.rc').write_text('disable_checkpoint = true\n')
        (folder / 'main.tf').write_text('''terraform { required_version = ">= 1.6, < 2.0" }
variable "data_revision" { type = number }
resource "terraform_data" "network" { input = "stable" }
resource "terraform_data" "database" { input = var.data_revision }
''')
        env = {k: v for k, v in os.environ.items() if not k.startswith(('TF_', 'AWS_'))}
        env.update(TF_CLI_CONFIG_FILE=str(folder / 'terraform.rc'), TF_IN_AUTOMATION='1', CHECKPOINT_DISABLE='1')

        def tf(*args):
            result = subprocess.run(['terraform', *args], cwd=folder, env=env,
                                    capture_output=True, text=True, timeout=60, check=True)
            return result.stdout

        tf('init', '-input=false', '-no-color')
        tf('apply', '-input=false', '-auto-approve', '-no-color', '-var=data_revision=1')

        def actions(name, *options):
            tf('plan', '-input=false', '-no-color', '-var=data_revision=2', f'-out={name}', *options)
            result = json.loads(tf('show', '-json', name))
            return {entry['address']: entry['change']['actions'] for entry in result['resource_changes']}

        targeted = actions('target.tfplan', '-target=terraform_data.network')
        full = actions('full.tfplan')
        if targeted != {'terraform_data.network': ['no-op']}:
            raise RuntimeError(f'Unexpected targeted scope: {targeted}')
        if full.get('terraform_data.network') != ['no-op'] or full.get('terraform_data.database') != ['update']:
            raise RuntimeError(f'Unexpected full-plan actions: {full}')
        state = json.loads(tf('show', '-json'))
        resources = {entry['address']: entry['values']
                     for entry in state['values']['root_module']['resources']}
        if resources['terraform_data.database']['input'] != 1:
            raise RuntimeError('Planning unexpectedly changed the local database-shaped object')
        print(json.dumps({'targeted_plan': targeted, 'full_plan': full,
                          'database_input_after_plans': resources['terraform_data.database']['input'],
                          'scope': 'local terraform_data only; neither plan applied; no AWS or actual database'}, indent=2))


if __name__ == '__main__':
    main()
