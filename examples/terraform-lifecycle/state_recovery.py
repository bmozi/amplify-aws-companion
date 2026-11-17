"""Local state safety drill; no external objects, providers or remote backend."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def run():
    if __debug__ is False:
        raise RuntimeError('Run without Python optimization')
    with tempfile.TemporaryDirectory(prefix='amplify-state-record-') as temporary:
        root = Path(temporary)
        cli = root / 'terraform.rc'
        cli.write_text('disable_checkpoint = true\n')
        env = {k: v for k, v in os.environ.items() if not k.startswith(('TF_', 'AWS_'))}
        env.update(TF_CLI_CONFIG_FILE=str(cli), TF_IN_AUTOMATION='1', CHECKPOINT_DISABLE='1')

        def tf(folder, *args, code=0):
            result = subprocess.run(['terraform', *args], cwd=folder, env=env,
                                    text=True, capture_output=True, timeout=60)
            assert result.returncode == code, result.stdout + result.stderr
            return result.stdout + result.stderr if code else result.stdout

        def setup(name):
            folder = root / name
            folder.mkdir()
            shutil.copyfile(Path(__file__).with_name('main.tf'), folder / 'main.tf')
            tf(folder, 'init', '-input=false', '-no-color')
            return folder

        def state(folder):
            return json.loads(tf(folder, 'state', 'pull'))

        source = setup('source')
        tf(source, 'apply', '-auto-approve', '-input=false', '-no-color')
        older = state(source)
        old_path = root / 'older.json'
        old_path.write_text(json.dumps(older))
        tf(source, 'apply', '-auto-approve', '-input=false', '-no-color', '-var=revision=3')
        current = state(source)
        assert older['lineage'] == current['lineage']
        assert older['serial'] < current['serial']
        rejected = tf(source, 'state', 'push', str(old_path), code=1)
        assert 'serial' in rejected.lower()
        assert state(source) == current, 'Rejected older state must leave destination unchanged'

        unrelated = setup('unrelated')
        tf(unrelated, 'apply', '-auto-approve', '-input=false', '-no-color')
        unrelated_before = state(unrelated)
        assert unrelated_before['lineage'] != current['lineage']
        snapshot = root / 'current.json'
        snapshot.write_text(json.dumps(current))
        rejected = tf(unrelated, 'state', 'push', str(snapshot), code=1)
        assert 'lineage' in rejected.lower()
        assert state(unrelated) == unrelated_before

        restored = setup('empty-destination')
        tf(restored, 'plan', '-input=false', '-no-color', '-var=revision=3', '-out=empty.tfplan')
        empty = json.loads(tf(restored, 'show', '-json', 'empty.tfplan'))
        assert empty['resource_changes'][0]['change']['actions'] == ['create']
        # Never apply the empty-state plan. Restore only into this disposable local folder.
        tf(restored, 'state', 'push', str(snapshot))
        recovered = state(restored)
        assert recovered['lineage'] == current['lineage']
        assert recovered['resources'] == current['resources']
        assert recovered['outputs'] == current['outputs']
        tf(restored, 'plan', '-input=false', '-no-color', '-var=revision=3', '-out=restored.tfplan')
        planned = json.loads(tf(restored, 'show', '-json', 'restored.tfplan'))
        assert planned['resource_changes'][0]['change']['actions'] == ['no-op']
        # Negative control: an empty destination cannot establish the intended lineage.
        wrong_destination = setup('wrong-history-control')
        wrong_snapshot = root / 'unrelated.json'
        wrong_snapshot.write_text(json.dumps(unrelated_before))
        tf(wrong_destination, 'state', 'push', str(wrong_snapshot))
        wrong_state = state(wrong_destination)
        assert wrong_state['lineage'] != current['lineage']
        tf(wrong_destination, 'plan', '-input=false', '-no-color', '-out=wrong.tfplan')
        wrong_plan = json.loads(tf(wrong_destination, 'show', '-json', 'wrong.tfplan'))
        assert wrong_plan['resource_changes'][0]['change']['actions'] == ['no-op']
        # These objects exist only in local state. No cloud resource needs teardown.
    assert not root.exists()
    return {'older_serial_rejected_without_mutation': True,
            'different_lineage_rejected_without_mutation': True,
            'empty_state_plan': 'create; not applied',
            'restored_snapshot_plan': 'no-op; matching IDs and outputs',
            'wrong_history_in_empty_destination': 'accepted and no-op; intended lineage mismatch detected separately',
            'temporary_directory_removed': True,
            'scope': 'local terraform_data records only; no external objects, remote locks or business-data recovery'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
