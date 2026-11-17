"""Build and exercise real local containers; does not call AWS or push images."""
from concurrent.futures import ThreadPoolExecutor
from http.client import RemoteDisconnected
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import threading
import time
import urllib.error
import urllib.request
import uuid

BASE = Path(__file__).resolve().parent
DOCKER_CONTEXT = None


class DrainFailure(AssertionError):
    pass


class BusinessGateFailure(AssertionError):
    pass


def select_local_context():
    if os.environ.get('DOCKER_HOST'):
        raise RuntimeError('Unset DOCKER_HOST and select a local Unix-socket Docker context')
    context = subprocess.check_output(['docker', 'context', 'show'], text=True, timeout=15).strip()
    detail = json.loads(subprocess.check_output(
        ['docker', 'context', 'inspect', context], text=True, timeout=15))
    endpoint = detail[0]['Endpoints']['docker']['Host']
    if not endpoint.startswith('unix:///'):
        raise RuntimeError('This lesson requires a local Unix-socket Docker endpoint')
    return context


def docker_command(*args):
    if DOCKER_CONTEXT is None:
        raise RuntimeError('Select the reviewed local Docker context before running commands')
    return ['docker', '--context', DOCKER_CONTEXT, *args]


def docker(*args):
    return subprocess.check_output(docker_command(*args), text=True,
                                   stderr=subprocess.STDOUT, timeout=180).strip()


def request(url):
    try:
        response = urllib.request.urlopen(url, timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.status, json.load(response)


def business_probe(url, release):
    """One synthetic acceptance case; it is not a full invoice test suite."""
    status, body = request(url + '/invoice?subtotal_cents=1000&discount_cents=100')
    return status == 200 and body == {'release': release, 'total_cents': 900}


def main():
    if __debug__ is False:
        raise SystemExit('Run without Python optimization')
    global DOCKER_CONTEXT
    DOCKER_CONTEXT = select_local_context()
    token = uuid.uuid4().hex[:12]
    image = 'amplify-container-lesson:' + token
    containers = []
    target = {'url': None}
    observations = []

    class Router(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                status, body = request(target['url'] + self.path)
            except (RemoteDisconnected, ConnectionResetError, urllib.error.URLError):
                status, body = 502, {'error':'upstream disconnected'}
            payload = json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        def log_message(self, *args):
            pass

    router = ThreadingHTTPServer(('127.0.0.1', 0), Router)
    worker = threading.Thread(target=router.serve_forever)
    worker.start()
    endpoint = f'http://127.0.0.1:{router.server_port}'

    def launch(release, ready, invoice_mode='correct'):
        name = f'amplify-lesson-{token}-{release}'
        containers.append(name)
        docker('run', '-d', '--name', name, '--label', 'amplify.lesson=' + token,
               '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
               '--memory=128m', '--cpus=0.5', '--pids-limit=64',
               '-p', '127.0.0.1::8080', '-e', 'RELEASE=' + release,
               '-e', 'READY=' + ready, '-e', 'INVOICE_MODE=' + invoice_mode, image)
        detail = json.loads(docker('inspect', name))[0]
        assert detail['Config']['User'] == '10001:10001'
        assert detail['HostConfig']['ReadonlyRootfs'] is True
        mapping = detail['NetworkSettings']['Ports']['8080/tcp'][0]
        assert mapping['HostIp'] == '127.0.0.1'
        url = 'http://127.0.0.1:' + mapping['HostPort']
        deadline = time.monotonic() + 20
        while True:
            try:
                if request(url + '/live')[0] == 200:
                    return name, url
            except (OSError, urllib.error.URLError):
                pass
            if time.monotonic() > deadline:
                raise RuntimeError('Container failed to start: ' + name)
            time.sleep(0.1)

    def promote(url, release):
        if request(url + '/ready')[0] != 200:
            return False
        if not business_probe(url, release):
            return False
        target['url'] = url
        return True

    def wait_held(url):
        deadline = time.monotonic() + 5
        while not request(url + '/state')[1]['held']:
            if time.monotonic() > deadline:
                raise RuntimeError('Request never entered held state')
            time.sleep(0.02)

    def stop(name):
        docker('stop', '--time', '5', name)
        detail = json.loads(docker('inspect', name))[0]
        assert detail['State']['ExitCode'] == 0
        assert not detail['State']['OOMKilled']
        assert 'graceful_stop' in docker('logs', name)

    try:
        docker('build', '--pull=false', '--network=none', '-t', image, str(BASE))
        image_id = docker('image', 'inspect', image, '--format', '{{.Id}}')
        old, old_url = launch('v1', 'yes')
        assert promote(old_url, 'v1')
        assert request(endpoint) == (200, {'release':'v1'})
        bad, bad_url = launch('bad-config', 'no')
        assert request(bad_url + '/live')[0] == 200
        assert request(bad_url + '/ready')[0] == 503
        assert not promote(bad_url, 'bad-config')
        assert request(endpoint) == (200, {'release':'v1'})
        observations.append('running but unready candidate rejected; v1 still served')
        wrong, wrong_url = launch('wrong-invoice', 'yes', 'omit-discount')
        assert request(wrong_url + '/ready')[0] == 200
        assert request(wrong_url + '/invoice?subtotal_cents=1000&discount_cents=100') == (200, {'release':'wrong-invoice', 'total_cents':1000})
        if promote(wrong_url, 'wrong-invoice'):
            raise BusinessGateFailure('Ready candidate with wrong invoice total was promoted')
        assert request(endpoint) == (200, {'release':'v1'})
        assert business_probe(endpoint, 'v1')
        observations.append('ready candidate with wrong invoice total rejected; v1 still served')
        new, new_url = launch('v2', 'yes')
        with ThreadPoolExecutor(max_workers=1) as pool:
            inflight = pool.submit(request, endpoint + '/held')
            wait_held(old_url)
            assert not inflight.done()
            assert promote(new_url, 'v2')
            assert request(endpoint) == (200, {'release':'v2'})
            stop(old)
            outcome = inflight.result(timeout=5)
            if outcome != (200, {'release':'v1', 'completed':True}):
                raise DrainFailure(f'In-flight request did not complete: {outcome}')
        logs = docker('logs', old)
        assert logs.index('request_started') < logs.index('termination_received')
        assert logs.index('termination_received') < logs.index('request_completed') < logs.index('graceful_stop')
        assert request(endpoint) == (200, {'release':'v2'})
        observations.append('v1 request completed after SIGTERM while new requests reached v2')
        victim, victim_url = launch('forced-stop', 'yes')
        with ThreadPoolExecutor(max_workers=1) as pool:
            interrupted = pool.submit(request, victim_url + '/held')
            wait_held(victim_url)
            assert not interrupted.done()
            docker('kill', '--signal=KILL', victim)
            try:
                interrupted.result(timeout=5)
            except (RemoteDisconnected, ConnectionResetError, urllib.error.URLError):
                pass
            else:
                raise AssertionError('Forced stop unexpectedly produced a response')
        state = json.loads(docker('inspect', victim))[0]['State']
        assert state['ExitCode'] == 137 and not state['OOMKilled']
        assert 'request_completed' not in docker('logs', victim)
        observations.append('forced SIGKILL interrupted the held request; exit 137 without OOM')
        for name in (bad, wrong, new):
            stop(name)
        observations.append('four gracefully stopped processes exited zero; fifth was intentionally killed')
        print(json.dumps({'image_id':image_id,'observations':observations,
                          'scope':'local Docker and loopback router; controlled in-flight request and forced kill; no ECS/ALB/IAM'},indent=2))
    finally:
        router.shutdown()
        worker.join()
        router.server_close()
        failures = []
        for name in containers:
            try:
                result = subprocess.run(docker_command('rm','-f',name), capture_output=True, text=True, timeout=30)
            except (OSError, subprocess.TimeoutExpired) as error:
                failures.append(f'{name}: {error}')
                continue
            if result.returncode and 'No such container' not in result.stderr:
                failures.append(result.stderr)
        try:
            result = subprocess.run(docker_command('image','rm',image), capture_output=True, text=True, timeout=30)
            if result.returncode and 'No such image' not in result.stderr:
                failures.append(result.stderr)
        except (OSError, subprocess.TimeoutExpired) as error:
            failures.append(f'{image}: {error}')
        if failures:
            raise RuntimeError('Cleanup requires attention: ' + '\n'.join(failures))
        print('Removed this run\'s containers and image tag; base image/build cache retained.')


if __name__ == '__main__':
    main()
