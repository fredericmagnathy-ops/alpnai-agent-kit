"""Real stdlib client against a loopback HTTP server; no external requests or credentials."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
import uuid

KIT=Path(__file__).resolve().parents[2]
CLIENT=KIT/'examples/save_project.py'
sys.path.insert(0,str(KIT/'examples'))
spec=importlib.util.spec_from_file_location('save_project',CLIENT)
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
KEY='alp_test_OFFLINE_LOOPBACK_ONLY'
INPUT={'runs':[{'task_id':'opaque-1','workflow':'extract','variant':'baseline','cost_usd':0.01,'success':True},{'task_id':'opaque-1','workflow':'extract','variant':'candidate','cost_usd':0.005,'success':True}]}
RAW=json.dumps(INPUT).encode()

@contextmanager
def fixture(mode='ok'):
    seen=[];saved={};state={'mode':mode,'status':200}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*_):pass
        def do_POST(self):
            body=self.rfile.read(int(self.headers['Content-Length']))
            data=json.loads(body);seen.append((self.path,self.headers.get('Authorization'),body))
            if state['mode']=='redirect':
                self.send_response(307);self.send_header('Location',base+'/should-never-be-called');self.end_headers();return
            if state['mode']=='error':
                payload={'error':'SECRET_SERVER_BODY_'+KEY};status=state['status']
            else:
                past=data['request_id'] in saved
                report_id=saved.setdefault(data['request_id'],str(uuid.uuid4()))
                payload={'id':report_id,'replayed':past,'saved':True,'persistence':'computed_summary','payment_authorized':False,'ignored_secret':KEY}
                status=200
                if state['mode']=='invalid':payload['payment_authorized']=True
                if state['mode']=='lost':
                    state['mode']='ok';self.connection.shutdown(socket.SHUT_RDWR);self.connection.close();return
            encoded=json.dumps(payload).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(encoded)));self.end_headers();self.wfile.write(encoded)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);base=f'http://127.0.0.1:{server.server_port}'
    thread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':.01},daemon=True);thread.start()
    try:yield base,seen,saved,state
    finally:server.shutdown();server.server_close();thread.join(timeout=2)

class SaveProjectTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.state=Path(self.tmp.name)/'private/state.json'
    def save(self,base,**extra):
        values={'base':base,'key':KEY,'raw':RAW,'title':'Version 1','state_path':self.state,'allow_loopback':True,'attempts':1}
        values.update(extra);return client.save_project(**values)
    def test_real_request_and_private_no_secret_state(self):
        with fixture() as (base,seen,saved,_):
            result=self.save(base)
            self.assertEqual(seen[0][:2],('/api/v1/project-reports','Bearer '+KEY))
            body=json.loads(seen[0][2]);self.assertEqual(body['input'],INPUT);self.assertEqual(body['title'],'Version 1');self.assertNotIn('project',body)
            state=json.loads(self.state.read_text());self.assertEqual(set(state),{'version','request_id','fingerprint'});self.assertEqual(body['request_id'],state['request_id']);self.assertEqual(self.state.stat().st_mode&0o777,0o600)
            self.assertNotIn(KEY,self.state.read_text());self.assertNotIn('opaque-1',self.state.read_text());self.assertNotIn('Version 1',self.state.read_text());self.assertNotIn(KEY,json.dumps(result));self.assertFalse(result['payment_authorized']);self.assertEqual(len(saved),1)
    def test_restart_replays_same_uuid_and_body(self):
        with fixture() as (base,seen,saved,_):
            first=self.save(base);second=self.save(base)
            self.assertEqual(first['id'],second['id']);self.assertTrue(second['replayed']);self.assertEqual(seen[0][2],seen[1][2]);self.assertEqual(len(saved),1)
    def test_lost_response_retries_same_persisted_id(self):
        with fixture('lost') as (base,seen,saved,_),patch.object(client.time,'sleep'):
            result=self.save(base,attempts=2);self.assertTrue(result['replayed']);self.assertEqual(len(saved),1);self.assertEqual(len(seen),2);self.assertEqual(seen[0][2],seen[1][2])
    def test_parameter_or_key_change_blocked_locally(self):
        with fixture() as (base,seen,_,_):
            self.save(base)
            for change in [{'title':'Other version'},{'key':KEY+'OTHER'},{'raw':json.dumps({**INPUT,'config':{'minSamples':3}}).encode()}]:
                with self.subTest(change=next(iter(change))),self.assertRaises(client.ClientError):self.save(base,**change)
            self.assertEqual(len(seen),1)
        with fixture() as (newbase,seen,_,_):
            with self.assertRaises(client.ClientError):self.save(newbase)
            self.assertEqual(seen,[])
    def test_key_order_and_whitespace_normalize_to_same_body(self):
        with fixture() as (base,seen,_,_):
            self.save(base);self.save(base,raw=json.dumps(INPUT,sort_keys=True,indent=2).encode())
            self.assertEqual(seen[0][2],seen[1][2])
    def test_redirect_never_forwards_to_destination(self):
        with fixture('redirect') as (base,seen,_,_):
            with self.assertRaises(client.ClientError):self.save(base)
            self.assertEqual(len(seen),1);self.assertEqual(seen[0][0],'/api/v1/project-reports');self.assertTrue(self.state.exists())
    def test_unapproved_origins_and_implicit_loopback_rejected(self):
        for base in ['https://attacker.example','https://alpnai.com.attacker.example','https://user@alpnai.com','https://alpnai.com/path','http://alpnai.com','https://alpnai.com:444','http://127.0.0.1:9999']:
            with self.subTest(base=base),self.assertRaises(client.ClientError):client.origin(base)
        self.assertEqual(client.origin('https://alpnai.com:443/'),'https://alpnai.com')
    def test_invalid_input_never_sends_or_creates_state(self):
        with fixture() as (base,seen,_,_):
            for extra in [{'title':'\x00secret'},{'key':'0xWALLET_SECRET'},{'raw':b'{"runs":[],"prompt":"secret"}'},{'attempts':5},{'timeout':float('nan')}]:
                with self.subTest(extra=next(iter(extra))),self.assertRaises(client.ClientError):self.save(base,**extra)
            self.assertEqual(seen,[]);self.assertFalse(self.state.exists())
    def test_existing_lock_prevents_concurrent_new_request(self):
        with fixture() as (base,seen,_,_),client.locked_state(self.state):
            with self.assertRaises(client.ClientError):self.save(base)
            self.assertEqual(seen,[])
    def test_public_or_malformed_state_refused_without_request(self):
        with fixture() as (base,seen,_,_):
            self.save(base);self.state.chmod(0o644)
            with self.assertRaises(client.ClientError):self.save(base)
            self.state.chmod(0o600);self.state.write_text('{bad')
            with self.assertRaises(client.ClientError):self.save(base)
            self.assertEqual(len(seen),1)
    def test_rate_limit_retries_bounded_but_quota_auth_never_auto_retry(self):
        with fixture('error') as (base,seen,_,state),patch.object(client.time,'sleep'):
            state['status']=429
            with self.assertRaises(client.RetryableError):self.save(base,attempts=3)
            self.assertEqual(len(seen),3);self.assertEqual(len({v[2] for v in seen}),1)
            for code in [401,403,409]:
                state['status']=code;count=len(seen)
                with self.assertRaises(client.ClientError) as e:self.save(base,attempts=3)
                self.assertEqual(len(seen),count+1);self.assertNotIn(KEY,str(e.exception));self.assertNotIn('SECRET_SERVER_BODY',str(e.exception))
    def test_unexpected_confirmation_preserves_state_and_omits_body(self):
        with fixture('invalid') as (base,seen,_,_):
            with self.assertRaises(client.ClientError) as e:self.save(base)
            self.assertTrue(self.state.exists());self.assertNotIn(KEY,str(e.exception));self.assertEqual(len(seen),1)
    def test_real_cli_success_and_same_state_restart(self):
        with fixture() as (base,seen,saved,_):
            source=Path(self.tmp.name)/'input.json';source.write_bytes(RAW)
            env={**os.environ,'PYTHONPATH':str(KIT/'examples'),'ALPNAI_AGENT_KEY':KEY,'NO_PROXY':'127.0.0.1','no_proxy':'127.0.0.1'}
            command=[sys.executable,str(CLIENT),'--input',str(source),'--title','CLI fixture','--state',str(self.state),'--base-url',base,'--allow-loopback','--attempts','1']
            first=subprocess.run(command,env=env,capture_output=True,text=True,timeout=10);second=subprocess.run(command,env=env,capture_output=True,text=True,timeout=10)
            self.assertEqual(first.returncode,0,first.stderr);self.assertEqual(second.returncode,0,second.stderr);self.assertNotIn(KEY,first.stdout+first.stderr+second.stdout+second.stderr);self.assertFalse(json.loads(first.stdout)['replayed']);self.assertTrue(json.loads(second.stdout)['replayed']);self.assertEqual(len(saved),1)

if __name__=='__main__':unittest.main()
