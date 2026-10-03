"""V2 integration tests reuse the temporary test database from test_workflows."""
import io,json,os,uuid
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
import test_workflows as fixtures
from db import rows,one,write
from jobs import queue_translation,process_translation_jobs,enqueue_campaign,process_push_jobs,InvalidSubscription
from extensions import validate_image,verify_media
from PIL import Image

class Operations(fixtures.Fixture):
 # Avoid rerunning inherited V1 methods: this class extends only the fixtures/helpers.
 def test_categories_tags_and_seo(self):
  c,t=self.login();r=c.post('/admin/taxonomy/save',data={'csrf_token':t,'table':'categories','name':'Syans','active':'on','sort_order':'1'});self.assertEqual(r.status_code,200)
  self.assertIn('Syans',self.c.get('/ht/news').text);cat=one("SELECT * FROM categories WHERE name='Syans'");self.assertEqual(self.c.get('/ht/category/'+cat['slug']).status_code,200)
  self.assertEqual(c.post('/admin/taxonomy/save',data={'csrf_token':t,'table':'tags','name':'Dokimantè'}).status_code,200)
  a=one("SELECT * FROM articles WHERE slug='voix-qui-traversent-les-frontieres'")
  self.assertEqual(c.post('/admin/seo/save',data={'csrf_token':t,'target_type':'article','target_id':a['id'],'locale':'ht','title':'Tit SEO espesifik','description':'Deskripsyon SEO presi','noindex':'on'}).status_code,200)
  r=self.c.get('/ht/article/'+a['slug']);self.assertIn('<title>Tit SEO espesifik',r.text);self.assertIn('Deskripsyon SEO presi',r.text);self.assertIn('noindex,nofollow',r.text)
  for section in ['categories','tags','seo','newsletter','account']:
   self.assertEqual(c.get('/admin/'+section).status_code,200,section)
 def test_queue_dedup_budget_and_manual_translation(self):
  a=one("SELECT * FROM articles WHERE slug='mizik-nouvo-jenerasyon'");locale='es';version=a['updated_at']
  write('DELETE FROM translations WHERE target_id=? AND locale=?',(a['id'],locale));write('DELETE FROM translation_jobs WHERE target_id=? AND locale=?',(a['id'],locale))
  with patch.dict(os.environ,{'GOOGLE_TRANSLATION_KEY':'not-real-test-key'}):
   first=queue_translation('article',a,locale);second=queue_translation('article',a,locale);self.assertEqual(first['job_id'],second['job_id'])
   calls=[]
   def fake(payload,lang):calls.append(lang);return {k:'Tradui '+v for k,v in payload.items()}
   process_translation_jobs(fake,20);process_translation_jobs(fake,20);self.assertEqual(calls,[locale]);self.assertTrue(queue_translation('article',a,locale)['ok'])
   a2=one("SELECT * FROM articles WHERE slug='ti-istwa-gwo-enpak'");job=queue_translation('article',a2,'fr')
   write("UPDATE settings SET value='0' WHERE key='translation_limit'");process_translation_jobs(fake,20)
   self.assertEqual(one('SELECT status FROM translation_jobs WHERE id=?',(job['job_id'],))['status'],'blocked');write("UPDATE settings SET value='100000' WHERE key='translation_limit'")
   # Editor-created translation wins while a job is queued.
   version=a2['updated_at'];write('INSERT INTO translations VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO UPDATE SET data=excluded.data,manual=1',(str(uuid.uuid4()),'article',a2['id'],version,'fr',json.dumps({'title':'Tit manyèl'}),1,datetime.now(timezone.utc).isoformat()))
   write("UPDATE translation_jobs SET status='queued' WHERE id=?",(job['job_id'],));process_translation_jobs(fake,20)
   self.assertEqual(json.loads(one('SELECT data FROM translations WHERE target_id=? AND locale=?',(a2['id'],'fr'))['data'])['title'],'Tit manyèl')
 def test_push_targeting_caps_unsubscribe_and_idempotence(self):
  stamp=datetime.now(timezone.utc).isoformat();prefix=str(uuid.uuid4())
  for suffix,locale,topic in [('one','ht','Kilti'),('two','fr','Kilti'),('three','ht','Mizik')]:write('INSERT INTO push_subscriptions VALUES (?,?,?,?,?)',(prefix+suffix,'test-token-'+prefix+suffix,locale,topic,stamp))
  def campaign(n,topic='Kilti'):
   id=prefix+n;write('INSERT INTO campaigns(id,title,body,url,locale,status,created_at,topic) VALUES (?,?,?,?,?,?,?,?)',(id,'Tès kanpay','Yon mesaj tès','/ht/news','ht','draft',stamp,topic));return id
  first=campaign('first');self.assertTrue(enqueue_campaign(first));self.assertFalse(enqueue_campaign(first));sent=[]
  def fake(c,s):sent.append(s['visitor_hash'])
  process_push_jobs(fake,100);process_push_jobs(fake,100);self.assertEqual(sent,[prefix+'one'])
  write("UPDATE settings SET value='1' WHERE key='push_daily_limit'");second=campaign('second');enqueue_campaign(second);process_push_jobs(fake,100);self.assertEqual(len(sent),1)
  write('DELETE FROM push_subscriptions WHERE visitor_hash=?',(prefix+'one',));write("UPDATE deliveries SET next_try='' WHERE campaign_id=?",(second,));process_push_jobs(fake,100);self.assertEqual(one('SELECT status FROM deliveries WHERE campaign_id=?',(second,))['status'],'cancelled')
  write("UPDATE settings SET value='3' WHERE key='push_daily_limit'")
  for suffix in ['one','two','three']:write('DELETE FROM push_subscriptions WHERE visitor_hash=?',(prefix+suffix,))
 def test_metrics_and_private_bans(self):
  c,t=self.login();p=one("SELECT * FROM influencers WHERE slug='naelle-jean'")
  r=c.post('/admin/metrics/save',data={'csrf_token':t,'influencer_id':p['id'],'platform':'YouTube','followers':'123','source_url':'https://example.org/source','observed_at':'2026-01-01T12:00'});self.assertEqual(r.status_code,200)
  self.assertIn('https://example.org/source',self.c.get('/ht/influencer/naelle-jean').text)
  a=one("SELECT id FROM articles WHERE slug='voix-qui-traversent-les-frontieres'");token=self.token();r=self.c.post('/api/comments',json={'csrf_token':token,'target_type':'article','target_id':a['id'],'name':'Bann tès','body':'Yon kòmantè pou tès limit tanporè.'});id=r.json()['id']
  self.assertEqual(c.post('/admin/visitors/ban',data={'csrf_token':t,'comment_id':id,'hours':'1','reason':'Abi tès'}).status_code,200)
  self.assertEqual(self.c.post('/api/comments',json={'csrf_token':token,'target_type':'article','target_id':a['id'],'name':'Bann tès','body':'Yon lòt kòmantè.'}).status_code,403)
  c.post('/admin/visitors/unban',data={'csrf_token':t,'comment_id':id})
 def test_newsletter_and_accent_search(self):
  token=self.token();email=str(uuid.uuid4())+'@example.org'
  r=self.c.post('/api/newsletter/subscribe',json={'csrf_token':token,'email':email,'locale':'ht','consent':True});self.assertEqual(r.status_code,200);private=r.json()['unsubscribe_url'].split('token=')[1]
  self.assertEqual(self.c.get('/ht/newsletter-unsubscribe?token='+private).status_code,200);self.assertEqual(one('SELECT status FROM newsletter_subscribers WHERE email=?',(email,))['status'],'active')
  self.c.post('/api/newsletter/unsubscribe',json={'csrf_token':token,'token':private});self.assertEqual(one('SELECT status FROM newsletter_subscribers WHERE email=?',(email,))['status'],'unsubscribed')
  self.assertIn('Naëlle Jean',self.c.get('/ht/search?q=Naelle').text)
 def test_media_validation(self):
  image=io.BytesIO();Image.new('RGB',(32,24),'green').save(image,format='PNG');raw=image.getvalue();self.assertEqual(validate_image(raw,'image/png'),(32,24))
  with self.assertRaises(ValueError):validate_image(b'not-a-photo','image/png')
  with self.assertRaises(ValueError):validate_image(raw,'image/jpeg')
  c,t=self.login();staff=one("SELECT id FROM staff WHERE role='super_admin'");id=str(uuid.uuid4());stamp=datetime.now(timezone.utc).isoformat()
  write('INSERT INTO media_assets(id,object_key,url,content_type,status,staff_id,created_at) VALUES (?,?,?,?,?,?,?)',(id,'test-key','https://example.org/image.png','image/png','pending',staff['id'],stamp));record=one('SELECT * FROM media_assets WHERE id=?',(id,))
  class Storage:
   def get_object(self,**kw):return {'ContentLength':len(raw),'Body':io.BytesIO(raw)}
  with patch.dict(os.environ,{'S3_BUCKET':'test-bucket'}):self.assertTrue(verify_media(record,Storage())['ok'])
  self.assertEqual(one('SELECT status FROM media_assets WHERE id=?',(id,))['status'],'ready')
 def test_team_revocation_and_rtl(self):
  c,t=self.login();editor=one("SELECT id FROM staff WHERE role='editor'");e,et=self.login('editor')
  self.assertEqual(c.post('/admin/team/manage',data={'csrf_token':t,'id':editor['id'],'action':'disable'}).status_code,200)
  self.assertEqual(e.post('/admin/settings/save',data={'csrf_token':et,'brand':'invalid'}).status_code,401)
  c.post('/admin/team/manage',data={'csrf_token':t,'id':editor['id'],'action':'activate'})
  write('INSERT INTO supported_languages VALUES (?,?,?,?) ON CONFLICT(code) DO NOTHING',('ar','العربية',1,datetime.now(timezone.utc).isoformat()))
  r=self.c.get('/ar');self.assertEqual(r.status_code,200);self.assertIn('dir="rtl"',r.text)
  self.assertIn('Publicité',self.c.get('/fr/advertising').text);self.assertIn('Enviar mensagem',self.c.get('/pt-BR/contact').text)

 def test_private_submission_ownership_and_rich_content(self):
  from content import body_blocks
  from security import visitor,digest
  stamp=datetime.now(timezone.utc).isoformat();token=self.token();id=str(uuid.uuid4());cookie=self.c.cookies.get('vyora_visitor')
  write('INSERT INTO submission_assets VALUES (?,?,?,?,?,?,?)',(id,None,digest(cookie),'private-test.png','image/png',200,stamp))
  other=__import__('fastapi').testclient.TestClient(__import__('main').app);ot=self.token(other)
  payload={'csrf_token':ot,'kind':'news','name':'Sous tès','body':'Yon enfòmasyon ki bezwen revize.','attachments':id}
  self.assertEqual(other.post('/api/submissions',json=payload).status_code,403)
  payload['csrf_token']=token;self.assertEqual(self.c.post('/api/submissions',json=payload).status_code,200)
  self.assertIsNotNone(one('SELECT submission_id FROM submission_assets WHERE id=?',(id,))['submission_id'])
  blocks=body_blocks('## Yon tit\n\n> Yon sitasyon\n\n![Lejand](https://example.org/image.png)\n\nYon [lyen](https://example.org) ak <script>alert(1)</script>.')
  self.assertEqual([b['type'] for b in blocks],['heading','quote','image','paragraph'])
  self.assertEqual(blocks[-1]['parts'][1]['url'],'https://example.org')
  self.assertEqual(self.c.post('/api/submissions',content=b'x'*70000,headers={'content-type':'application/json'}).status_code,413)
 def test_reply_push_respects_consent_and_single_delivery(self):
  from security import digest
  a=one("SELECT id FROM articles WHERE slug='voix-qui-traversent-les-frontieres'");token=self.token();owner=digest(self.c.cookies.get('vyora_visitor'));stamp=datetime.now(timezone.utc).isoformat()
  write('INSERT INTO push_subscriptions VALUES (?,?,?,?,?) ON CONFLICT(visitor_hash) DO UPDATE SET token=excluded.token',(owner,'consented-test-token','ht','Kilti',stamp))
  r=self.c.post('/api/comments',json={'csrf_token':token,'target_type':'article','target_id':a['id'],'name':'Mèt kòmantè','body':'Yon kòmantè avèk opt-in pou repons.','subscribe_reply':True});parent=r.json()['id'];c,ct=self.login('moderator')
  c.post('/admin/moderate',data={'csrf_token':ct,'table':'comments','id':parent,'status':'approved','reason':'Valab pou tès'})
  other=__import__('fastapi').testclient.TestClient(__import__('main').app);ot=self.token(other)
  r=other.post('/api/comments',json={'csrf_token':ot,'target_type':'article','target_id':a['id'],'parent_id':parent,'name':'Lòt lektè','body':'Yon repons pou tès konsantman.'});child=r.json()['id']
  for _ in range(2):c.post('/admin/moderate',data={'csrf_token':ct,'table':'comments','id':child,'status':'approved','reason':'Valab pou tès'})
  self.assertEqual(one('SELECT count(*) n FROM campaigns WHERE id=?',('reply-'+child,))['n'],1)
  recipients=rows('SELECT visitor_hash FROM deliveries WHERE campaign_id=?',('reply-'+child,));self.assertEqual(recipients,[{'visitor_hash':owner}])
  self.c.post('/api/push/unsubscribe',json={'csrf_token':token});self.assertEqual(one('SELECT status FROM deliveries WHERE campaign_id=?',('reply-'+child,))['status'],'cancelled')
