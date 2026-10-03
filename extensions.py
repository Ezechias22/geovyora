import io,os,json,secrets,uuid,re,hashlib,warnings,unicodedata
from datetime import datetime,timezone,timedelta
from fastapi import Request,Form,HTTPException
from fastapi.responses import RedirectResponse,JSONResponse
from db import rows,one,write,connection,sql
from security import require,csrf,visitor,digest,hash_password,verify_password
from jobs import language_map,normalize_language,queue_translation,enqueue_campaign
now=lambda:datetime.now(timezone.utc).isoformat()
uid=lambda:str(uuid.uuid4())

def initialize_features():
    import main as core
    if not one("SELECT key FROM settings WHERE key='editorial_v2_initialized'"):
        for i,name in enumerate(core.CATEGORIES):write('INSERT INTO categories(id,name,slug,sort_order) VALUES (?,?,?,?) ON CONFLICT(name) DO NOTHING',(uid(),name,core.slugify(name),i))
        for a in rows('SELECT tags FROM articles'):
            for tag in a['tags'].split(','):
                tag=tag.strip()
                if tag:write('INSERT INTO tags VALUES (?,?,?) ON CONFLICT(name) DO NOTHING',(uid(),tag,core.slugify(tag)))
        for k,v in {'brand':'Geovyora','tagline':'Kilti. Kreyativite. Enpak.','default_locale':'ht','translation_limit':'100000','ads_enabled':'0','publisher_id':'','ad_slot':'','contact_email':'','push_daily_limit':'3','editorial_v2_initialized':'1','contact_company':'','contact_address':'','homepage_sections':'latest,creators,notifications'}.items():write('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO NOTHING',(k,v))

def categories():return [r['name'] for r in rows('SELECT name FROM categories WHERE active=1 ORDER BY sort_order,name')]
def normalize_search(value):return ''.join(c for c in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(c))
def search_matches(record,query,fields):return all(part in normalize_search(' '.join(str(record.get(k,'') or '') for k in fields)) for part in normalize_search(query).split())

def s3_client():
    if not all(os.getenv(k) for k in ['S3_BUCKET','S3_ACCESS_KEY_ID','S3_SECRET_ACCESS_KEY','MEDIA_PUBLIC_URL']):raise HTTPException(503,'Storage foto poko konekte.')
    import boto3
    from botocore.config import Config
    return boto3.client('s3',endpoint_url=os.getenv('S3_ENDPOINT_URL') or None,region_name=os.getenv('S3_REGION','us-east-1'),aws_access_key_id=os.environ['S3_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['S3_SECRET_ACCESS_KEY'],config=Config(signature_version='s3v4',request_checksum_calculation='when_required'))

def validate_image(raw,mime):
    from PIL import Image,UnidentifiedImageError
    if len(raw)>10*1024*1024:raise ValueError('Foto a depase 10 MB.')
    formats={'image/jpeg':'JPEG','image/png':'PNG','image/webp':'WEBP'}
    with warnings.catch_warnings():
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        try:
            with Image.open(io.BytesIO(raw)) as image:
                if image.format!=formats.get(mime):raise ValueError('Fòma foto a pa koresponn ak kalite fichye a.')
                width,height=image.size
                if width*height>25000000 or min(width,height)<16:raise ValueError('Dimansyon foto a pa valab.')
                if getattr(image,'n_frames',1)>1:raise ValueError('Chwazi yon foto ki pa anime.')
                image.verify()
        except (UnidentifiedImageError,OSError,Image.DecompressionBombError,Image.DecompressionBombWarning):raise ValueError('Foto a pa valab oswa li domaje.')
    return width,height

def validate_attachment(raw,filename,mime):
    if not raw:raise ValueError('Chwazi yon fichye.')
    if len(raw)>10*1024*1024:raise ValueError('Fichye a depase 10 MB.')
    extension=__import__('pathlib').Path(filename).suffix.lower()
    images={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'}
    if extension in images:
        expected=images[extension]
        if mime not in [expected,'application/octet-stream',None]:raise ValueError('Fòma fichye sa a pa aksepte.')
        validate_image(raw,expected)
        return expected,'.jpg' if extension=='.jpeg' else extension
    if extension=='.pdf' and raw.startswith(b'%PDF-') and b'%%EOF' in raw[-4096:]:
        return 'application/pdf','.pdf'
    if extension=='.txt':
        try:text=raw.decode('utf-8')
        except UnicodeDecodeError:raise ValueError('Fòma fichye sa a pa aksepte.')
        if any(ord(c)<32 and c not in '\n\r\t' for c in text):raise ValueError('Fòma fichye sa a pa aksepte.')
        return 'text/plain; charset=utf-8','.txt'
    raise ValueError('Fòma fichye sa a pa aksepte.')

def verify_media(record,client=None):
    client=client or s3_client();stream=None
    try:
        response=client.get_object(Bucket=os.environ['S3_BUCKET'],Key=record['object_key'])
        stream=response['Body']
        if response['ContentLength']>10*1024*1024:raise ValueError('Foto a depase limit la.')
        raw=stream.read(10*1024*1024+1);width,height=validate_image(raw,record['content_type'])
        write("UPDATE media_assets SET status='ready',size_bytes=?,width=?,height=?,error='' WHERE id=?",(len(raw),width,height,record['id']))
        return {'ok':True,'url':record['url'],'width':width,'height':height}
    except ValueError as e:
        write("UPDATE media_assets SET status='rejected',error=? WHERE id=?",(str(e),record['id']))
        try:client.delete_object(Bucket=os.environ['S3_BUCKET'],Key=record['object_key'])
        except Exception:pass
        raise HTTPException(422,str(e))
    except HTTPException:raise
    except Exception:raise HTTPException(503,'Foto a poko disponib nan storage. Eseye verifye li ankò.')
    finally:
        if stream:stream.close()

def install(app):
    import main as core
    @app.post('/admin/taxonomy/save')
    async def taxonomy_save(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.EDITOR)
        table=f.get('table');id=f.get('id') or uid()
        if table not in ['categories','tags']:raise HTTPException(422,'Kalite pa valab.')
        name=core.clean(f.get('name'),80,2);slug=core.slugify(f.get('slug') or name)
        old=one('SELECT * FROM '+table+' WHERE id=?',(id,))
        if one('SELECT id FROM '+table+' WHERE (name=? OR slug=?) AND id<>?',(name,slug,id)):raise HTTPException(409,'Non oswa slug sa a deja egziste.')
        if table=='categories':
            try:order=int(f.get('sort_order','0'))
            except ValueError:raise HTTPException(422,'Lòd pa valab.')
            active=int(f.get('active')=='on')
            if old:
                with connection() as c:
                    c.execute(sql('UPDATE categories SET name=?,slug=?,sort_order=?,active=? WHERE id=?'),(name,slug,order,active,id))
                    c.execute(sql('UPDATE articles SET category=? WHERE category=?'),(name,old['name']))
                    c.execute(sql('UPDATE influencers SET category=? WHERE category=?'),(name,old['name']))
            else:write('INSERT INTO categories VALUES (?,?,?,?,?)',(id,name,slug,order,active))
        else:
            if old:write('UPDATE tags SET name=?,slug=? WHERE id=?',(name,slug,id))
            else:write('INSERT INTO tags VALUES (?,?,?)',(id,name,slug))
        core.audit(u,table+'.save',id);return RedirectResponse('/admin/'+table+'?saved=1',303)

    @app.post('/admin/seo/save')
    async def seo_save(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.EDITOR)
        typ=f.get('target_type');id=f.get('target_id');locale=f.get('locale','ht')
        if typ not in ['article','influencer'] or locale not in language_map():raise HTTPException(422,'Kontni oswa lang pa valab.')
        if not one('SELECT id FROM '+('articles' if typ=='article' else 'influencers')+' WHERE id=?',(id,)):raise HTTPException(404,'Kontni pa jwenn.')
        title=core.clean(f.get('title'),120);description=core.clean(f.get('description'),300);noindex=int(f.get('noindex')=='on')
        write('INSERT INTO seo_metadata VALUES (?,?,?,?,?,?) ON CONFLICT(target_type,target_id,locale) DO UPDATE SET title=excluded.title,description=excluded.description,noindex=excluded.noindex',(typ,id,locale,title,description,noindex))
        core.audit(u,'seo.save',id,locale);return RedirectResponse('/admin/seo?saved=1',303)

    @app.post('/admin/team/manage')
    async def staff_manage(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,['super_admin'])
        id=f.get('id');staff=one('SELECT * FROM staff WHERE id=?',(id,));action=f.get('action')
        if not staff:raise HTTPException(404,'Manm pa jwenn.')
        if action not in ['disable','activate','role','reset']:raise HTTPException(422,'Aksyon pa valab.')
        if staff['role']=='super_admin' and action in ['disable','role']:raise HTTPException(403,'Pwoteksyon Super Admin: sèvi ak console prive pou aksyon sa a.')
        if id==u['id'] and action=='disable':raise HTTPException(403,'Ou pa ka dezaktive pwòp kont ou.')
        if action in ['disable','activate']:write('UPDATE staff SET active=? WHERE id=?',(int(action=='activate'),id))
        elif action=='role':
            role=f.get('role')
            if role not in ['admin','editor','moderator']:raise HTTPException(422,'Wòl pa valab.')
            write('UPDATE staff SET role=? WHERE id=?',(role,id))
        else:write('UPDATE staff SET password_hash=? WHERE id=?',(hash_password(core.clean(f.get('password'),200,12)),id))
        write('DELETE FROM sessions WHERE staff_id=?',(id,));core.audit(u,'staff.'+action,id);return RedirectResponse('/admin/team?saved=1',303)

    @app.post('/admin/account/password')
    async def change_password(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'))
        if not verify_password(f.get('current_password',''),u['password_hash']):raise HTTPException(403,'Modpas aktyèl la pa kòrèk.')
        password=core.clean(f.get('password'),200,12)
        if password!=f.get('confirm_password'):raise HTTPException(422,'Modpas yo pa menm.')
        write('UPDATE staff SET password_hash=? WHERE id=?',(hash_password(password),u['id']));write('DELETE FROM sessions WHERE staff_id=?',(u['id'],));core.audit(u,'staff.password_change',u['id'])
        res=RedirectResponse('/admin/login',303);res.delete_cookie('vyora_staff');return res

    @app.post('/admin/metrics/save')
    async def save_metrics(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.EDITOR);id=f.get('influencer_id')
        if not one('SELECT id FROM influencers WHERE id=?',(id,)):raise HTTPException(404,'Pwofil pa jwenn.')
        source=core.safe_url(f.get('source_url'))
        try:followers=int(f.get('followers'));observed=datetime.fromisoformat(f.get('observed_at')).replace(tzinfo=timezone.utc)
        except (ValueError,TypeError):raise HTTPException(422,'Chif oswa dat la pa valab.')
        if followers<0 or followers>10000000000 or not source.startswith('https://') or observed>datetime.now(timezone.utc):raise HTTPException(422,'Sous, dat oswa kantite pa valab.')
        write('INSERT INTO influencer_metrics VALUES (?,?,?,?,?,?,?)',(uid(),id,core.clean(f.get('platform'),60,2),followers,source,observed.isoformat(),now()));core.audit(u,'metric.save',id);return RedirectResponse('/admin/influencers?edit='+id,303)

    @app.post('/admin/visitors/ban')
    async def ban(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.MOD);comment=one('SELECT visitor_hash FROM comments WHERE id=?',(f.get('comment_id'),))
        if not comment:raise HTTPException(404,'Kòmantè pa jwenn.')
        try:hours=max(1,min(168,int(f.get('hours','24'))))
        except ValueError:raise HTTPException(422,'Dire entèdiksyon pa valab.')
        reason=core.clean(f.get('reason'),500,3);expiry=(datetime.now(timezone.utc)+timedelta(hours=hours)).isoformat()
        write('INSERT INTO visitor_bans VALUES (?,?,?,?) ON CONFLICT(visitor_hash) DO UPDATE SET expires_at=excluded.expires_at,reason=excluded.reason,staff_id=excluded.staff_id',(comment['visitor_hash'],expiry,reason,u['id']));core.audit(u,'visitor.ban',f.get('comment_id'),reason);return RedirectResponse('/admin/comments?saved=1',303)

    @app.post('/admin/visitors/unban')
    async def unban(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.MOD)
        c=one('SELECT visitor_hash FROM comments WHERE id=?',(f.get('comment_id'),))
        if c:write('DELETE FROM visitor_bans WHERE visitor_hash=?',(c['visitor_hash'],))
        core.audit(u,'visitor.unban',f.get('comment_id'));return RedirectResponse('/admin/comments?saved=1',303)

    @app.post('/admin/media/verify')
    async def media_verify(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.EDITOR);record=one('SELECT * FROM media_assets WHERE id=?',(f.get('id'),))
        if not record:raise HTTPException(404,'Foto pa jwenn.')
        if u['role']=='editor' and record['staff_id']!=u['id']:raise HTTPException(403,'Foto sa a pou yon lòt editè.')
        result=verify_media(record);core.audit(u,'media.verified',record['id']);return result

    @app.get('/api/languages')
    def languages():return {'languages':[{'code':k,'name':v} for k,v in language_map().items()],'additional_available':bool(os.getenv('GOOGLE_TRANSLATION_KEY'))}

    @app.post('/admin/languages/refresh')
    async def refresh_languages(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.ADMIN)
        if not os.getenv('GOOGLE_TRANSLATION_KEY'):raise HTTPException(503,'Konekte Google Translation anvan ou mete lis lang yo ajou.')
        async with __import__('httpx').AsyncClient(timeout=20) as client:
            result=await client.get('https://translation.googleapis.com/language/translate/v2/languages',params={'key':os.environ['GOOGLE_TRANSLATION_KEY'],'target':'en'})
        if result.status_code!=200:raise HTTPException(502,'Lis lang yo pa disponib.')
        from jobs import RTL
        with connection() as c:
            for item in result.json().get('data',{}).get('languages',[]):
                code=item['language']
                if not re.fullmatch('[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})?',code):continue
                c.execute(sql('INSERT INTO supported_languages VALUES (?,?,?,?) ON CONFLICT(code) DO UPDATE SET name=excluded.name,rtl=excluded.rtl,updated_at=excluded.updated_at'),(code,item.get('name',code),int(code in RTL),now()))
        core.audit(u,'languages.refresh','site');return RedirectResponse('/admin/translations?saved=1',303)

    @app.get('/api/translation-jobs/{id}')
    def job_status(request:Request,id:str):
        job=one('SELECT * FROM translation_jobs WHERE id=?',(id,))
        if not job:raise HTTPException(404,'Travay pa jwenn.')
        core.target_ok(job['target_type'],job['target_id'])
        cached=one('SELECT data FROM translations WHERE target_type=? AND target_id=? AND version=? AND locale=?',(job['target_type'],job['target_id'],job['version'],job['locale']))
        return {'status':job['status'],'message':job['error'],'ok':bool(cached),'data':json.loads(cached['data']) if cached else None}

    @app.post('/admin/translation-jobs/retry')
    async def retry_translation(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.EDITOR)
        write("UPDATE translation_jobs SET status='queued',attempts=0,error='',next_try=? WHERE id=? AND status IN ('error','blocked')",(now(),f.get('id')));core.audit(u,'translation.retry',f.get('id'));return RedirectResponse('/admin/translations',303)

    @app.get('/api/push/preferences')
    def preferences(request:Request):
        record=one('SELECT locale,topics FROM push_subscriptions WHERE visitor_hash=?',(visitor(request),))
        return {'subscribed':bool(record),'preferences':record}

    @app.post('/api/push/follow')
    async def follow_creator(request:Request):
        f=await core.public_form(request);core.rate(request,'follow',15,3600);core.target_ok('influencer',f.get('id'))
        sub=one('SELECT * FROM push_subscriptions WHERE visitor_hash=?',(visitor(request),))
        if not sub:raise HTTPException(409,'Aktive notifikasyon sou navigatè sa a anvan ou swiv nouvèl yon kreyatè.')
        topics=set(filter(None,sub['topics'].split(',')));topic='influencer:'+f['id']
        if f.get('remove'):topics.discard(topic)
        else:topics.add(topic)
        write('UPDATE push_subscriptions SET topics=? WHERE visitor_hash=?',(','.join(sorted(topics)),visitor(request)));return {'ok':True,'message':'Preferans kreyatè a sove sou navigatè sa a.'}

    @app.post('/api/newsletter/subscribe')
    async def newsletter(request:Request):
        f=await core.public_form(request);core.rate(request,'newsletter',5,3600);email=core.clean(f.get('email'),250,5).lower();locale=f.get('locale','ht')
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or locale not in language_map() or f.get('consent') not in [True,'on']:raise HTTPException(422,'Bay yon imel valab ak konsantman pou newsletter la.')
        token=secrets.token_urlsafe(32);exists=one('SELECT id,status FROM newsletter_subscribers WHERE email=?',(email,))
        if exists and exists['status']=='active':return {'ok':True,'message':'Demann lan resevwa. Si imel sa a deja abòne, abònman an rete aktif.'}
        write('INSERT INTO newsletter_subscribers VALUES (?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET locale=excluded.locale,token_hash=excluded.token_hash,status=excluded.status',(uid(),email,locale,digest(token),'active',now()))
        return {'ok':True,'message':'Ou abòne. Sove lyen prive dezabònman sa a.','unsubscribe_url':'/'+locale+'/newsletter-unsubscribe?token='+token}

    @app.post('/api/newsletter/unsubscribe')
    async def newsletter_remove(request:Request):
        f=await core.public_form(request);core.rate(request,'newsletter-remove',10,3600);token=core.clean(f.get('token'),100,20)
        write("UPDATE newsletter_subscribers SET status='unsubscribed' WHERE token_hash=?",(digest(token),));return {'ok':True,'message':'Dezabònman an anrejistre.'}

    @app.post('/api/submissions/upload')
    async def public_upload(request:Request):
        core.same_origin(request);core.rate(request,'submission-upload',12,3600)
        f=await request.form()
        if not __import__('hmac').compare_digest(str(f.get('csrf_token','')),request.state.public_csrf):raise HTTPException(403,'Rechaje paj la.')
        if not os.getenv('PRIVATE_SUBMISSION_BUCKET'):raise HTTPException(503,'Pyès jointes prive poko konekte.')
        upload=f.get('file')
        if not hasattr(upload,'read'):raise HTTPException(422,'Chwazi yon fichye.')
        try:raw=await upload.read(10*1024*1024+1)
        finally:await upload.close()
        try:mime,extension=validate_attachment(raw,upload.filename or '',upload.content_type)
        except ValueError as error:raise HTTPException(422,str(error))
        id=uid();key='submissions/'+id+extension
        try:s3_client().put_object(Bucket=os.environ['PRIVATE_SUBMISSION_BUCKET'],Key=key,Body=raw,ContentType=mime,ContentDisposition='attachment; filename="'+id+extension+'"')
        except HTTPException:raise
        except Exception:raise HTTPException(503,'Chajman fichye a echwe. Eseye ankò.')
        write('INSERT INTO submission_assets VALUES (?,?,?,?,?,?,?)',(id,None,visitor(request),key,mime,len(raw),now()))
        return {'ok':True,'id':id,'message':'Fichye chaje an prive.'}

    @app.get('/admin/submission-assets/{id}')
    def private_asset(request:Request,id:str):
        require(request,core.EDITOR+core.MOD);record=one('SELECT * FROM submission_assets WHERE id=? AND submission_id IS NOT NULL',(id,))
        if not record:raise HTTPException(404,'Pyès joint pa jwenn.')
        if not os.getenv('PRIVATE_SUBMISSION_BUCKET'):raise HTTPException(503,'Storage prive pa konfigire.')
        url=s3_client().generate_presigned_url('get_object',Params={'Bucket':os.environ['PRIVATE_SUBMISSION_BUCKET'],'Key':record['object_key']},ExpiresIn=120)
        return RedirectResponse(url,303)

    @app.post('/admin/ads/banner')
    async def banner_save(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.ADMIN)
        image=core.safe_url(f.get('image_url'));link=core.safe_url(f.get('target_url'));locale=f.get('locale','')
        if not image or not link.startswith('https://') or locale and locale not in language_map():raise HTTPException(422,'Lyen oswa lang pa valab.')
        id=uid();write('INSERT INTO ad_placements VALUES (?,?,?,?,?,?,?)',(id,core.clean(f.get('name'),100,3),image,link,locale,int(f.get('active')=='on'),now()));core.audit(u,'banner.save',id);return RedirectResponse('/admin/ads',303)

    @app.post('/admin/ads/toggle')
    async def banner_toggle(request:Request):
        f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,core.ADMIN)
        write('UPDATE ad_placements SET active=1-active WHERE id=?',(f.get('id'),));core.audit(u,'banner.toggle',f.get('id'));return RedirectResponse('/admin/ads',303)
