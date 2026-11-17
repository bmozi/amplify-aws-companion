"""Compare a prepared response with a changed fictional provider contract.

Pure local fixtures: this is not API Gateway, an HTTP server, or a scheduler.
"""
import json


def read_availability(status, body):
    """Validate the promised customer-facing response, not a booking effect."""
    if status != 200:
        return 'service error'
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return 'invalid response'
    if (not isinstance(payload, dict)
            or not isinstance(payload.get('appointmentId'), str)
            or not payload['appointmentId']
            or type(payload.get('available')) is not bool):
        return 'invalid response'
    return 'available' if payload['available'] else 'unavailable'


def demo():
    cases = [
        ('prepared mock', 200, '{"appointmentId":"A-1","available":true}'),
        ('changed provider fixture', 200, '{"appointmentId":42,"available":true}'),
        ('service error fixture', 503, '{"message":"unavailable"}'),
    ]
    for name, status, body in cases:
        print(f'{name}: {read_availability(status, body)}')
    print('Fixtures only: no API, scheduler or booking was contacted.')


if __name__ == '__main__':
    demo()
