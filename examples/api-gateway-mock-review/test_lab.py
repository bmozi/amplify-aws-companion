import unittest
from lab import read_availability


class ContractTests(unittest.TestCase):
    def test_mock_success_and_realistic_unavailable(self):
        self.assertEqual(read_availability(200, '{"appointmentId":"A-1","available":true}'), 'available')
        self.assertEqual(read_availability(200, '{"appointmentId":"A-1","available":false}'), 'unavailable')

    def test_changed_provider_response_is_not_silently_accepted(self):
        self.assertEqual(read_availability(200, '{"appointmentId":42,"available":true}'), 'invalid response')
        self.assertEqual(read_availability(200, '{"appointmentId":"A-1","available":"true"}'), 'invalid response')
        self.assertEqual(read_availability(200, 'not-json'), 'invalid response')

    def test_failure_does_not_become_a_success(self):
        self.assertEqual(read_availability(503, '{"appointmentId":"A-1","available":true}'), 'service error')
        self.assertNotEqual(read_availability(503, '{}'), read_availability(200, '{"appointmentId":"A-1","available":false}'))


if __name__ == '__main__':
    unittest.main()
