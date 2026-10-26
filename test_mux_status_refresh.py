import os,tempfile,unittest,uuid,re
from types import SimpleNamespace
from unittest.mock import AsyncMock,MagicMock,patch

TMP=tempfile.TemporaryDirectory()
os.environ['SQLITE_PATH']=TMP.name+'/mux-refresh.db'
os.environ['DATABASE_URL']=''
os.environ['SEED_DEMO']='0'
os.environ['MUX_TOKEN_ID']='test-id'
os.environ['MUX_TOKEN_SECRET']='test-secret'
os.environ['MUX_WEBHOOK_SECRET']='test-webhook-secret'

from fastapi.testclient import TestClient
from main import app
from db import one,write
from security import hash_password,digest

class MuxVideoRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=TestClient(app);cls.client.__enter__()
        write('INSERT INTO staff(id,email,name,password_hash,role) VALUES (?,?,?,?,?)',('mux-refresh-admin','admin@example.test','Mux Admin',hash_password('Test-Password-12345'),'super_admin'))

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None,None,None);TMP.cleanup()

    def login(self):
        client=TestClient(app)
        page=client.get('/fr')
        public_csrf=re.search(r'name="csrf-token" content="([^"]+)"',page.text)[1]
        response=client.post('/admin/login',data={'email':'admin@example.test','password':'Test-Password-12345','csrf_token':public_csrf})
        self.assertEqual(response.status_code,200)
        session=one('SELECT csrf FROM sessions WHERE token_hash=?',(digest(client.cookies['vyora_staff']),))
        return client,session['csrf']

    def test_refresh_publishes_ready_asset_and_keeps_preparing_asset_pending(self):
        ready_id='mux-refresh-ready-'+uuid.uuid4().hex[:8]
        processing_id='mux-refresh-processing-'+uuid.uuid4().hex[:8]
        write('INSERT INTO videos(id,slug,title,asset_id,status,created_at) VALUES (?,?,?,?,?,?)',(ready_id,ready_id,'Ready video','asset-ready','processing','2026-01-01T00:00:00+00:00'))
        write('INSERT INTO videos(id,slug,title,asset_id,status,created_at) VALUES (?,?,?,?,?,?)',(processing_id,processing_id,'Processing video','asset-processing','processing','2026-01-02T00:00:00+00:00'))
        mux=MagicMock()
        async def get(url,auth=None):
            asset_id=url.rsplit('/',1)[-1]
            if asset_id=='asset-ready':
                return SimpleNamespace(status_code=200,json=lambda:{'data':{'id':'asset-ready','status':'ready','playback_ids':[{'id':'playback-ready','policy':'public'}]}})
            return SimpleNamespace(status_code=200,json=lambda:{'data':{'id':'asset-processing','status':'preparing','playback_ids':[]}})
        mux.get=AsyncMock(side_effect=get)
        manager=MagicMock();manager.__aenter__=AsyncMock(return_value=mux);manager.__aexit__=AsyncMock(return_value=False)
        client,csrf_token=self.login()
        with patch('main.httpx.AsyncClient',return_value=manager):
            response=client.post('/admin/videos/refresh',data={'csrf_token':csrf_token},follow_redirects=False)
        self.assertEqual(response.status_code,303)
        ready=one('SELECT status,playback_id FROM videos WHERE id=?',(ready_id,))
        still_processing=one('SELECT status FROM videos WHERE id=?',(processing_id,))
        self.assertEqual(ready,{'status':'ready','playback_id':'playback-ready'})
        self.assertEqual(still_processing['status'],'processing')
        self.assertIn('ready=1',response.headers['location'])
        self.assertIn('processing=1',response.headers['location'])

if __name__=='__main__':unittest.main(verbosity=2)
