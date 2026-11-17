"""Serialized response/client matrix; no HTTP, AWS or deployed-client evidence."""
import json


MESSAGES = {'accepted':'Request saved', 'completed':'Repair completed', 'rejected':'Repair rejected'}


def legacy_client(wire):
    body = json.loads(wire)
    return body['request_id'], MESSAGES[body['state']]


def strict_client(wire):
    body = json.loads(wire)
    if set(body) != {'request_id','state'}:
        raise ValueError('Unexpected response fields')
    return legacy_client(wire)


def prepared_client(wire):
    body = json.loads(wire)
    if not isinstance(body,dict) or not isinstance(body.get('request_id'),str) or not isinstance(body.get('state'),str):
        raise ValueError('Missing or invalid required response fields')
    return body['request_id'], MESSAGES.get(body['state'],'Status not understood; check through the supported recovery path')


def unsafe_client(wire):
    body = json.loads(wire)
    return 'Repair rejected' if body['state'] == 'rejected' else 'Repair completed'


def main():
    responses = {
        'original': {'request_id':'R17','state':'accepted'},
        'add_optional': {'request_id':'R17','state':'accepted','status_url':'/repairs/R17'},
        'rename_required': {'id':'R17','state':'accepted'},
        'new_business_state': {'request_id':'R17','state':'inspection_required'},
    }
    expected = {
        'original': (True,True,True),
        'add_optional': (True,False,True),
        'rename_required': (False,False,False),
        'new_business_state': (False,False,True),
    }
    for name,body in responses.items():
        wire=json.dumps(body).encode()
        results=[]
        for client in (legacy_client,strict_client,prepared_client):
            try: result=client(wire)
            except (KeyError,ValueError): results.append(False)
            else:
                results.append(True)
                assert result[0]=='R17'
                if name=='new_business_state': assert result[1].startswith('Status not understood')
                else: assert result[1]=='Request saved'
        assert tuple(results)==expected[name]
        print(name, 'legacy / strict / prepared:', *results)
    unknown=json.dumps(responses['new_business_state']).encode()
    assert unsafe_client(unknown)=='Repair completed'
    assert prepared_client(unknown)[1]!='Repair completed'
    print('Negative control: unsafe default falsely reports completion for an unknown state.')
    # A rollback to the old consumer cannot read a newly produced state.
    try: legacy_client(unknown)
    except KeyError: print('Old consumer rollback fails on already-produced new state.')
    else: raise AssertionError('Expected incompatibility absent')
    print('PASS: bounded serialized fixture matrix; no installed-client inventory or deployment.')


if __name__=='__main__':
    main()
