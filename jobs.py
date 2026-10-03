"""Durable, bounded jobs shared by API and worker. External services are injectable in tests."""
import os,json,uuid,html,logging
from datetime import datetime,timezone,timedelta
import httpx
from db import one,rows,write,connection,sql

now=lambda:datetime.now(timezone.utc).isoformat()
uid=lambda:str(uuid.uuid4())
PRIMARY={'ht':'Kreyòl','fr':'Français','en':'English','pt-BR':'Português','es':'Español'}
RTL={'ar','fa','he','iw','ur','ps','sd','ug','yi','dv','ckb'}

def language_map():
    return {**{r['code']:r['name'] for r in rows('SELECT code,name FROM supported_languages')},**PRIMARY}
def normalize_language(code):
    langs=language_map();code=(code or '').strip()
    if code in langs:return code
    if code.lower().startswith('pt'):return 'pt-BR'
    if code.split('-')[0] in langs:return code.split('-')[0]
    return None

def queue_translation(typ,record,locale):
    fields=['title','subtitle','body'] if typ=='article' else ['bio'] if typ=='influencer' else ['body']
    version=record.get('updated_at',record.get('created_at',''))
    cached=one('SELECT data FROM translations WHERE target_type=? AND target_id=? AND version=? AND locale=?',(typ,record['id'],version,locale))
    if cached:return {'ok':True,'data':json.loads(cached['data'])}
    if not os.getenv('GOOGLE_TRANSLATION_KEY'):return {'ok':False,'message':'Tradiksyon otomatik poko konekte. Ou ka li orijinal la.'}
    payload=record['payload'] if typ=='ui' else {k:record[k] for k in fields};id=uid();stamp=now()
    write('INSERT INTO translation_jobs(id,target_type,target_id,version,locale,payload,next_try,created_at) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING',(id,typ,record['id'],version,locale,json.dumps(payload),stamp,stamp))
    job=one('SELECT * FROM translation_jobs WHERE target_type=? AND target_id=? AND version=? AND locale=?',(typ,record['id'],version,locale))
    return {'ok':False,'queued':job['status'] in ['queued','processing'],'job_id':job['id'],'status':job['status'],'message':job['error'] or 'Tradiksyon an antre nan fil travay la. Orijinal la toujou disponib.'}

def google_translate(payload,locale):
    # Bound request size and query count; only return a complete record for the cache.
    chunks=[]
    for key,text in payload.items():
        remaining=text
        if not remaining:chunks.append((key,''));continue
        while remaining:
            end=min(len(remaining),4000)
            if end<len(remaining):
                boundary=max(remaining.rfind('\n',0,end),remaining.rfind(' ',0,end))
                if boundary>2000:end=boundary+1
            chunks.append((key,remaining[:end]));remaining=remaining[end:]
    batches=[];batch=[];size=0
    for item in chunks:
        if batch and (size+len(item[1])>5000 or len(batch)>=50):batches.append(batch);batch=[];size=0
        batch.append(item);size+=len(item[1])
    if batch:batches.append(batch)
    result={k:'' for k in payload}
    with httpx.Client(timeout=25) as client:
        for batch in batches:
            response=client.post('https://translation.googleapis.com/language/translate/v2',params={'key':os.environ['GOOGLE_TRANSLATION_KEY']},json={'q':[item[1] for item in batch],'target':'pt' if locale=='pt-BR' else locale,'format':'text'})
            if response.status_code in [429,500,502,503,504]:raise TemporaryServiceError('Sèvis tradiksyon an okipe.')
            if response.status_code!=200:raise ValueError('Konfigirasyon oswa lang tradiksyon an pa valab.')
            translated=response.json().get('data',{}).get('translations',[])
            if len(translated)!=len(batch):raise TemporaryServiceError('Repons tradiksyon an pa konplè.')
            for (key,_),item in zip(batch,translated):result[key]+=html.unescape(item['translatedText'])
    return result
class TemporaryServiceError(Exception):pass

def process_translation_jobs(provider=None,batch=3):
    if provider is None and not os.getenv('GOOGLE_TRANSLATION_KEY'):return 0
    provider=provider or google_translate;completed=0
    stale=(datetime.now(timezone.utc)-timedelta(minutes=5)).isoformat()
    # The provider may have billed a crashed request; reservation stays conservative.
    write("UPDATE translation_jobs SET status='queued',error='Travay la ap rekòmanse.',next_try=? WHERE status='processing' AND lease_at<? AND attempts<3",(now(),stale))
    write("UPDATE translation_jobs SET status='error',error='Travay la bezwen revizyon.' WHERE status='processing' AND lease_at<? AND attempts>=3",(stale,))
    for job in rows("SELECT * FROM translation_jobs WHERE status='queued' AND next_try<=? ORDER BY CASE target_type WHEN 'ui' THEN 0 WHEN 'comment' THEN 1 ELSE 2 END,created_at LIMIT ?",(now(),batch)):
        stamp=now()
        if not write("UPDATE translation_jobs SET status='processing',lease_at=?,attempts=attempts+1 WHERE id=? AND status='queued'",(stamp,job['id'])):continue
        payload=json.loads(job['payload']);chars=sum(len(v) for v in payload.values());month=stamp[:7]
        cfg=one("SELECT value FROM settings WHERE key='translation_limit'");limit=int(cfg['value'] if cfg else '100000')
        # If an editor saved a translation while queued, never overwrite it.
        cached=one('SELECT id FROM translations WHERE target_type=? AND target_id=? AND version=? AND locale=?',(job['target_type'],job['target_id'],job['version'],job['locale']))
        if cached:write("UPDATE translation_jobs SET status='done',error='' WHERE id=?",(job['id'],));continue
        with connection() as c:
            c.execute(sql('INSERT INTO usage_months(month,characters) VALUES (?,0) ON CONFLICT(month) DO NOTHING'),(month,))
            reserved=c.execute(sql('UPDATE usage_months SET characters=characters+? WHERE month=? AND characters+?<=?'),(chars,month,chars,limit)).rowcount
        if not reserved:
            write("UPDATE translation_jobs SET status='blocked',error='Limit tradiksyon mwa sa a rive.' WHERE id=?",(job['id'],));continue
        try:
            data=provider(payload,job['locale'])
            write('INSERT INTO translations VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING',(uid(),job['target_type'],job['target_id'],job['version'],job['locale'],json.dumps(data),0,now()))
            write("UPDATE translation_jobs SET status='done',error='' WHERE id=?",(job['id'],));completed+=1
        except (TemporaryServiceError,httpx.TimeoutException,httpx.TransportError):
            status='queued' if job['attempts']<2 else 'error';next_try=(datetime.now(timezone.utc)+timedelta(seconds=30*(2**job['attempts']))).isoformat()
            write('UPDATE translation_jobs SET status=?,next_try=?,error=? WHERE id=?',(status,next_try,'Sèvis tradiksyon an pa disponib; orijinal la toujou disponib.',job['id']))
        except Exception:
            write("UPDATE translation_jobs SET status='error',error='Verifye sèvis tradiksyon an oswa lang lan.' WHERE id=?",(job['id'],))
            logging.warning('Translation job failed: %s',job['id'])
    return completed

def eligible(campaign,subscription):
    if campaign.get('audience_hash') and campaign['audience_hash']!=subscription['visitor_hash']:return False
    if subscription['locale']!=campaign['locale']:return False
    topics=set(filter(None,subscription['topics'].split(',')))
    if campaign.get('topic') and campaign['topic'] not in topics:return False
    if campaign.get('influencer_id') and 'influencer:'+campaign['influencer_id'] not in topics:return False
    return True

def enqueue_campaign(id):
    campaign=one('SELECT * FROM campaigns WHERE id=?',(id,))
    if not campaign or campaign['status'] not in ['draft','scheduled']:return False
    stamp=now()
    with connection() as c:
        if not c.execute(sql("UPDATE campaigns SET status='queued' WHERE id=? AND status IN ('draft','scheduled')"),(id,)).rowcount:return False
        for sub in c.execute('SELECT * FROM push_subscriptions').fetchall():
            sub=dict(sub)
            if eligible(campaign,sub):c.execute(sql("INSERT INTO deliveries(campaign_id,visitor_hash,status,created_at,updated_at) VALUES (?,?,'queued',?,?) ON CONFLICT(campaign_id,visitor_hash) DO NOTHING"),(id,sub['visitor_hash'],stamp,stamp))
    return True

def firebase_send(campaign,subscription):
    import firebase_admin
    from firebase_admin import credentials,messaging
    if not firebase_admin._apps:firebase_admin.initialize_app(credentials.Certificate(json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])))
    site=os.getenv('SITE_URL','').rstrip('/')
    try:
        messaging.send(messaging.Message(notification=messaging.Notification(title=campaign['title'],body=campaign['body']),token=subscription['token'],webpush=messaging.WebpushConfig(fcm_options=messaging.WebpushFCMOptions(link=site+campaign['url']))))
    except messaging.UnregisteredError:raise InvalidSubscription()
class InvalidSubscription(Exception):pass

def process_push_jobs(sender=None,batch=100):
    if sender is None and not os.getenv('FIREBASE_SERVICE_ACCOUNT'):return 0
    sender=sender or firebase_send;completed=0;stamp=now();stale=(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat()
    # A crash can occur after delivery. Never resend uncertain messages automatically.
    write("UPDATE deliveries SET status='uncertain',error='Livrezon ensèten apre entèripsyon.' WHERE status='sending' AND updated_at<?",(stale,))
    for campaign in rows("SELECT id FROM campaigns WHERE status='scheduled' AND scheduled_at<=?",(stamp,)):enqueue_campaign(campaign['id'])
    for item in rows("SELECT * FROM deliveries WHERE status='queued' AND next_try<=? ORDER BY created_at LIMIT ?",(now(),batch)):
        campaign=one('SELECT * FROM campaigns WHERE id=?',(item['campaign_id'],));sub=one('SELECT * FROM push_subscriptions WHERE visitor_hash=?',(item['visitor_hash'],))
        if not sub or not campaign or not eligible(campaign,sub):
            write("UPDATE deliveries SET status='cancelled',updated_at=? WHERE campaign_id=? AND visitor_hash=? AND status='queued'",(now(),item['campaign_id'],item['visitor_hash']));continue
        cap=one("SELECT value FROM settings WHERE key='push_daily_limit'");limit=int(cap['value'] if cap else '3');since=(datetime.now(timezone.utc)-timedelta(hours=24)).isoformat()
        # Serialize the frequency check and claim for this visitor across workers.
        with connection() as c:
            c.execute(sql('UPDATE push_subscriptions SET topics=topics WHERE visitor_hash=?'),(sub['visitor_hash'],))
            count=c.execute(sql("SELECT count(*) n FROM deliveries WHERE visitor_hash=? AND status IN ('sent','sending','uncertain') AND updated_at>?"),(sub['visitor_hash'],since)).fetchone()['n']
            if count>=limit:
                oldest=c.execute(sql("SELECT min(updated_at) stamp FROM deliveries WHERE visitor_hash=? AND status IN ('sent','sending','uncertain') AND updated_at>?"),(sub['visitor_hash'],since)).fetchone()['stamp']
                try:retry=(datetime.fromisoformat(oldest)+timedelta(hours=24,seconds=1)).isoformat()
                except Exception:retry=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
                c.execute(sql("UPDATE deliveries SET next_try=? WHERE campaign_id=? AND visitor_hash=? AND status='queued'"),(retry,campaign['id'],sub['visitor_hash']))
                continue
            claimed=c.execute(sql("UPDATE deliveries SET status='sending',attempts=attempts+1,updated_at=? WHERE campaign_id=? AND visitor_hash=? AND status='queued'"),(now(),campaign['id'],sub['visitor_hash'])).rowcount
        if not claimed:continue
        status='sent';error=''
        try:sender(campaign,sub);completed+=1
        except InvalidSubscription:status='invalid';write('DELETE FROM push_subscriptions WHERE visitor_hash=?',(sub['visitor_hash'],))
        except Exception:status='uncertain';error='Livrezon pa konfime. Pa gen retry otomatik.';logging.warning('Push delivery unconfirmed for campaign %s',campaign['id'])
        write('UPDATE deliveries SET status=?,error=?,updated_at=? WHERE campaign_id=? AND visitor_hash=?',(status,error,now(),campaign['id'],sub['visitor_hash']))
    for c in rows("SELECT id FROM campaigns WHERE status='queued'"):
        pending=one("SELECT count(*) n FROM deliveries WHERE campaign_id=? AND status IN ('queued','sending')",(c['id'],))['n']
        if not pending:
            problems=one("SELECT count(*) n FROM deliveries WHERE campaign_id=? AND status='uncertain'",(c['id'],))['n']
            write('UPDATE campaigns SET status=? WHERE id=?',('needs_review' if problems else 'sent',c['id']))
    return completed
