"""Cross-customer cache and origin-failure controls for the loopback fixture."""

import unittest
from urllib.request import Request, urlopen

from cache_boundary import Fixture, request, start_server


class CacheBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.server, self.worker = start_server(self.fixture)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join()

    def test_safe_private_path_keeps_two_customers_distinct_after_warm_read(self):
        alice = request(self.server, 'GET', '/invoice/current', 'alice')
        bob = request(self.server, 'GET', '/invoice/current', 'bob')
        stranger = request(self.server, 'GET', '/invoice/current', 'stranger')
        self.assertEqual(alice, (200, b'invoice-for-alice', 'private-no-store'))
        self.assertEqual(bob, (200, b'invoice-for-bob', 'private-no-store'))
        self.assertEqual(stranger[0], 403)
        self.assertEqual(self.fixture.private_cache, {})
        req = Request(f'http://127.0.0.1:{self.server.server_port}/invoice/current',
                      headers={'X-Fixture-Actor': 'alice'})
        with urlopen(req, timeout=3) as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_public_cache_hit_does_not_prove_origin_or_booking_is_available(self):
        self.assertEqual(request(self.server, 'GET', '/guide/warm')[2], 'public-fill')
        self.fixture.origin_up = False
        self.assertEqual(request(self.server, 'GET', '/guide/warm'), (200, b'public-guide-v1', 'public-hit'))
        self.assertEqual(request(self.server, 'GET', '/guide/cold')[0], 503)
        self.assertEqual(request(self.server, 'GET', '/invoice/current', 'alice')[0], 503)
        self.assertEqual(request(self.server, 'POST', '/booking', 'alice')[0], 503)

    def test_url_only_private_cache_is_an_intentional_leak_control(self):
        bad = Fixture(unsafe_private_cache=True)
        server, worker = start_server(bad)
        try:
            self.assertEqual(request(server, 'GET', '/invoice/current', 'alice')[1], b'invoice-for-alice')
            leaked = request(server, 'GET', '/invoice/current', 'bob')
            self.assertEqual(leaked, (200, b'invoice-for-alice', 'UNSAFE-private-hit'))
            req = Request(f'http://127.0.0.1:{server.server_port}/invoice/current',
                          headers={'X-Fixture-Actor': 'bob'})
            with urlopen(req, timeout=3) as response:
                self.assertEqual(response.headers['Cache-Control'], 'public, max-age=300')
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


if __name__ == '__main__':
    unittest.main()
