"""Sequential loopback HTTP canary drill; no AWS, production traffic or writes."""
import argparse
from collections import Counter
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Thread
from urllib.request import ProxyHandler, build_opener

HTTP = build_opener(ProxyHandler({}))


def get(url):
    with HTTP.open(url, timeout=3) as response:
        assert response.status == 200
        return json.load(response)


@contextmanager
def server(respond):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            payload = json.dumps(respond(self.path)).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    instance = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = Thread(target=instance.serve_forever, daemon=True)
    worker.start()
    try:
        yield f'http://127.0.0.1:{instance.server_port}'
    finally:
        instance.shutdown()
        instance.server_close()
        worker.join(timeout=3)
        assert not worker.is_alive()


def version(name, broken):
    def respond(path):
        if path == '/health':
            return {'ready': True, 'version': name}
        # Fixture contract: a 10 percent discount on 1000 cents yields 900.
        return {'version': name, 'quote_cents': 1000 if broken else 900}
    return respond


def decision(observations, candidate):
    results = [x for x in observations if x['version'] == candidate]
    if any(x['quote_cents'] != 900 for x in results):
        return 'rollback'
    if len(results) < 2:
        return 'hold'
    return 'promote'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable-rollback', action='store_true',
                        help='Negative control: expected to fail the recovery assertion')
    args = parser.parse_args()
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    with server(version('stable', False)) as stable, server(version('bad', True)) as bad, server(version('fixed', False)) as fixed:
        route = {'candidate': bad, 'slots': 0, 'sequence': 0}

        def forward(path):
            slot = route['sequence'] % 10
            route['sequence'] += 1
            target = route['candidate'] if slot < route['slots'] else stable
            return get(target + path)

        with server(forward) as public:
            def window(count):
                return [get(public + '/quote') for _ in range(count)]

            assert get(bad + '/health')['ready'] is True
            baseline = window(10)
            assert all(x == {'version': 'stable', 'quote_cents': 900} for x in baseline)
            assert decision([], 'bad') == 'hold'
            route.update(slots=2, sequence=0)
            single = window(1)
            assert decision(single, 'bad') == 'rollback'
            assert decision([{'version': 'fixed', 'quote_cents': 900}], 'fixed') == 'hold'
            route['sequence'] = 0
            canary = window(10)
            assert Counter(x['version'] for x in canary) == {'bad': 2, 'stable': 8}
            action = decision(canary, 'bad')
            assert action == 'rollback'
            if action == 'rollback' and not args.disable_rollback:
                route['slots'] = 0
            route['sequence'] = 0
            recovered = window(10)
            assert all(x == {'version': 'stable', 'quote_cents': 900} for x in recovered), 'rollback did not restore stable responses'
            route.update(candidate=fixed, slots=2, sequence=0)
            repaired = window(10)
            assert decision(repaired, 'fixed') == 'promote'
            route.update(slots=10, sequence=0)
            promoted = window(10)
            assert all(x == {'version': 'fixed', 'quote_cents': 900} for x in promoted)
            result = {'baseline_requests': 10, 'canary_requests': 10,
                      'canary_versions': dict(Counter(x['version'] for x in canary)),
                      'incorrect_business_responses': sum(x['quote_cents'] != 900 for x in canary),
                      'decision': action, 'recovery_checked_requests': len(recovered),
                      'fixed_release_checked_requests': len(promoted),
                      'scope': 'Sequential deterministic loopback HTTP; no AWS, load, data rollback or statistical confidence'}
    result['servers_closed'] = True
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
