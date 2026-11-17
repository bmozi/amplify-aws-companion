"""Small loopback DNS teaching fixture; no Route 53 or hybrid network is used.

Only one-question UDP A/IN lookups are supported. A supplied clock makes TTL
expiry observable without sleeping; it does not change any operating-system
resolver cache.
"""

from dataclasses import dataclass, field
from socket import AF_INET, SOCK_DGRAM, socket
from socketserver import BaseRequestHandler, ThreadingUDPServer
from struct import pack, unpack
from threading import Thread


def wire_name(name):
    labels = name.rstrip('.').lower().split('.')
    if not labels or any(not label or len(label.encode()) > 63 for label in labels):
        raise ValueError('invalid teaching name')
    return b''.join(bytes([len(label)]) + label.encode('ascii') for label in labels) + b'\0'


def question(packet):
    if len(packet) < 17 or unpack('!H', packet[4:6])[0] != 1:
        raise ValueError('one DNS question required')
    offset = 12
    labels = []
    while True:
        if offset >= len(packet):
            raise ValueError('truncated name')
        size = packet[offset]
        offset += 1
        if size == 0:
            break
        if size > 63 or offset + size > len(packet):
            raise ValueError('unsupported name')
        labels.append(packet[offset:offset + size].decode('ascii').lower())
        offset += size
    if offset + 4 != len(packet) or packet[offset:offset + 4] != b'\0\x01\0\x01':
        raise ValueError('only A/IN questions are supported')
    return '.'.join(labels) + '.', packet[12:]


def answer(packet, address=None, ttl=30):
    _name, original_question = question(packet)
    code = 0 if address else 3  # NOERROR or NXDOMAIN in this fixture.
    header = packet[:2] + pack('!HHHHH', 0x8180 | code, 1, int(bool(address)), 0, 0)
    if not address:
        return header + original_question
    octets = bytes(int(part) for part in address.split('.'))
    if len(octets) != 4:
        raise ValueError('IPv4 address required')
    return header + original_question + b'\xc0\x0c' + pack('!HHIH', 1, 1, ttl, 4) + octets


def lookup(port, name, transaction_id=0x1234):
    packet = pack('!HHHHHH', transaction_id, 0x0100, 1, 0, 0, 0) + wire_name(name) + b'\0\x01\0\x01'
    with socket(AF_INET, SOCK_DGRAM) as client:
        client.settimeout(2)
        client.sendto(packet, ('127.0.0.1', port))
        response, _ = client.recvfrom(512)
    if response[:2] != packet[:2] or response[12:12 + len(packet[12:])] != packet[12:]:
        raise ValueError('unexpected DNS response')
    code = unpack('!H', response[2:4])[0] & 0xF
    if code == 3:
        return 'NXDOMAIN'
    if code != 0 or unpack('!H', response[6:8])[0] != 1 or len(response) < 16:
        raise ValueError('unexpected DNS answer')
    return '.'.join(str(byte) for byte in response[-4:])


@dataclass
class Authority:
    records: dict[str, str]
    queries: int = 0


@dataclass
class Forwarder:
    suffix: str
    target_port: int
    clock: list[int]
    rule_enabled: bool = True
    cache: dict[str, tuple[int, bytes]] = field(default_factory=dict)
    forwarded: int = 0


def authority_server(state):
    class Handler(BaseRequestHandler):
        def handle(self):
            packet, sock = self.request
            name, _ = question(packet)
            state.queries += 1
            sock.sendto(answer(packet, state.records.get(name)), self.client_address)

    return ThreadingUDPServer(('127.0.0.1', 0), Handler)


def forwarder_server(state):
    class Handler(BaseRequestHandler):
        def handle(self):
            packet, sock = self.request
            name, _ = question(packet)
            cached = state.cache.get(name)
            if cached and state.clock[0] < cached[0]:
                # Restore the caller's transaction ID; cache belongs to a name,
                # not to the first client that asked for it.
                response = packet[:2] + cached[1][2:]
            elif not state.rule_enabled or not name.endswith(state.suffix):
                response = answer(packet)
            else:
                with socket(AF_INET, SOCK_DGRAM) as upstream:
                    upstream.settimeout(2)
                    upstream.sendto(packet, ('127.0.0.1', state.target_port))
                    response, _ = upstream.recvfrom(512)
                state.forwarded += 1
                if unpack('!H', response[6:8])[0] == 1:
                    state.cache[name] = (state.clock[0] + 30, response)
            sock.sendto(response, self.client_address)

    return ThreadingUDPServer(('127.0.0.1', 0), Handler)


def run():
    if not __debug__:
        raise SystemExit('Run without Python optimization')
    clock = [0]
    private = Authority({'booking.aws.test.': '10.80.2.10'})
    office = Authority({'parts.office.test.': '10.20.8.9'})
    servers = []
    threads = []
    try:
        for state in (private, office):
            server = authority_server(state)
            servers.append(server)
        inbound = Forwarder('.aws.test.', servers[0].server_address[1], clock)
        outbound = Forwarder('.office.test.', servers[1].server_address[1], clock)
        servers.extend((forwarder_server(inbound), forwarder_server(outbound)))
        for server in servers:
            worker = Thread(target=server.serve_forever)
            worker.start()
            threads.append(worker)

        inbound_port, outbound_port = (server.server_address[1] for server in servers[2:])
        assert lookup(inbound_port, 'booking.aws.test') == '10.80.2.10'
        assert lookup(outbound_port, 'parts.office.test') == '10.20.8.9'
        assert (private.queries, office.queries) == (1, 1)
        assert lookup(inbound_port, 'parts.office.test') == 'NXDOMAIN'
        assert private.queries == 1

        private.records['booking.aws.test.'] = '10.80.9.9'
        clock[0] = 5
        assert lookup(inbound_port, 'booking.aws.test', 0x4321) == '10.80.2.10'
        assert private.queries == 1  # old answer retained until this fixture's TTL
        clock[0] = 31
        assert lookup(inbound_port, 'booking.aws.test') == '10.80.9.9'
        assert private.queries == 2
        inbound.rule_enabled = False
        clock[0] = 62
        assert lookup(inbound_port, 'booking.aws.test') == 'NXDOMAIN'
        assert private.queries == 2  # no rule, so no new authority question
        print('PASS: office-to-private and VPC-to-office directions used separate local rules;')
        print('a cached old answer survived a record change until simulated TTL expiry;')
        print('then a missing forward rule returned NXDOMAIN despite the private record.')
        print('DNS answers alone do not test routes, TLS, API access or AWS Resolver.')
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=3)
            assert not thread.is_alive()


if __name__ == '__main__':
    run()
