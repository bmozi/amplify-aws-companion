"""Failure-path checks; never start Docker, Kubernetes or AWS."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('k8s_lesson', Path(__file__).with_name('run_lab.py'))
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class CleanupTests(unittest.TestCase):
    def test_failed_build_removes_tag_if_created(self):
        def command(*args, **kwargs):
            if 'build' in args:
                raise subprocess.TimeoutExpired(args, 180)
            if 'ls' in args:
                return 'image-id'
            return ''
        with patch.object(lab, 'preflight'), patch.object(lab, 'command', side_effect=command) as cmd, patch.object(lab, 'kubectl') as kube:
            with self.assertRaises(subprocess.TimeoutExpired):
                lab.run()
            self.assertTrue(any('rm' in call.args for call in cmd.call_args_list))
            kube.assert_not_called()

    def test_lost_create_response_attempts_owned_cleanup(self):
        with patch.object(lab, 'preflight'), patch.object(lab, 'command', return_value=''), patch.object(lab, 'kubectl', side_effect=RuntimeError('lost response')), patch.object(lab, 'remove_namespace') as cleanup:
            with self.assertRaisesRegex(RuntimeError, 'lost response'):
                lab.run()
            cleanup.assert_called_once()
            namespace, owner = cleanup.call_args.args
            self.assertEqual(namespace, 'amplify-k8s-reality-' + owner)

    def test_other_owner_is_preserved(self):
        with patch.object(lab, 'kubectl', return_value=json.dumps({'metadata': {'labels': {'amplify-lab-owner': 'someone-else'}}})) as kube:
            with self.assertRaisesRegex(RuntimeError, 'different ownership'):
                lab.remove_namespace('fixture', 'ours')
            self.assertEqual(kube.call_count, 1)

    def test_owned_namespace_deleted(self):
        with patch.object(lab, 'kubectl', side_effect=[json.dumps({'metadata': {'labels': {'amplify-lab-owner': 'ours'}}}), '']) as kube:
            lab.remove_namespace('fixture', 'ours')
            self.assertEqual(kube.call_args.args[:3], ('delete', 'namespace', 'fixture'))

    def test_absent_namespace_needs_no_delete(self):
        with patch.object(lab, 'kubectl', return_value='') as kube:
            lab.remove_namespace('fixture', 'ours')
            self.assertEqual(kube.call_count, 1)

    def test_missing_base_fails_preflight(self):
        with patch.object(lab, 'kubectl', return_value=json.dumps({'clusters': [{'cluster': {'server': 'https://127.0.0.1:6443'}}]})), patch.object(lab, 'command', side_effect=['linux', RuntimeError('base absent')]) as cmd:
            with self.assertRaisesRegex(RuntimeError, 'base absent'):
                lab.preflight()
            self.assertEqual(cmd.call_args.args[-3:], ('image', 'inspect', 'python:3.13-slim'))


if __name__ == '__main__':
    unittest.main()
