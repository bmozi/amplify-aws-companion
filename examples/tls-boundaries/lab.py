"""Real local TLS validation and separate synthetic application authorization."""
from contextlib import contextmanager
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading


@contextmanager
def serve(certificate, key, events):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(certificate, key)

    class Server(ThreadingHTTPServer):
        def get_request(self):
            raw, address = super().get_request()
            raw.settimeout(2)
            try:
                return context.wrap_socket(raw, server_side=True), address
            except BaseException:
                raw.close()
                raise

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            actor = self.headers.get('X-Fixture-Actor')
            status = 200 if actor == 'alice' else 403
            if self.path != '/invoice':
                status = 404
            events.append(status)  # No request headers or invoice contents in the evidence log.
            body = json.dumps({'invoice': 'fictional-alice-invoice'} if status == 200 else {'error': 'denied'}).encode()
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = Server(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
        assert not thread.is_alive()


def client_context(certificate=None):
    # No system trust-store modification or inherited CA bundle. An empty store is
    # intentional for the unknown-issuer case. Verification stays on in every case.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    if certificate:
        context.load_verify_locations(cafile=str(certificate))
    assert context.check_hostname and context.verify_mode == ssl.CERT_REQUIRED
    return context


def request(port, context, hostname='localhost', actor='alice'):
    # Always connect to loopback: server_hostname is a verification input, not DNS.
    with socket.create_connection(('127.0.0.1', port), timeout=2) as raw:
        with context.wrap_socket(raw, server_hostname=hostname) as connection:
            protocol = connection.version()
            connection.sendall(('GET /invoice HTTP/1.1\r\nHost: localhost\r\n'
                                f'X-Fixture-Actor: {actor}\r\nConnection: close\r\n\r\n').encode())
            with HTTPResponse(connection) as response:
                response.begin()
                return response.status, json.loads(response.read()), protocol


def main():
    if sys.flags.optimize:
        raise SystemExit('Run without -O: the teaching checks use assertions.')
    openssl = shutil.which('openssl')
    if not openssl:
        raise SystemExit('OpenSSL CLI with req -addext support is required; nothing is installed automatically.')
    events, results = [], []
    with tempfile.TemporaryDirectory(prefix='amplify-local-tls-') as temporary:
        root = Path(temporary)
        certificate, key = root / 'localhost.pem', root / 'localhost.key'
        # One-day, self-signed local trust anchor; never uploaded or installed globally.
        subprocess.run([openssl, 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                        '-days', '1', '-subj', '/CN=localhost',
                        '-addext', 'subjectAltName=DNS:localhost',
                        '-addext', 'basicConstraints=critical,CA:TRUE',
                        '-addext', 'keyUsage=critical,digitalSignature,keyCertSign',
                        '-keyout', str(key), '-out', str(certificate)],
                       check=True, capture_output=True, timeout=20)
        key.chmod(0o600)
        trusted = client_context(certificate)
        with serve(str(certificate), str(key), events) as port:
            status, body, protocol = request(port, trusted)
            assert status == 200 and body == {'invoice': 'fictional-alice-invoice'}
            results.append({'case': 'trusted issuer and matching name', 'http_status': status, 'tls': protocol})
            for label, context, name, expected_code in [
                ('untrusted self-signed issuer', client_context(), 'localhost', 18),
                ('trusted certificate but wrong name', trusted, 'wrong.example', 62),
            ]:
                before = len(events)
                try:
                    request(port, context, name)
                except ssl.SSLCertVerificationError as error:
                    assert error.verify_code == expected_code, (label, error.verify_code, error.verify_message)
                    results.append({'case': label, 'verification_code': error.verify_code,
                                    'reason': error.verify_message, 'http_request_reached_handler': False})
                else:
                    raise AssertionError(label + ' incorrectly succeeded')
                assert len(events) == before
            status, body, protocol = request(port, trusted, actor='bob')
            assert status == 403 and 'invoice' not in body
            results.append({'case': 'valid TLS but unauthorized fixture actor', 'http_status': status, 'tls': protocol})
            assert events == [200, 403]
    assert not root.exists()
    print(json.dumps({'result': 'passed', 'observations': results,
                      'python_version': sys.version.split()[0],
                      'python_tls_library': ssl.OPENSSL_VERSION,
                      'temporary_certificate_removed': not certificate.exists(),
                      'temporary_private_key_removed': not key.exists(),
                      'scope': 'Actual loopback TLS handshake/hostname/trust checks and synthetic authorization; no AWS ACM or renewal'}, indent=2))


if __name__ == '__main__':
    main()
