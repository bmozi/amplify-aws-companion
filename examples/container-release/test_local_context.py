"""Context-selection checks without a Docker daemon."""
import json
import unittest
from unittest.mock import patch
import lab


class ContextTests(unittest.TestCase):
    def test_host_override_refused_before_cli(self):
        with patch.dict(lab.os.environ, {'DOCKER_HOST': 'ssh://remote'}), patch.object(lab.subprocess, 'check_output') as cli:
            with self.assertRaises(RuntimeError):
                lab.select_local_context()
            cli.assert_not_called()

    def test_remote_context_refused(self):
        for endpoint in ['ssh://remote', 'tcp://127.0.0.1:2375', 'tcp://remote:2376']:
            with self.subTest(endpoint=endpoint), patch.dict(lab.os.environ, {}, clear=True), patch.object(lab.subprocess, 'check_output', side_effect=['remote\n', json.dumps([{'Endpoints': {'docker': {'Host': endpoint}}}])]):
                with self.assertRaises(RuntimeError):
                    lab.select_local_context()

    def test_local_context_selected_and_pinned(self):
        with patch.dict(lab.os.environ, {}, clear=True), patch.object(lab.subprocess, 'check_output', side_effect=['desktop\n', json.dumps([{'Endpoints': {'docker': {'Host': 'unix:///tmp/docker.sock'}}}])]):
            self.assertEqual(lab.select_local_context(), 'desktop')
        with patch.object(lab, 'DOCKER_CONTEXT', 'desktop'):
            self.assertEqual(lab.docker_command('rm', 'our-container'), ['docker', '--context', 'desktop', 'rm', 'our-container'])

    def test_cleanup_timeout_does_not_skip_other_run_resources(self):
        launched = []

        def docker(*args):
            if args[0] == 'run':
                launched.append(args[args.index('--name') + 1])
                if len(launched) == 2:
                    raise RuntimeError('injected second launch failure')
                return 'container-id'
            if args[0] == 'inspect':
                return json.dumps([{'Config': {'User': '10001:10001'},
                                    'HostConfig': {'ReadonlyRootfs': True},
                                    'NetworkSettings': {'Ports': {'8080/tcp': [
                                        {'HostIp': '127.0.0.1', 'HostPort': '12345'}]}}}])
            return 'image-id'

        success = lab.subprocess.CompletedProcess([], 0, '', '')
        failure = lab.subprocess.TimeoutExpired(['docker', 'rm'], 30)
        with patch.object(lab, 'select_local_context', return_value='local'), \
             patch.object(lab, 'ThreadingHTTPServer'), patch.object(lab.threading, 'Thread'), \
             patch.object(lab, 'docker', side_effect=docker), \
             patch.object(lab, 'request', return_value=(200, {'release': 'v1'})), \
             patch.object(lab, 'business_probe', return_value=True), \
             patch.object(lab.subprocess, 'run', side_effect=[failure, success, success]) as cleanup:
            with self.assertRaisesRegex(RuntimeError, 'Cleanup requires attention'):
                lab.main()
        self.assertEqual(len(launched), 2)
        self.assertEqual(cleanup.call_count, 3)
        self.assertEqual(cleanup.call_args_list[0].args[0][-1], launched[0])
        self.assertEqual(cleanup.call_args_list[1].args[0][-1], launched[1])
        self.assertEqual(cleanup.call_args_list[2].args[0][3:5], ['image', 'rm'])
        self.assertTrue(all(call.kwargs['timeout'] == 30 for call in cleanup.call_args_list))

    def test_no_command_before_selection(self):
        with patch.object(lab, 'DOCKER_CONTEXT', None):
            with self.assertRaises(RuntimeError):
                lab.docker_command('build')


if __name__ == '__main__':
    unittest.main()
