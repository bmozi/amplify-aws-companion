import contextlib
import hashlib
import importlib.util
import io
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
import tempfile
from threading import Thread
import unittest
from pathlib import Path
from unittest.mock import MagicMock, call, patch
from zipfile import ZipFile


SCRIPT = Path(__file__).resolve().parents[1] / "deploy-frontend-from-github.py"
SPEC = importlib.util.spec_from_file_location("github_frontend_publisher", SCRIPT)
publisher = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(publisher)

ROOT = Path(__file__).resolve().parents[2]
LIVE_WORKFLOW = ROOT / '.github/workflows/amplify-publish.yml'
EXAMPLE_WORKFLOW = ROOT / 'examples/github-workflows/amplify-publish.yml'
LIVE_REUSABLE = ROOT / '.github/workflows/reusable-amplify-publish.yml'
EXAMPLE_REUSABLE = ROOT / 'examples/github-workflows/reusable-amplify-publish.yml'


def workflow_text():
    if LIVE_WORKFLOW.is_file():
        assert LIVE_WORKFLOW.read_bytes() == EXAMPLE_WORKFLOW.read_bytes()
        return LIVE_WORKFLOW.read_text()
    return EXAMPLE_WORKFLOW.read_text()


def reusable_text():
    if LIVE_REUSABLE.is_file():
        assert LIVE_REUSABLE.read_bytes() == EXAMPLE_REUSABLE.read_bytes()
        return LIVE_REUSABLE.read_text()
    return EXAMPLE_REUSABLE.read_text()


class GitHubPublisherBoundaryTests(unittest.TestCase):
    def test_workflow_keeps_install_before_client_config_and_aws_role_separate(self):
        caller = workflow_text()
        typecheck, publish_call = caller.split('\n  publish:', 1)
        build, publish = reusable_text().split('\n  publish:', 1)
        self.assertIn("needs: typecheck", publish_call)
        self.assertIn("printf '{}\\n' > amplify_outputs.json", typecheck)
        self.assertNotIn('AMPLIFY_OUTPUTS_JSON:', typecheck)
        self.assertNotIn('id-token: write', typecheck)
        self.assertIn('cache-dependency-path: app/frontend-publisher/package-lock.json', build)
        self.assertLess(build.index('npm ci --ignore-scripts'),
                        build.index('python3 scripts/stage-frontend-publisher.py'))
        self.assertLess(build.index('npm audit --audit-level=moderate'),
                        build.index('      - name: Add the generated Amplify browser configuration'))
        self.assertLess(build.index('      - name: Add the generated Amplify browser configuration'),
                        build.index('npm run build'))
        self.assertIn('root = Path("app/frontend-publisher/dist")', build)
        self.assertNotIn('id-token: write', build)
        self.assertIn('uses: ./.github/workflows/reusable-amplify-publish.yml', publish_call)
        self.assertIn('id-token: write', publish)
        self.assertNotIn('npm ci', publish)
        self.assertIn('needs: build', publish)
        self.assertIn('EXPECTED_ARCHIVE_SHA256: ${{ needs.build.outputs.archive_sha256 }}', publish)

    def test_unreviewed_cost_scenario_skips_every_job(self):
        workflow = workflow_text()
        trigger, rest = workflow.split('\njobs:\n', 1)
        typecheck, publish_call = rest.split('\n  publish:', 1)
        build, publish = reusable_text().split('\n  publish:', 1)
        self.assertIn('options: ["review_needed", "static_smoke_100_visit_1d"]', trigger)
        self.assertIn('default: "review_needed"', trigger)
        for job in (build, publish):
            self.assertIn("github.workflow_ref == 'bmozi/aws-capabilities-lab/.github/workflows/amplify-publish.yml@refs/heads/main'", job)
        for job in (typecheck, build, publish_call, publish):
            self.assertIn("inputs.cost_scenario == 'static_smoke_100_visit_1d'", job)
            self.assertIn("inputs.confirm_publish == 'yes'", job)
            self.assertIn("vars.AMPLIFY_PUBLISH_ENABLED == 'true'", job)
        self.assertLess(publish.index('publisher-run-estimate.py'),
                        publish.index('configure-aws-credentials@'))
        self.assertIn('publisher-smoke-run-estimate.json', publish)
        self.assertLess(publish.index('credit-check.py'),
                        publish.index('check-publisher-source-head.py'))
        self.assertLess(publish.index('check-publisher-source-head.py'),
                        publish.index('deploy-frontend-from-github.py'))
        self.assertIn("github.sha == inputs.source_commit", publish)
        self.assertIn("github.workflow == 'Publish the Amplify lab frontend'", publish)
        self.assertIn('EXPECTED_ARCHIVE_SHA256: ${{ needs.build.outputs.archive_sha256 }}', publish)
        self.assertIn('--app-tree-sha "$(git rev-parse HEAD:app)"', publish)
        self.assertIn('(root / "config.sha256").write_text(outputs_digest', build)
        self.assertIn('--archive artifacts/frontend/frontend.zip', publish)
        self.assertIn('--archive-sha256 "$EXPECTED_ARCHIVE_SHA256"', publish)
        self.assertIn('--estimated-run-usd "$ESTIMATED_RUN_USD"', publish)
        self.assertIn('steps.estimate.outputs.planned_end_epoch', publish)

    def test_publisher_lock_excludes_backend_generation_toolchain(self):
        folder = Path(__file__).resolve().parents[2] / 'app/frontend-publisher'
        package = json.loads((folder / 'package.json').read_text())
        locked = json.loads((folder / 'package-lock.json').read_text())
        self.assertEqual(locked['packages']['']['name'], package['name'])
        self.assertEqual(set(package['dependencies']),
                         {'@aws-amplify/ui-react', 'aws-amplify', 'react', 'react-dom'})
        self.assertEqual(set(package['devDependencies']),
                         {'@vitejs/plugin-react', 'vite'})
        for name in ('@aws-amplify/backend', '@aws-amplify/backend-cli',
                     '@graphql-tools/utils', 'braces'):
            self.assertNotIn('node_modules/' + name, locked['packages'])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.archive = Path(self.temp.name) / "frontend.zip"
        self.commit = "a" * 40
        self.run_id = "12345"
        with ZipFile(self.archive, "w") as bundle:
            bundle.writestr("index.html", "synthetic page")
            bundle.writestr("deployment.json", json.dumps({"source_commit": self.commit, "workflow_run_id": self.run_id}))
        self.digest = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.environment = patch.dict(
            os.environ,
            {
                "AWS_LAB_AMPLIFY_APP_ID": "d123abc",
                "AWS_LAB_AMPLIFY_BRANCH": "lab",
                "AWS_LAB_EXPECTED_ACCOUNT_ID": "123456789012",
                "AWS_LAB_EXPECTED_ROLE_NAME": "AmplifyLabGitHubPublisher",
                "SOURCE_COMMIT": self.commit,
                "WORKFLOW_RUN_ID": self.run_id,
                "EXPECTED_ARCHIVE_SHA256": self.digest,
            },
            clear=True,
        )
        self.environment.start()
        self.argv = patch.object(sys, "argv", [str(SCRIPT), str(self.archive)])
        self.argv.start()

    def tearDown(self):
        self.argv.stop()
        self.environment.stop()
        self.temp.cleanup()

    def test_rejects_root_before_any_amplify_change(self):
        with patch.object(
            publisher,
            "aws",
            return_value={"Account": "123456789012", "Arn": "arn:aws:iam::123456789012:root"},
        ) as aws:
            with self.assertRaises(SystemExit):
                publisher.main()
        self.assertEqual(aws.call_args_list, [call("sts", "get-caller-identity")])

    def test_rejects_wrong_account_before_any_amplify_change(self):
        with patch.object(
            publisher,
            "aws",
            return_value={
                "Account": "210987654321",
                "Arn": "arn:aws:sts::210987654321:assumed-role/AmplifyLabGitHubPublisher/run-1",
            },
        ) as aws:
            with self.assertRaises(SystemExit):
                publisher.main()
        self.assertEqual(aws.call_args_list, [call("sts", "get-caller-identity")])

    def test_rejects_other_branch_before_any_aws_call(self):
        os.environ["AWS_LAB_AMPLIFY_BRANCH"] = "production"
        with patch.object(publisher, "aws") as aws:
            with self.assertRaises(SystemExit):
                publisher.main()
        aws.assert_not_called()

    def test_rejects_mismatched_build_before_any_aws_call(self):
        os.environ["SOURCE_COMMIT"] = "b" * 40
        with patch.object(publisher, "aws") as aws, self.assertRaises(SystemExit):
            publisher.main()
        aws.assert_not_called()

    def test_rejects_changed_archive_before_any_aws_call(self):
        with ZipFile(self.archive, "a") as bundle:
            bundle.writestr("changed.js", "different content")
        with patch.object(publisher, "aws") as aws, self.assertRaises(SystemExit):
            publisher.main()
        aws.assert_not_called()

    def test_rejects_traversal_even_with_matching_digest(self):
        with ZipFile(self.archive, "a") as bundle:
            bundle.writestr("../outside.txt", "unexpected file")
        os.environ["EXPECTED_ARCHIVE_SHA256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        with patch.object(publisher, "aws") as aws, self.assertRaises(SystemExit):
            publisher.main()
        aws.assert_not_called()

    def test_rejects_duplicate_name_even_with_matching_digest(self):
        with ZipFile(self.archive, "a") as bundle:
            bundle.writestr("index.html", "second version")
        os.environ["EXPECTED_ARCHIVE_SHA256"] = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        with patch.object(publisher, "aws") as aws, self.assertRaises(SystemExit):
            publisher.main()
        aws.assert_not_called()

    def test_success_never_logs_temporary_upload_url(self):
        signed_url = "https://upload.example.invalid/private-bearer-value"
        aws = MagicMock(
            side_effect=[
                {
                    "Account": "123456789012",
                    "Arn": "arn:aws:sts::123456789012:assumed-role/AmplifyLabGitHubPublisher/run-1",
                },
                {"zipUploadUrl": signed_url, "jobId": "19"},
                {},
                {"job": {"summary": {"status": "SUCCEED"}}},
            ]
        )
        response = MagicMock()
        response.status = 200
        response.__enter__.return_value = response
        output = io.StringIO()
        with patch.object(publisher, "aws", aws), patch.object(
            publisher.urllib.request, "urlopen", return_value=response
        ) as urlopen, patch.object(
            publisher, "read_direct_marker", return_value=True
        ) as marker_read, patch.object(publisher.time, "sleep"), contextlib.redirect_stdout(output):
            self.assertEqual(publisher.main(), 0)
        self.assertEqual(urlopen.call_count, 1)
        marker_read.assert_called_once_with(
            "https://lab.d123abc.amplifyapp.com/deployment.json?run=12345",
            {"source_commit": self.commit, "workflow_run_id": self.run_id},
        )
        self.assertNotIn(signed_url, output.getvalue())
        self.assertIn("Amplify hosting job 19: SUCCEED", output.getvalue())
        self.assertIn("Published to https://lab.d123abc.amplifyapp.com", output.getvalue())

    def test_successful_job_with_stale_hosted_marker_fails_publication(self):
        aws = MagicMock(side_effect=[
            {"Account": "123456789012", "Arn": "arn:aws:sts::123456789012:assumed-role/AmplifyLabGitHubPublisher/run-1"},
            {"zipUploadUrl": "https://upload.example.invalid/secret", "jobId": "19"},
            {},
            {"job": {"summary": {"status": "SUCCEED"}}},
        ])
        upload = MagicMock(status=200)
        upload.__enter__.return_value = upload
        with patch.object(publisher, "aws", aws), patch.object(
            publisher.urllib.request, "urlopen", return_value=upload
        ), patch.object(publisher, "read_direct_marker", return_value=False) as marker_read, \
                patch.object(publisher.time, "sleep"), self.assertRaises(SystemExit):
            publisher.main()
        self.assertEqual(marker_read.call_count, 6)

    def test_direct_marker_rejects_redirect_even_when_destination_matches(self):
        expected = {"source_commit": self.commit, "workflow_run_id": self.run_id}

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/redirect":
                    self.send_response(302)
                    self.send_header("Location", "/deployment.json")
                    self.end_headers()
                    return
                body = json.dumps(expected).encode() if self.path == "/deployment.json" else b"not found"
                self.send_response(200 if self.path == "/deployment.json" else 404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            with patch.dict(os.environ, {"no_proxy": "127.0.0.1,localhost"}):
                self.assertTrue(publisher.read_direct_marker(base + "/deployment.json", expected))
                self.assertFalse(publisher.read_direct_marker(base + "/redirect", expected))
        finally:
            server.shutdown()
            worker.join(timeout=5)
            server.server_close()


if __name__ == "__main__":
    unittest.main()
