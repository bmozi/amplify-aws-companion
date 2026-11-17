"""Real loopback HTTP correlation and alert delivery; no cloud or external recipients."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import uuid


@contextmanager
def serve(handler):
    server=ThreadingHTTPServer(('127.0.0.1',0),handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown();server.server_close();thread.join(timeout=2)
        assert not thread.is_alive()


def request(url, payload=None, headers=None):
    body=json.dumps(payload).encode() if payload is not None else None
    req=Request(url,data=body,headers=headers or {})
    try:
        with urlopen(req,timeout=3) as response:return response.status,json.load(response)
    except HTTPError as error:
        with error:return error.code,json.load(error)


class QuietHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass  # Default access logs could contain unreviewed request paths.
    def reply(self,status,payload):
        data=json.dumps(payload).encode()
        self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)


def main():
    logs=[];receipts={};deliveries=[]
    state={'dependency_ok':True,'receiver_ok':True}
    class Dependency(QuietHandler):
        def do_GET(self):
            trace=self.headers.get('X-Lab-Trace')
            status=200 if state['dependency_ok'] else 503
            logs.append({'service':'dependency','trace':trace,'status':status})
            self.reply(status,{'status':'ok' if status==200 else 'unavailable'})
    class Receiver(QuietHandler):
        def do_POST(self):
            packet=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if not state['receiver_ok']:
                self.reply(503,{'accepted':False});return
            # Synthetic bounded sender only; this receiver is not a production endpoint.
            if packet['event_id'] in receipts:
                assert receipts[packet['event_id']]==packet
            else:receipts[packet['event_id']]=packet
            self.reply(202,{'accepted':True,'event_id':packet['event_id']})
    with serve(Dependency) as dependency, serve(Receiver) as receiver:
        class Frontend(QuietHandler):
            def do_GET(self):
                trace=uuid.uuid4().hex  # Do not trust the caller's proposed correlation header.
                started=time.perf_counter()
                status,_=request(dependency+'/check',headers={'X-Lab-Trace':trace})
                logs.append({'service':'frontend','trace':trace,'status':status,
                             'elapsed_ms':round((time.perf_counter()-started)*1000,3)})
                self.reply(status,{'trace':trace,'status':'ok' if status==200 else 'unavailable'})
        with serve(Frontend) as frontend:
            outcomes=[]
            for available in [True,False,True]:
                state['dependency_ok']=available
                status,body=request(frontend+'/check?private=DO_NOT_LOG',
                    headers={'Authorization':'Bearer SYNTHETIC_SECRET','X-Lab-Trace':'caller-chosen'})
                outcomes.append((status,body['trace']))
            assert [status for status,_ in outcomes]==[200,503,200]
            assert len({trace for _,trace in outcomes})==3
            for status,trace in outcomes:
                events=[event for event in logs if event['trace']==trace]
                assert {e['service'] for e in events}=={'frontend','dependency'} and len(events)==2
                assert all(e['status']==status for e in events)
            assert all(e['elapsed_ms']>=0 for e in logs if e['service']=='frontend')
            encoded=json.dumps(logs)
            assert all(value not in encoded for value in ['SYNTHETIC_SECRET','DO_NOT_LOG','caller-chosen'])
            # One failed probe triggers this teaching alert; not a production SLO policy.
            failed_trace=outcomes[1][1]
            alert={'event_id':uuid.uuid4().hex,'kind':'probe_failed','trace':failed_trace,'status':503}
            def deliver():
                status,response=request(receiver+'/alerts',alert)
                acknowledged=status==202 and response.get('accepted') is True and response.get('event_id')==alert['event_id']
                deliveries.append({'http_status':status,'acknowledged':acknowledged})
                return acknowledged
            state['receiver_ok']=False
            assert not deliver() and not receipts  # Alert condition is not delivery evidence.
            state['receiver_ok']=True
            assert deliver() and deliver()  # Same stable ID; receiver stores one receipt.
            assert list(receipts.values())==[alert]
            assert any(e['service']=='dependency' and e['trace']==alert['trace'] and e['status']==503 for e in logs)
    print(json.dumps({'result':'passed','observed_http_statuses':[s for s,_ in outcomes],
        'correlated_requests':len(outcomes),'log_events':len(logs),'deliveries':deliveries,
        'unique_alert_receipts':len(receipts),'logs':logs,
        'scope':'Actual sequential loopback HTTP and local receiver receipt; no AWS, TLS, OTel or human notification'},indent=2))


if __name__=='__main__':main()
