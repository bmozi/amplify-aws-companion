"""Static least-privilege guard for the lab source; not an AWS IAM evaluation."""
from pathlib import Path
import re
import unittest


class PolicySourceTests(unittest.TestCase):
    def test_reservation_role_lists_the_hold_and_sweep_actions(self):
        source = (Path(__file__).resolve().parents[1] / 'infra' / 'main.tf').read_text()
        match = re.search(r'reservation\s*=\s*\[([^\]]+)\]', source)
        self.assertIsNotNone(match, 'reservation action list is missing')
        actions = set(re.findall(r'"(dynamodb:[A-Za-z]+)"', match.group(1)))
        self.assertEqual({
            'dynamodb:GetItem', 'dynamodb:PutItem', 'dynamodb:UpdateItem',
            'dynamodb:DeleteItem', 'dynamodb:ConditionCheckItem', 'dynamodb:Scan',
        }, actions)


if __name__ == '__main__':
    unittest.main()
