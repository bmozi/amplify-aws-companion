"""Compare real Python and Node JSON parsers on one set of local wire bytes."""
import json
from pathlib import Path
import subprocess

from lab import apply_update, unique_object


def run():
    current = {'part_id': '0012', 'price_cents': 30, 'note': 'Keep dry'}
    emoji = '🚚' * 200
    wires = {
        'safe_update': '{"version":1,"part_id":"0012","price_cents":0}',
        'numeric_event_id': '{"event_id":9007199254740993}',
        'text_event_id': '{"event_id":"9007199254740993"}',
        'duplicate_price': '{"version":1,"part_id":"0012","price_cents":10,"price_cents":20}',
        'emoji_note': json.dumps({'version': 1, 'part_id': '0012', 'note': emoji}, ensure_ascii=False),
    }
    cases = [{'name': name, 'raw': raw} for name, raw in wires.items()]
    process = subprocess.run(
        ['node', str(Path(__file__).with_name('interop_consumer.mjs'))],
        input=json.dumps(cases, ensure_ascii=False), text=True, capture_output=True,
        timeout=10, check=True,
    )
    node = json.loads(process.stdout)
    assert set(node) == set(wires)

    safe = apply_update(current, wires['safe_update'].encode())
    assert safe == {'part_id': '0012', 'price_cents': 0, 'note': 'Keep dry'}
    assert node['safe_update'] == {'part_id': '0012', 'price_cents': 0, 'has_note': False}
    assert current['price_cents'] == 30

    exact = json.loads(wires['numeric_event_id'])['event_id']
    assert exact == 9007199254740993
    assert node['numeric_event_id'] == {
        'type': 'number', 'value': '9007199254740992', 'safe_integer': False,
    }
    assert node['text_event_id'] == {
        'type': 'string', 'value': str(exact), 'safe_integer': False,
    }

    try:
        json.loads(wires['duplicate_price'], object_pairs_hook=unique_object)
    except ValueError as error:
        assert 'duplicate field' in str(error)
    else:
        raise AssertionError('The strict Python parser accepted a duplicate price')
    assert node['duplicate_price'] == {'price_cents': 20}
    try:
        apply_update(current, wires['duplicate_price'].encode())
    except ValueError:
        pass
    else:
        raise AssertionError('The application accepted a duplicate price')

    assert apply_update(current, wires['emoji_note'].encode())['note'] == emoji
    assert len(emoji) == 200
    assert node['emoji_note'] == {
        'utf16_units': 400, 'code_points': 200, 'utf8_bytes': 800,
    }
    print(json.dumps({
        'safe_update': node['safe_update'],
        'numeric_id': {'python_exact': str(exact), 'node': node['numeric_event_id']},
        'text_id': node['text_event_id'],
        'duplicate_price': {'strict_python': 'rejected', 'node_last_value': 20},
        'emoji_note': node['emoji_note'],
        'scope': 'Local Python and Node parser observations only; no AWS or authenticated API',
    }, ensure_ascii=False))


if __name__ == '__main__':
    run()
