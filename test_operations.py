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
 def test_profile_edit_refreshes_translation_cache(self):
  profile=one("SELECT * FROM influencers WHERE slug='naelle-jean'")
  previous=profile['updated_at'] or profile['created_at']
  write("DELETE FROM translations WHERE target_type='influencer' AND target_id=? AND locale='fr'",(profile['id'],))
  write('INSERT INTO translations VALUES (?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),'influencer',profile['id'],previous,'fr',json.dumps({'bio':'Ansyen tradiksyon'}),1,datetime.now(timezone.utc).isoformat()))
  client,token=self.login()
  form={'csrf_token':token,'id':profile['id'],'slug':profile['slug'],'name':profile['name'],'username':profile['username'],'origin':profile['origin'],'residence':profile['residence'],'category':profile['category'],'bio':'Nouvo bio pou verifye invalidasyon tradiksyon an.','image':profile['image'],'languages':profile['languages'],'status':profile['status']}
  if profile['demo']:form['demo']='on'
  for platform,url in json.loads(profile['socials'] or '{}').items():form[platform]=url
  self.assertEqual(client.post('/admin/influencers/save',data=form).status_code,200)
  updated=one('SELECT * FROM influencers WHERE id=?',(profile['id'],))
  self.assertNotEqual(updated['updated_at'],previous)
  with patch.dict(os.environ,{'GOOGLE_TRANSLATION_KEY':''}):
   result=queue_translation('influencer',updated,'fr')
  self.assertFalse(result['ok'])
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

 def test_b2_presigned_put(self):
  from unittest.mock import Mock
  client=Mock();client.generate_presigned_url.return_value='https://example.test/upload'
  c,t=self.login()
  with patch.dict(os.environ,{'S3_BUCKET':'public-test','S3_ACCESS_KEY_ID':'test-key','S3_SECRET_ACCESS_KEY':'test-secret','MEDIA_PUBLIC_URL':'https://example.test/public'}),patch('boto3.client',return_value=client):
   r=c.post('/admin/media/upload-url',data={'csrf_token':t,'content_type':'image/jpeg'})
  self.assertEqual(r.status_code,200);self.assertEqual(r.json()['method'],'PUT');self.assertEqual(r.json()['headers'],{'Content-Type':'image/jpeg'})
  self.assertEqual(client.generate_presigned_url.call_args.args[0],'put_object')
  client.generate_presigned_post.assert_not_called()

 def test_private_document_upload_validation_and_ownership(self):
  from unittest.mock import Mock
  from extensions import validate_attachment
  from fastapi.testclient import TestClient
  from main import app
  document=b'%PDF-1.7\n1 0 obj<<>>endobj\n%%EOF'
  self.assertEqual(validate_attachment(document,'proof.pdf','application/pdf'),('application/pdf','.pdf'))
  for raw,name,mime in [(b'fake','proof.pdf','application/pdf'),(b'<svg/>','photo.svg','image/svg+xml'),(b'hello\x00','note.txt','text/plain')]:
   with self.assertRaises(ValueError):validate_attachment(raw,name,mime)
  self.assertEqual(validate_attachment('Sous vérifiée'.encode(),'notes.txt','text/plain')[0],'text/plain; charset=utf-8')
  token=self.token();storage=Mock()
  with patch.dict(os.environ,{'PRIVATE_SUBMISSION_BUCKET':'private-test'}),patch('extensions.s3_client',return_value=storage):
   response=self.c.post('/api/submissions/upload',data={'csrf_token':token},files={'file':('proof.pdf',document,'application/pdf')})
   self.assertEqual(response.status_code,200,response.text);id=response.json()['id']
   self.assertEqual(storage.put_object.call_args.kwargs['Bucket'],'private-test')
   self.assertIn('attachment',storage.put_object.call_args.kwargs['ContentDisposition'])
   self.assertEqual(storage.put_object.call_args.kwargs['ContentType'],'application/pdf')
   other=TestClient(app);other_token=self.token(other)
   payload={'csrf_token':other_token,'kind':'contact','name':'Proof request','body':'Please review this document.','attachments':id}
   self.assertEqual(other.post('/api/submissions',json=payload).status_code,403)
   payload['csrf_token']=token
   self.assertEqual(self.c.post('/api/submissions',json=payload).status_code,200)
   self.assertEqual(self.c.post('/api/submissions',json=payload).status_code,403)
   self.assertEqual(TestClient(app).get('/admin/submission-assets/'+id).status_code,401)

 def test_production_interface_and_demo_visibility(self):
  from localization import ui_text
  from html.parser import HTMLParser
  class VisibleText(HTMLParser):
   def __init__(self):super().__init__();self.text=[]
   def handle_data(self,text):self.text.append(text.strip())
  with patch.dict(os.environ,{'ALLOW_DEMO_CONTENT':'0'}):
   self.assertEqual(self.c.get('/en/article/voix-qui-traversent-les-frontieres').status_code,404)
   self.assertEqual(self.c.get('/en/influencer/naya-lumiere').status_code,404)
   for lang in ['fr','en','pt-BR','es']:
    response=self.c.get('/'+lang+'/discoveries');parser=VisibleText();parser.feed(response.text)
    for source in ['Komedi','Mòd','Bote','Biznis','Teknoloji','Espò','Kwizin','Edikasyon','Vwayaj','Dekouvèt']:
     self.assertIn(ui_text(source,lang),parser.text)
     self.assertNotIn(source,parser.text)
    for page in ['about','privacy','terms','cookies','editorial','community','copyright']:
     response=self.c.get('/'+lang+'/'+page);self.assertEqual(response.status_code,200)
     self.assertNotIn('Tèks pwovizwa',response.text);self.assertNotIn('FÈ AK KREYATIVITE',response.text)
     self.assertIn('/static/geovyora-mark.png',response.text)

 @patch('main.rate')
 def test_admin_languages_preserve_editorial_values_and_diagnostics(self,rate_mock):
  from unittest.mock import patch
  from localization import ui_text
  c,t=self.login();stamp=datetime.now(timezone.utc).isoformat();article=one("SELECT id FROM articles LIMIT 1")
  write('UPDATE articles SET title=?,body=? WHERE id=?',('Tit','Paramèt',article['id']))
  keys={'MUX_TOKEN_ID':'','MUX_TOKEN_SECRET':'','S3_BUCKET':'','S3_ENDPOINT_URL':'','S3_REGION':'','S3_ACCESS_KEY_ID':'','S3_SECRET_ACCESS_KEY':'','MEDIA_PUBLIC_URL':'','FIREBASE_PUBLIC_CONFIG':'','FIREBASE_SERVICE_ACCOUNT':'','FIREBASE_VAPID_KEY':''}
  expected={'fr':'Vue d’ensemble','en':'Overview','pt-BR':'Visão geral','es':'Resumen'}
  with patch.dict(os.environ,keys):
   for locale,caption in expected.items():
    r=c.get('/admin?lang='+locale);self.assertEqual(r.status_code,200);self.assertIn(caption,r.text);self.assertIn('id="admin-language"',r.text);self.assertIn('<code>MUX_TOKEN_ID</code>',r.text)
    r=c.get('/admin/articles?edit='+article['id']+'&lang='+locale);self.assertEqual(r.status_code,200)
    self.assertIn('name="title" value="Tit"',r.text);self.assertIn('>Paramèt</textarea>',r.text)
    self.assertIn('value="Kilti"',r.text);self.assertIn('value="draft"',r.text);self.assertIn('editor-image-file',r.text);self.assertIn('editor-video-file',r.text)
   c.cookies.set('geovyora_admin_locale','pt-BR')
   self.assertIn('Visão geral',c.get('/admin').text)
  write('UPDATE articles SET title=?,body=? WHERE id=?',('Article QA','Editorial body for subsequent tests.',article['id']))

 @patch('main.rate')
 def test_mux_upload_returns_slug_for_inline_editor_and_requires_role(self,rate_mock):
  from unittest.mock import AsyncMock,MagicMock,patch
  from types import SimpleNamespace
  c,t=self.login();client=MagicMock();client.__aenter__.return_value.post=AsyncMock(return_value=SimpleNamespace(status_code=201,json=lambda:{'data':{'id':'qa-mux-upload','url':'https://upload.mux.com/qa'}}))
  with patch.dict(os.environ,{'MUX_TOKEN_ID':'qa-token','MUX_TOKEN_SECRET':'qa-secret'}),patch('main.httpx.AsyncClient',return_value=client):
   r=c.post('/admin/videos/upload',headers={'Accept':'application/json'},data={'csrf_token':t,'title':'Inline video QA','locale':'en'})
   self.assertEqual(r.status_code,200,r.text);result=r.json();record=one('SELECT * FROM videos WHERE id=?',(result['id'],))
   self.assertEqual(record['slug'],result['slug']);self.assertEqual(record['status'],'uploading');self.assertEqual(record['upload_id'],'qa-mux-upload')
   moderator,mt=self.login('moderator');self.assertEqual(moderator.post('/admin/videos/upload',headers={'Accept':'application/json'},data={'csrf_token':mt,'title':'Unauthorized video'}).status_code,403)
   before=client.__aenter__.return_value.post.await_count
   self.assertEqual(c.post('/admin/videos/upload',headers={'Accept':'application/json'},data={'csrf_token':t,'title':'x'}).status_code,422)
   self.assertEqual(client.__aenter__.return_value.post.await_count,before)

class ServiceDiagnostics(fixtures.Fixture):
 @patch('main.rate')
 def test_diagnostics_access_and_safe_failures(self,mock_rate):
  c,t=self.login()
  with patch('service_checks.check_mux',return_value='Aksè Mux verifye.'),patch('service_checks.check_storage',side_effect=RuntimeError('PRIVATE-SECRET')),patch('service_checks.check_firebase',return_value='Otantifikasyon Firebase verifye; livrezon notifikasyon poko teste.'):
   r=c.post('/admin/services/check',data={'csrf_token':t})
   self.assertEqual(r.status_code,200)
   self.assertNotIn('PRIVATE-SECRET',r.text)
   self.assertIn('Tès la echwe.',r.text)
   self.assertIn('Aksè Mux verifye.',r.text)
  self.assertEqual(c.post('/admin/services/check',data={'csrf_token':'wrong'}).status_code,403)
  m,token=self.login('moderator')
  self.assertEqual(m.post('/admin/services/check',data={'csrf_token':token}).status_code,403)
