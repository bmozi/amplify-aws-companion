"""A deliberately small JSON update contract; standard library, no network or AWS."""
import json


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate field: ' + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('non-finite JSON number: ' + value)


def apply_update(current, payload):
    """Validate completely before returning a new record; never mutate current."""
    if not isinstance(payload, bytes) or len(payload) > 1024:
        raise ValueError('expected at most 1024 UTF-8 bytes')
    try:
        update = json.loads(payload.decode('utf-8'), object_pairs_hook=unique_object,
                            parse_constant=reject_constant)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError('invalid UTF-8 JSON') from error
    if type(update) is not dict:
        raise ValueError('expected an object')
    if set(update) - {'version', 'part_id', 'price_cents', 'note'}:
        raise ValueError('unknown field')
    if type(update.get('version')) is not int or update['version'] != 1:
        raise ValueError('unsupported contract version')
    if type(update.get('part_id')) is not str or update['part_id'] != current['part_id']:
        raise ValueError('part identifier must match exactly')
    if 'price_cents' in update:
        price = update['price_cents']
        if type(price) is not int or not 0 <= price <= 1_000_000:
            raise ValueError('price must be integer USD cents within the fixture limit')
    if 'note' in update:
        note = update['note']
        if note is not None and (type(note) is not str or len(note) > 200):
            raise ValueError('note must be null or a string of at most 200 characters')
    result = dict(current)
    for key in ('price_cents', 'note'):
        if key in update:
            result[key] = update[key]
    return result


def run():
    original = {'part_id': '0012', 'price_cents': 30, 'note': 'Keep dry'}
    wire = b'{"version":1,"part_id":"0012","price_cents":0}'
    free = apply_update(original, wire)
    assert free == {'part_id': '0012', 'price_cents': 0, 'note': 'Keep dry'}
    cleared = apply_update(free, b'{"version":1,"part_id":"0012","note":null}')
    assert cleared['note'] is None and cleared['price_cents'] == 0
    blank = apply_update(original, b'{"version":1,"part_id":"0012","note":""}')
    assert blank['note'] == '' and original['note'] == 'Keep dry'
    unicode_note = 'é' * 200
    unicode_wire = json.dumps({'version': 1, 'part_id': '0012', 'note': unicode_note},
                              ensure_ascii=False).encode('utf-8')
    assert len(unicode_note) == 200 and len(unicode_note.encode('utf-8')) == 400
    assert apply_update(original, unicode_wire)['note'] == unicode_note
    assert apply_update(original, wire + b' ' * (1024 - len(wire))) == free
    encoded = json.dumps(cleared, ensure_ascii=False).encode('utf-8')
    assert json.loads(encoded) == cleared
    assert 10 + 20 == 30
    assert 0.1 + 0.2 != 0.3  # Binary floating-point is not exact decimal arithmetic.
    base = {'version': 1, 'part_id': '0012'}
    invalid = [dict(base, price_cents=v) for v in [True, '30', 30.0, None, -1, 1_000_001]]
    invalid += [dict(base, version=v) for v in [True, 2, '1']]
    invalid += [dict(base, part_id=12), dict(base, part_id='12'),
                dict(base, note=4), dict(base, note='x'*201),
                dict(base, price=30), {'part_id': '0012'}, {'version': 1}, []]
    bad_wires = [json.dumps(item).encode() for item in invalid]
    bad_wires += [b'{"version":1,"part_id":"0012","price_cents":10,"price_cents":20}',
                  b'{"version":1,"part_id":"0012","price_cents":NaN}',
                  b'\xff', b'{', b' '*1025]
    for payload in bad_wires:
        before = dict(original)
        try:
            apply_update(original, payload)
        except ValueError:
            pass
        else:
            raise AssertionError('ambiguous or invalid input accepted: ' + repr(payload))
        assert original == before, 'rejection changed the existing record'
    print(json.dumps({'valid_zero': free, 'explicit_clear': cleared, 'empty_note': blank,
                      'rejected_payloads': len(bad_wires), 'original_unchanged': original}))


if __name__ == '__main__':
    run()
