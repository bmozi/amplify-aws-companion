"""Compare field-specific Unicode choices across local Python and Node runtimes."""
import json
from pathlib import Path
import subprocess
import unicodedata


def normalized_label(value):
    """A deliberately narrow, human-entered-label rule; not an ID or auth rule."""
    if not isinstance(value, str) or not value:
        raise ValueError('label must be nonempty text')
    return unicodedata.normalize('NFC', value)


def add_label(index, raw, record_id):
    key = normalized_label(raw)
    if key in index:
        raise ValueError('canonical label collision')
    index[key] = record_id


def run():
    values = {
        'composed_label': 'Caf\u00e9',
        'decomposed_label': 'Cafe\u0301',
        'circled_id': '\u2460',
        'ascii_id': '1',
        'latin_a': 'a',
        'cyrillic_a': '\u0430',
    }
    cases = [{'name': name, 'value': value} for name, value in values.items()]
    process = subprocess.run(
        ['node', str(Path(__file__).with_name('unicode_consumer.mjs'))],
        input=json.dumps(cases, ensure_ascii=False), text=True,
        capture_output=True, timeout=10, check=True,
    )
    node = json.loads(process.stdout)
    observations = node['observations']
    assert set(observations) == set(values)
    for name, value in values.items():
        result = observations[name]
        assert result['raw'] == value
        assert result['nfc'] == unicodedata.normalize('NFC', value)
        assert result['nfkc'] == unicodedata.normalize('NFKC', value)
        assert result['code_points'] == len(value)
        assert result['utf8_bytes'] == len(value.encode('utf-8'))

    composed = observations['composed_label']
    decomposed = observations['decomposed_label']
    assert composed['raw'] != decomposed['raw']
    assert composed['nfc'] == decomposed['nfc'] == 'Caf\u00e9'
    assert (composed['code_points'], composed['utf8_bytes']) == (4, 5)
    assert (decomposed['code_points'], decomposed['utf8_bytes']) == (5, 6)
    assert (composed['utf16_units'], decomposed['utf16_units']) == (4, 5)

    index = {}
    add_label(index, values['composed_label'], 'supplier-A')
    try:
        add_label(index, values['decomposed_label'], 'supplier-B')
    except ValueError as error:
        assert str(error) == 'canonical label collision'
    else:
        raise AssertionError('Second equivalent label overwrote the first')
    assert index == {'Caf\u00e9': 'supplier-A'}

    # Opaque IDs have exact-byte identity in this fixture; compatibility folding
    # would silently merge two distinct IDs and is therefore not their policy.
    assert values['circled_id'] != values['ascii_id']
    assert observations['circled_id']['nfc'] != observations['ascii_id']['nfc']
    assert observations['circled_id']['nfkc'] == observations['ascii_id']['nfkc'] == '1'
    assert observations['latin_a']['nfc'] != observations['cyrillic_a']['nfc']
    print(json.dumps({
        'versions': {'python_unicode': unicodedata.unidata_version,
                     'node_unicode': node['unicode_version']},
        'label': {'raw_equal': False, 'nfc_equal': True,
                  'raw_code_points': [composed['code_points'], decomposed['code_points']],
                  'raw_utf8_bytes': [composed['utf8_bytes'], decomposed['utf8_bytes']],
                  'second_insert': 'rejected; first record preserved'},
        'opaque_ids': {'raw_distinct': True, 'nfkc_would_merge': True},
        'lookalike_scripts': {'nfc_distinct': True},
        'scope': 'Local authored strings only; no identity, database, AWS or security review',
    }, ensure_ascii=False))


if __name__ == '__main__':
    run()
