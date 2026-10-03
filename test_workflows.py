import os,tempfile,unittest,uuid,re,json,time,hmac,hashlib
TMP=tempfile.TemporaryDirectory();os.environ['SQLITE_PATH']=TMP.name+'/test.db';os.environ['DATABASE_URL']='';os.environ['SEED_DEMO']='1';os.environ['ALLOW_DEMO_CONTENT']='1';os.environ['MUX_WEBHOOK_SECRET']='test-secret'
from fastapi.testclient import TestClient
from main import app
from db import one,rows,write
from security import hash_password,digest
from worker import tick
class Fixture(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.c=TestClient(app);cls.c.__enter__()
  for role in ['super_admin','editor','moderator']:write('INSERT INTO staff(id,email,name,password_hash,role) VALUES (?,?,?,?,?)',(str(uuid.uuid4()),role+'@test.local',role,hash_password('Test-Password-12345'),role))
 @classmethod
 def tearDownClass(cls):cls.c.__exit__(None,None,None);TMP.cleanup()
 def token(self,c=None):return re.search('name="csrf-token" content="([^"]+)"',(c or self.c).get('/ht').text)[1]
 def login(self,role='super_admin'):
  c=TestClient(app);t=self.token(c);r=c.post('/admin/login',data={'email':role+'@test.local','password':'Test-Password-12345','csrf_token':t});self.assertEqual(r.status_code,200);return c,one('SELECT csrf FROM sessions WHERE token_hash=?',(digest(c.cookies['vyora_staff']),))['csrf']
class Workflows(Fixture):
 def test_routes(self):
  for l in ['ht','fr','en','pt-BR','es']:
   for p in ['', '/news','/haiti','/world','/interviews','/videos','/influencers','/notifications','/saved','/contact','/about','/search?q=Kreyativite','/trending']:
    self.assertEqual(self.c.get('/'+l+p).status_code,200,l+p)
  self.assertEqual(self.c.get('/',headers={'accept-language':'pt-BR,pt;q=.8'}).url.path,'/pt-BR');self.assertEqual(self.c.get('/ht/unknown').status_code,404)
 def test_admin_publish_and_revisions(self):
  c,t=self.login()
  for s in ['','articles','influencers','videos','comments','reports','submissions','translations','analytics','settings','team','notifications','ads','audit']:self.assertEqual(c.get('/admin'+('/'+s if s else '')).status_code,200,s)
  f={'csrf_token':t,'title':'Tès editoryal reyèl','body':'Kontni pou verifye piblikasyon nan CMS la.','category':'Kilti','author':'Editè tès','status':'draft','locale':'ht','slug':'integration-test'}
  r=c.post('/admin/articles/save',data=f);self.assertEqual(r.status_code,200,r.text[:100]);a=one("SELECT * FROM articles WHERE slug='integration-test'")
  self.assertEqual(self.c.get('/ht/article/integration-test').status_code,404);self.assertEqual(c.get('/admin/preview/'+a['id']).status_code,200);self.assertEqual(TestClient(app).get('/admin/preview/'+a['id']).status_code,401)
  f.update(id=a['id'],status='published');self.assertEqual(c.post('/admin/articles/save',data=f).status_code,200);self.assertEqual(self.c.get('/ht/article/integration-test').status_code,200);self.assertIn('Tès editoryal reyèl',self.c.get('/ht/search?q=editoryal').text)
  f['title']='Tit korije';c.post('/admin/articles/save',data=f);self.assertTrue(rows('SELECT * FROM revisions WHERE article_id=?',(a['id'],)))
 def test_comments_threads_moderation_and_ownership(self):
  a=one("SELECT id FROM articles WHERE slug='voix-qui-traversent-les-frontieres'");t=self.token();d={'csrf_token':t,'target_type':'article','target_id':a['id'],'name':'Lektè tès','body':'Yon kòmantè pou moderasyon.'};r=self.c.post('/api/comments',json=d);self.assertEqual(r.status_code,200);id=r.json()['id']
  self.assertFalse(self.c.get('/api/comments',params={'target_type':'article','target_id':a['id']}).json()['comments'])
  c,ct=self.login('moderator');self.assertEqual(c.post('/admin/moderate',data={'csrf_token':ct,'table':'comments','id':id,'status':'approved','reason':'Règleman respekte'}).status_code,200)
  d.update(parent_id=id,body='Repons ki nan bon thread la.');r=self.c.post('/api/comments',json=d);self.assertEqual(r.status_code,200);self.assertEqual(one('SELECT parent_id FROM comments WHERE id=?',(r.json()['id'],))['parent_id'],id)
  other=TestClient(app);ot=self.token(other);self.assertEqual(other.post('/api/comments/'+id+'/manage',json={'csrf_token':ot,'action':'delete'}).status_code,403)
  for _ in range(2):self.assertEqual(self.c.post('/api/reports',json={'csrf_token':t,'target_type':'comment','target_id':id,'reason':'spam'}).status_code,200)
  self.assertEqual(one('SELECT count(*) n FROM reports WHERE target_id=?',(id,))['n'],1)
  for _ in range(2):self.c.post('/api/comments/'+id+'/like',json={'csrf_token':t})
  self.assertEqual(one('SELECT count(*) n FROM reactions WHERE comment_id=?',(id,))['n'],0)
 def test_security(self):
  c,t=self.login('editor');self.assertEqual(c.post('/admin/settings/save',data={'csrf_token':t,'brand':'Attack'}).status_code,403);self.assertEqual(c.post('/admin/articles/save',data={'csrf_token':'bad'}).status_code,403)
  t=self.token();self.assertEqual(self.c.post('/api/submissions',json={'csrf_token':t,'kind':'contact','name':'Tès','body':'Mesaj valid.'},headers={'origin':'https://attacker.invalid'}).status_code,403);self.assertEqual(self.c.post('/api/webhooks/mux',content='{}').status_code,401)
 def test_mux_and_jobs(self):
  id=str(uuid.uuid4());stamp='2000-01-01T00:00:00+00:00';write('INSERT INTO videos(id,slug,title,status,created_at) VALUES (?,?,?,?,?)',(id,'mux-test','Mux Test','processing',stamp));raw=json.dumps({'id':'event-test','type':'video.asset.ready','data':{'id':'asset-test','passthrough':id,'playback_ids':[{'id':'playback-test','policy':'public'}]}}).encode();ts=str(int(time.time()));sig=hmac.new(b'test-secret',ts.encode()+b'.'+raw,hashlib.sha256).hexdigest();h={'mux-signature':'t='+ts+',v1='+sig}
  self.assertEqual(self.c.post('/api/webhooks/mux',content=raw,headers=h).status_code,200);self.assertTrue(self.c.post('/api/webhooks/mux',content=raw,headers=h).json()['duplicate']);self.assertEqual(one('SELECT status FROM videos WHERE id=?',(id,))['status'],'ready')
  a=one("SELECT id FROM articles WHERE slug='kreyativite-san-limit'");write("UPDATE articles SET status='scheduled',publish_at=? WHERE id=?",(stamp,a['id']));self.assertEqual(tick(),1);self.assertEqual(tick(),0)
 def test_translation_and_persistence(self):
  t=self.token();a=one("SELECT id FROM articles WHERE slug='voix-qui-traversent-les-frontieres'");payload={'csrf_token':t,'target_type':'article','target_id':a['id'],'locale':'fr'};self.assertFalse(self.c.post('/api/translate',json=payload).json()['ok']);c,ct=self.login();self.assertEqual(c.post('/admin/translations/save',data={'csrf_token':ct,'target_type':'article','target_id':a['id'],'locale':'fr','title':'Traduction éditoriale','body':'Texte français.'}).status_code,200);self.assertTrue(self.c.post('/api/translate',json=payload).json()['ok'])
  self.assertEqual(self.c.post('/api/submissions',json={'csrf_token':t,'kind':'influencer','name':'Kreyatè tès','body':'Pwofil pou revizyon ak lyen sosyal.'}).status_code,200);self.assertTrue(one("SELECT id FROM submissions WHERE name='Kreyatè tès'"))
if __name__=='__main__':unittest.main(verbosity=2)
