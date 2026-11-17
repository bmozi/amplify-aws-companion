"""Loopback-only stock provider in a separate process; no AWS or real partner."""

import argparse
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
import hmac
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

from external_stock import ReplyLost, StockSystem, PickupCoordinator


HERE = Path(__file__).resolve().parent


def handler_for(stock, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def answer(self, code, payload):
            data = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def authorized(self):
            supplied = self.headers.get('Authorization', '')
            if not hmac.compare_digest(supplied, 'Bearer ' + token):
                self.answer(401, {'error': 'unauthorized'})
                return False
            return True

        def do_POST(self):
            if not self.authorized():
                return
            if self.path != '/reserve':
                return self.answer(404, {'error': 'not_found'})
            try:
                length = int(self.headers.get('Content-Length', '-1'))
                if not 0 < length <= 2048:
                    raise ValueError('Invalid request size')
                body = json.loads(self.rfile.read(length))
                if (set(body) != {'operation_id', 'request_id', 'depot', 'drop_reply'}
                        or not all(isinstance(body[key], str) and body[key]
                                   for key in ('operation_id', 'request_id', 'depot'))
                        or not isinstance(body['drop_reply'], bool)):
                    raise ValueError('Invalid request')
                outcome = stock.reserve(body['operation_id'], body['request_id'], body['depot'])
            except (ValueError, TypeError, json.JSONDecodeError) as error:
                return self.answer(409, {'error': str(error)})
            if body['drop_reply']:
                # The database transaction has committed. Close this connection
                # without an HTTP response; the client cannot know that fact.
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.connection.close()
                return
            return self.answer(200, {'outcome': outcome})

        def do_GET(self):
            if not self.authorized():
                return
            path = urlsplit(self.path).path
            if path == '/availability':
                return self.answer(200, {'available': stock.available()})
            if path.startswith('/decisions/'):
                operation_id = unquote(path.removeprefix('/decisions/'))
                if not operation_id or '/' in operation_id:
                    return self.answer(400, {'error': 'invalid_operation_id'})
                decision = stock.lookup(operation_id)
                if decision is None:
                    return self.answer(404, {'error': 'not_found'})
                return self.answer(200, {'request_id': decision[0],
                                         'depot': decision[1], 'outcome': decision[2]})
            return self.answer(404, {'error': 'not_found'})

    return Handler


class StockHttpClient:
    def __init__(self, port, token=''):
        self.base = f'http://127.0.0.1:{port}'
        self.token = token

    def request(self, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        headers = {'Authorization': 'Bearer ' + self.token} if self.token else {}
        if data:
            headers['Content-Type'] = 'application/json'
        request = Request(self.base + path, data=data, headers=headers)
        try:
            with urlopen(request, timeout=2) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)
        except (URLError, OSError, TimeoutError) as error:
            raise ReplyLost('No authoritative stock reply arrived') from error

    def reserve(self, operation_id, request_id, depot, *, lose_reply=False):
        status, body = self.request('/reserve', {'operation_id': operation_id,
                                                'request_id': request_id,
                                                'depot': depot,
                                                'drop_reply': lose_reply})
        if status == 409:
            raise ValueError(body['error'])
        if status != 200 or body.get('outcome') not in ('reserved', 'unavailable'):
            raise ValueError('Invalid stock response')
        return body['outcome']

    def lookup(self, operation_id):
        status, body = self.request('/decisions/' + quote(operation_id, safe=''))
        if status == 404:
            return None
        if status != 200:
            raise ValueError('Invalid stock lookup response')
        return body['request_id'], body['depot'], body['outcome']

    def available(self):
        status, body = self.request('/availability')
        if status != 200:
            raise ValueError('Invalid stock availability response')
        return body['available']


@contextmanager
def provider(stock_path, ready_path):
    ready_path.unlink(missing_ok=True)
    token = secrets.token_urlsafe(32)
    child_environment = os.environ.copy()
    child_environment['FOOD_BANK_STOCK_TOKEN'] = token
    process = subprocess.Popen([sys.executable, str(HERE / 'stock_http.py'), 'serve',
                                '--stock', str(stock_path), '--ready', str(ready_path)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                               env=child_environment)
    try:
        deadline = time.monotonic() + 5
        while not ready_path.exists():
            if process.poll() is not None:
                raise RuntimeError('Stock provider exited before readiness: '
                                   + process.stderr.read().decode()[-1000:])
            if time.monotonic() > deadline:
                raise RuntimeError('Stock provider did not become ready')
            time.sleep(0.02)
        client = StockHttpClient(int(ready_path.read_text()), token)
        yield process, client
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        process.stderr.close()
        ready_path.unlink(missing_ok=True)


def run(pickup_path, stock_path, ready_path):
    pickup = PickupCoordinator(pickup_path)
    pickup.accept('request-a', 'depot-1')
    with provider(stock_path, ready_path) as (first_process, stock):
        first_pid = first_process.pid
        after_loss = pickup.dispatch('request-a', stock, lose_reply=True)
        assert after_loss == 'stock_unknown' and stock.available() == 0
    while_down = pickup.reconcile('request-a', stock)
    assert while_down == 'stock_unknown'
    with provider(stock_path, ready_path) as (second_process, stock):
        second_pid = second_process.pid
        pickup = PickupCoordinator(pickup_path)
        recovered = pickup.reconcile('request-a', stock)
        replay = stock.reserve('reserve:request-a', 'request-a', 'depot-1')
        pickup.accept('request-b', 'depot-1')
        second = pickup.dispatch('request-b', stock)
        remaining = stock.available()
    assert first_pid != second_pid and recovered == replay == 'reserved'
    assert second == 'unavailable' and remaining == 0
    return {'after_lost_http_reply': after_loss, 'while_provider_down': while_down,
            'after_new_process_lookup': recovered, 'same_id_replay': replay,
            'second_request': second, 'remaining_boxes': remaining,
            'provider_process_changed': first_pid != second_pid,
            'scope': 'two local OS processes and SQLite files over loopback HTTP; no independent host, real identity, depot API or AWS'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('serve', 'demo'))
    parser.add_argument('--stock', type=Path)
    parser.add_argument('--ready', type=Path)
    args = parser.parse_args()
    if args.mode == 'serve':
        if not args.stock or not args.ready:
            parser.error('serve needs --stock and --ready')
        token = os.environ.get('FOOD_BANK_STOCK_TOKEN', '')
        if len(token) < 32:
            parser.error('serve needs an ephemeral stock token from the local harness')
        stock = StockSystem(args.stock)
        server = HTTPServer(('127.0.0.1', 0), handler_for(stock, token))
        args.ready.write_text(str(server.server_port))
        server.serve_forever()
    else:
        import tempfile
        with tempfile.TemporaryDirectory(prefix='amplify-stock-http-') as raw:
            root = Path(raw)
            print(json.dumps(run(root / 'pickup.sqlite', root / 'stock.sqlite',
                                 root / 'ready'), indent=2))


if __name__ == '__main__':
    main()
