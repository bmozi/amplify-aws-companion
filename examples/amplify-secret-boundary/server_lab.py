"""A loopback-only model of a server using a private value without returning it."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import hmac
import json


INVENTED_SUPPLIER_KEY = 'FICTIONAL_SERVER_SUPPLIER_KEY_9021'
FIXTURE_CALLER = 'fixture-customer-1'


class Gateway(BaseHTTPRequestHandler):
    events = []
    unsafe_debug = False

    def log_message(self, *_args):
        pass

    def do_GET(self):
        if self.path != '/availability/F-42':
            return self.reply(404, {'error': 'unknown item'})
        supplied = self.headers.get('Authorization', '')
        if not hmac.compare_digest(supplied, 'Bearer ' + FIXTURE_CALLER):
            self.events.append({'result': 'denied', 'item': 'F-42'})
            return self.reply(403, {'error': 'not allowed'})
        # This is a local stand-in for a supplier call. There is no external API.
        available = INVENTED_SUPPLIER_KEY.startswith('FICTIONAL_SERVER_')
        self.events.append({'result': 'allowed', 'item': 'F-42'})
        answer = {'item': 'F-42', 'available': available}
        if self.unsafe_debug:
            answer['debug_supplier_key'] = INVENTED_SUPPLIER_KEY
        return self.reply(200, answer)

    def reply(self, status, value):
        data = json.dumps(value, sort_keys=True).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def call(port, caller):
    request = Request(f'http://127.0.0.1:{port}/availability/F-42')
    if caller is not None:
        request.add_header('Authorization', 'Bearer ' + caller)
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()


def run_case(unsafe_debug):
    handler = type('FixtureGateway', (Gateway,), {'events': [], 'unsafe_debug': unsafe_debug})
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        allowed_status, allowed_body = call(server.server_port, FIXTURE_CALLER)
        denied_status, denied_body = call(server.server_port, 'fixture-other-customer')
        missing_status, missing_body = call(server.server_port, None)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    assert allowed_status == 200 and json.loads(allowed_body)['available'] is True
    assert denied_status == missing_status == 403
    assert json.loads(denied_body) == json.loads(missing_body) == {'error': 'not allowed'}
    assert INVENTED_SUPPLIER_KEY.encode() not in denied_body + missing_body
    assert INVENTED_SUPPLIER_KEY not in json.dumps(handler.events)
    return {'authorized_result': 'available', 'other_caller_status': denied_status,
            'missing_caller_status': missing_status,
            'invented_key_in_authorized_response': INVENTED_SUPPLIER_KEY.encode() in allowed_body,
            'invented_key_in_denied_response_or_events': False}


def run():
    safe = run_case(False)
    unsafe = run_case(True)
    assert not safe['invented_key_in_authorized_response']
    assert unsafe['invented_key_in_authorized_response']
    return {'safe': safe, 'unsafe_debug': unsafe,
            'scope': 'loopback Python fixture with invented caller and supplier key; no AWS function, secret store, identity or upstream'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
