"""Local TLS endpoint-change exercise. Generates only disposable practice certificates."""

import hashlib
import http.server
import json
import pathlib
import socket
import ssl
import subprocess
import tempfile
import threading


def openssl(*args):
    result = subprocess.run(
        ["openssl", *map(str, args)], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise RuntimeError(f"OpenSSL fixture generation failed: {result.stderr.strip()}")


def make_certificates(root):
    ca_key, ca_cert = root / "ca.key", root / "ca.pem"
    openssl("req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "2",
            "-keyout", ca_key, "-out", ca_cert, "-subj", "/CN=Practice CA",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign",
            "-addext", "subjectKeyIdentifier=hash")
    ext = root / "server.ext"
    ext.write_text("subjectAltName=DNS:localhost\nextendedKeyUsage=serverAuth\n"
                   "basicConstraints=critical,CA:FALSE\n"
                   "keyUsage=critical,digitalSignature,keyEncipherment\n"
                   "subjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\n")
    pairs = {}
    for label, serial in (("old", "101"), ("new", "102")):
        key, csr, cert = root / f"{label}.key", root / f"{label}.csr", root / f"{label}.pem"
        openssl("req", "-newkey", "rsa:2048", "-nodes", "-keyout", key,
                "-out", csr, "-subj", "/CN=localhost")
        openssl("x509", "-req", "-in", csr, "-CA", ca_cert, "-CAkey", ca_key,
                "-set_serial", serial, "-out", cert, "-days", "2", "-sha256",
                "-extfile", ext)
        pairs[label] = (cert, key)
    return ca_cert, pairs


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"practice endpoint\n")

    def log_message(self, *_args):
        pass


class Endpoint(http.server.HTTPServer):
    def __init__(self, context):
        super().__init__(("127.0.0.1", 0), Handler)
        self.context = context

    def get_request(self):
        connection, address = self.socket.accept()
        try:
            return self.context.wrap_socket(connection, server_side=True), address
        except Exception:
            connection.close()
            raise


def server_context(pair):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(*map(str, pair))
    return context


def observe(endpoint, ca_cert, name="localhost"):
    context = ssl.create_default_context(cafile=str(ca_cert))
    with socket.create_connection(("127.0.0.1", endpoint.server_port), timeout=3) as raw:
        with context.wrap_socket(raw, server_hostname=name) as tls:
            fingerprint = hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest()
            tls.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            response = tls.recv(4096)
            if b"200 OK" not in response:
                raise RuntimeError("TLS endpoint did not return its practice response")
            return fingerprint


def run():
    with tempfile.TemporaryDirectory(prefix="cert-endpoint-change-") as temp:
        ca_cert, pairs = make_certificates(pathlib.Path(temp))
        west = Endpoint(server_context(pairs["old"]))
        east = Endpoint(server_context(pairs["old"]))
        threads = [threading.Thread(target=server.serve_forever, daemon=True)
                   for server in (west, east)]
        for thread in threads:
            thread.start()
        try:
            original_west = observe(west, ca_cert)
            original_east = observe(east, ca_cert)
            if original_west != original_east:
                raise RuntimeError("Starting endpoints did not present the same certificate")

            # The fictional inventory is updated for both places, but only one
            # live listener receives the replacement. The client checks each.
            west.context = server_context(pairs["new"])
            replaced_west = observe(west, ca_cert)
            unchanged_east = observe(east, ca_cert)
            if replaced_west == original_west or unchanged_east != original_east:
                raise RuntimeError("Endpoint replacement boundary was not observed")
            try:
                observe(west, ca_cert, name="wrong.example")
            except ssl.SSLCertVerificationError:
                wrong_name_rejected = True
            else:
                raise RuntimeError("Wrong server name was accepted")

            return {
                "west_new_certificate_seen": replaced_west != original_west,
                "east_inventory_claim_disagrees_with_endpoint": unchanged_east != replaced_west,
                "wrong_server_name_rejected": wrong_name_rejected,
                "both_valid_connections_used_ca_and_hostname_checks": True,
                "scope": "two local TLS listeners and disposable certificates; no ACM or AWS call",
            }
        finally:
            for server in (west, east):
                server.shutdown()
                server.server_close()
            for thread in threads:
                thread.join(timeout=3)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
