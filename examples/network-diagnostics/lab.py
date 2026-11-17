"""Loopback HTTP observations plus a deliberately small IPv4 routing model. No AWS calls."""
import argparse
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import ipaddress
import json
from pathlib import Path
import socket
import threading

# Deliberately public fixture strings; these are not real credentials or a production auth design.
FIXTURE_USERS = {'fixture-alice': 'alice', 'fixture-bob': 'bob'}


def select_route(destination, routes):
    address=ipaddress.IPv4Address(destination)
    parsed=[(ipaddress.IPv4Network(r['destination']),r) for r in routes]
    if len({network for network,_ in parsed})!=len(parsed):
        raise ValueError('Duplicate destinations are outside this small model')
    matching=[(network,r) for network,r in parsed if address in network]
    if not matching:return None
    return max(matching,key=lambda item:item[0].prefixlen)[1].copy()


def route_drill():
    routes=[{'destination':'0.0.0.0/0','target':'egress','state':'active'},
            {'destination':'10.20.0.0/16','target':'local','state':'active'},
            {'destination':'10.20.8.0/24','target':'inspection','state':'blackhole'}]
    selected=select_route('10.20.8.9',routes)
    assert selected['target']=='inspection' and selected['state']=='blackhole'
    # Selecting a more general healthy route would hide the failure, and be wrong for this exercise.
    assert select_route('10.20.9.9',routes)['target']=='local'
    assert select_route('203.0.113.7',routes)['target']=='egress'
    assert select_route('192.0.2.1',routes[1:]) is None
    try:select_route('10.20.8.9',routes+[routes[0]])
    except ValueError:pass
    else:raise AssertionError('Ambiguous duplicate route must be rejected')
    return {'specific_failed_route':selected,'local_route':'local','default_route':'egress',
            'no_match':None,'duplicate_destination_rejected':True,
            'scope':'IPv4 longest-prefix model only; no AWS tie-breaking, propagation, endpoints or packet forwarding'}


def http_drill():
    observations=[]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.path=='/unavailable':status,body=503,{'error':'synthetic_dependency_unavailable'}
            elif self.path!='/notes/alice':status,body=404,{'error':'not_found'}
            else:
                scheme,separator,credential=self.headers.get('Authorization','').partition(' ')
                actor=FIXTURE_USERS.get(credential) if separator and scheme.lower()=='bearer' else None
                if actor is None:status,body=401,{'error':'sign_in_required'}
                elif actor!='alice':status,body=403,{'error':'forbidden'}
                else:status,body=200,{'note':'Synthetic private note'}
            payload=json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(payload)))
            if status==401:self.send_header('WWW-Authenticate','Bearer realm="fixture"')
            self.end_headers();self.wfile.write(payload)
            observations.append({'path':self.path,'status':status})
    server=HTTPServer(('127.0.0.1',0),Handler)
    port=server.server_address[1]
    worker=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':0.01},daemon=True)
    worker.start()
    def request(path,token=None,raw_header=None):
        client=http.client.HTTPConnection('127.0.0.1',port,timeout=2)
        try:
            headers={} if token is None else {'Authorization':'Bearer '+token}
            if raw_header is not None:headers['Authorization']=raw_header
            client.request('GET',path,headers=headers)
            reply=client.getresponse();return reply.status,json.loads(reply.read())
        finally:client.close()
    try:
        owner=request('/notes/alice','fixture-alice')
        stranger=request('/notes/alice','fixture-bob')
        unsigned=request('/notes/alice')
        invalid=request('/notes/alice','fixture-invalid')
        malformed=request('/notes/alice',raw_header='fixture-alice')
        unavailable=request('/unavailable')
        assert owner==(200,{'note':'Synthetic private note'})
        assert stranger==(403,{'error':'forbidden'})
        assert unsigned[0]==invalid[0]==malformed[0]==401
        assert unavailable[0]==503
        assert all('note' not in body for _,body in [stranger,unsigned,invalid,malformed,unavailable])
    finally:
        server.shutdown();server.server_close();worker.join(timeout=2)
    assert not worker.is_alive() and server.socket.fileno()==-1
    # No listener is expected after cleanup. This is a refusal, not a simulated timeout.
    try:
        with socket.create_connection(('127.0.0.1',port),timeout=1):
            raise AssertionError('Unexpected listener on the just-released port; inspect local environment')
    except ConnectionRefusedError:transport='connection_refused'
    return {'observed_http':observations,'after_cleanup':transport,'server_stopped':True,
            'scope':'Real loopback HTTP and application fixture authorization; no TLS, external DNS or AWS policy evaluation'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result={'http':http_drill(),'routes':route_drill()}
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')

if __name__=='__main__':main()
