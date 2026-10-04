import os,json,uuid,secrets,time,hmac,hashlib,html,re,logging
from datetime import datetime,timezone,timedelta
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlencode
import httpx
from fastapi import FastAPI,Request,Form,HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse,JSONResponse,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import migrate,rows,one,write,connection,sql
from security import hash_password,verify_password,digest,session,require,csrf,same_origin,rate,visitor
from i18n import LANGUAGES,labels
from seed import seed
from jobs import language_map,normalize_language,queue_translation,enqueue_campaign
from extensions import initialize_features,categories,normalize_search,search_matches
ROOT=Path(__file__).parent
EDITOR=['super_admin','admin','editor']
MOD=['super_admin','admin','moderator']
ADMIN=['super_admin','admin']
CATEGORIES=['Kilti','Lifestyle','Mizik','Komedi','Mòd','Bote','Biznis','Teknoloji','Gaming','Espò','Kwizin','Edikasyon','Vwayaj','Dekouvèt']
REASONS=['spam','harassment','hate','threat','privacy','impersonation','misinformation','copyright','other']
now=lambda: datetime.now(timezone.utc).isoformat()
uid=lambda: str(uuid.uuid4())
@asynccontextmanager
async def lifespan(app):
    migrate()
    if os.getenv('SEED_DEMO','0')=='1': seed()
    initialize_features()
    yield
app=FastAPI(title='Geovyora Media',lifespan=lifespan,docs_url=None,redoc_url=None)
from request_limits import RequestSizeLimit
app.add_middleware(RequestSizeLimit)
app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
templates=Jinja2Templates(directory=ROOT/'templates')

def settings(): return {r['key']:r['value'] for r in rows('SELECT * FROM settings')}
def audit(u,action,target,reason=''): write('INSERT INTO audit_logs VALUES (?,?,?,?,?,?)',(uid(),u['id'],action,target,reason,now()))
def slugify(value):
    import unicodedata
    text=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','-',text).strip('-')[:120] or secrets.token_hex(6)
def safe_url(value):
    value=(value or '').strip()
    return value if value.startswith(('https://','/static/')) and not value.startswith('//') else ''
def clean(value,limit,minimum=0):
    value=str(value or '').strip()
    if len(value)>limit or len(value)<minimum: raise HTTPException(422,'Longè chan an pa valab.')
    return value

def translate_record(record,locale,typ='article'):
    original=record.get('locale','ht')
    record=dict(record)
    record['original_locale']=original;record['translated']=False;record['fallback']=False
    if locale==original:return record
    version=record.get('updated_at',record.get('created_at',''))
    cache=one('SELECT * FROM translations WHERE target_type=? AND target_id=? AND version=? AND locale=?',(typ,record['id'],version,locale))
    if cache:
        record.update(json.loads(cache['data']));record['translated']=True;record['machine_translation']=not bool(cache['manual'])
    else:record['fallback']=True
    return record

def public_demo_clause(alias=''):
    return '' if os.getenv('ALLOW_DEMO_CONTENT','0')=='1' else ' AND '+alias+'demo=0'

def article_list(where='1=1',args=(),limit=60):
    return rows("SELECT * FROM articles WHERE status='published' AND "+where+public_demo_clause()+' ORDER BY featured DESC,publish_at DESC LIMIT ?',(*args,limit))
def render(request,page,locale='ht',**kw):
    cfg=settings()
    if page=='admin':
        chosen=request.query_params.get('lang') or request.cookies.get('geovyora_admin_locale') or request.headers.get('accept-language','').split(',')[0].split(';')[0]
        locale=normalize_language(chosen) or cfg.get('default_locale','ht')
        if locale not in LANGUAGES:locale='en'
    t=labels(locale);ui={} 
    if page!='admin':
        from localization import ui_translation,queue_ui
        ui=ui_translation(locale) if locale!='ht' else {}
        t.update({k[6:]:v for k,v in ui.items() if k.startswith('label:')})
        if locale!='ht':queue_ui(locale)
    base={'request':request,'locale':locale,'t':t,'languages':language_map(),'settings':cfg,'brand':cfg.get('brand','Geovyora'),'page':page,'categories':categories(),'staff':session(request),'csrf_token':request.state.public_csrf,'title':cfg.get('brand','Geovyora'),'description':'Magazin sou kreyatè Ayisyen, dyaspora ak mond lan.','path':request.url.path,'ads_allowed':False}
    base.update(kw)
    if page=='admin':
        from admin_localization import COPY,admin_text
        base['admin_languages']=LANGUAGES
        base['admin_text']=admin_text
        base['admin_copy']={text:admin_text(text,locale) for text in COPY}
        base['admin_greeting']={'ht':'Bonjou','fr':'Bonjour','en':'Hello','pt-BR':'Olá','es':'Hola'}.get(locale,'Hello')
        base['media_library']=rows("SELECT url,content_type FROM media_assets WHERE status='ready' ORDER BY created_at DESC LIMIT 40")
        base['video_library']=rows("SELECT slug,title FROM videos WHERE status='ready' ORDER BY created_at DESC LIMIT 100")

    base['direction']='rtl' if locale.split('-')[0] in __import__('jobs').RTL else 'ltr'
    base['language_ui_fallback']=locale not in language_map()
    base['banners']=rows("SELECT * FROM ad_placements WHERE active=1 AND (locale='' OR locale=?)",(locale,)) if page!='admin' else []
    base['seo_noindex']=False
    base['submission_upload_configured']=bool(os.getenv('PRIVATE_SUBMISSION_BUCKET') and os.getenv('S3_ACCESS_KEY_ID') and os.getenv('S3_SECRET_ACCESS_KEY'))
    base['max_video_bytes']=int(os.getenv('MAX_VIDEO_BYTES','1073741824'))
    record=base.get('article') or base.get('profile')
    if record and record.get('demo') or base.get('articles') and all(a.get('demo') for a in base['articles']):base['banners']=[]
    if record and page in ['article','influencer']:
        metadata=one('SELECT * FROM seo_metadata WHERE target_type=? AND target_id=? AND locale=?',(page,record['id'],locale))
        if metadata:
            if metadata['title']:base['title']=metadata['title']
            if metadata['description']:base['description']=metadata['description']
            base['seo_noindex']=bool(metadata['noindex'])
    origin=os.getenv('SITE_URL','http://localhost:8000').rstrip('/')
    base['canonical']=origin+request.url.path
    base['share_image']=origin+'/static/geovyora-share.png'
    base['copyright_year']=now()[:4]
    base['alternates']=[]
    if page=='article' and base.get('article'):
        a=base['article']
        base['canonical']=origin+'/'+(locale if a.get('translated') else a.get('original_locale',locale))+'/article/'+a['slug']
        version=a.get('updated_at','')
        langs=[a.get('original_locale',locale)]+[x['locale'] for x in rows("SELECT locale FROM translations WHERE target_type='article' AND target_id=? AND version=?",(a['id'],version))]
        base['alternates']=[{'locale':l,'url':origin+'/'+l+'/article/'+a['slug']} for l in set(langs)]
    base['body_blocks']=[]
    if page=='article' and base.get('article'):
        from content import body_blocks
        base['body_blocks']=body_blocks(base['article']['body'])
    base['structured_data']=None
    if page=='article' and base.get('article') and not base['article']['demo']:
        a=base['article']
        base['structured_data']={'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['subtitle'],'datePublished':a['publish_at'],'dateModified':a['updated_at'],'author':{'@type':'Person','name':a['author']},'publisher':{'@type':'Organization','name':cfg.get('brand','Geovyora'),'logo':{'@type':'ImageObject','url':origin+'/static/geovyora-mark.png'}},'inLanguage':locale if a.get('translated') else a.get('original_locale',locale),'mainEntityOfPage':base['canonical']}
    base['corrections']=[]
    if page=='article' and base.get('article'):
        for revision in rows('SELECT data,created_at FROM revisions WHERE article_id=? ORDER BY created_at DESC LIMIT 30',(base['article']['id'],)):
            note=json.loads(revision['data']).get('correction_note')
            if note:base['corrections'].append({'note':note,'date':revision['created_at'][:10]})
    base['home_sections']=[v for v in cfg.get('homepage_sections','latest,creators,notifications').split(',') if v in ['latest','creators','notifications']]
    if base.get('article') and base['article'].get('sources'):
        base['sources_list']=[{'text':x.strip(),'url':safe_url(x.strip()) if x.strip().startswith('https://') else None} for x in base['article']['sources'].splitlines() if x.strip()]
    if page!='admin' and locale in ['fr','en','pt-BR','es'] and cfg.get('ads_enabled')=='1' and cfg.get('publisher_id') and os.getenv('ADS_CONSENT_READY')=='1':
        displayed=base.get('article')
        base['ads_allowed']=bool(displayed and not displayed['demo'] and displayed.get('translated') and displayed.get('original_locale')!=locale or displayed and not displayed['demo'] and displayed.get('original_locale')==locale)
    response=templates.TemplateResponse(request=request,name=('admin.html' if page=='admin' else 'site.html'),context=base)
    if page=='admin':
        from admin_localization import localize_admin
        response.body=localize_admin(response.body.decode('utf-8'),locale).encode('utf-8')
    else:
        from localization import localize_html
        response.body=localize_html(response.body.decode('utf-8'),locale).encode('utf-8')
    response.headers['content-length']=str(len(response.body))
    blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',response.body.decode('utf-8'),re.S)
    import base64
    request.state.schema_hashes=["'sha256-"+base64.b64encode(hashlib.sha256(block.encode()).digest()).decode()+"'" for block in blocks]
    return response

@app.middleware('http')
async def cookies_and_headers(request,call_next):
    v=request.cookies.get('vyora_visitor')
    if not v or not re.fullmatch('[A-Za-z0-9_-]{32,64}',v): v=secrets.token_urlsafe(32)
    request.state.visitor=v
    request.state.public_csrf=digest('csrf|'+v)
    try: response=await call_next(request)
    except Exception:
        logging.exception('Unhandled application error');return JSONResponse({'detail':'Sèvis la pa disponib. Eseye ankò.'},status_code=503)
    if request.cookies.get('vyora_visitor')!=v:response.set_cookie('vyora_visitor',v,max_age=365*86400,httponly=True,secure=os.getenv('COOKIE_SECURE','0')=='1',samesite='lax')
    response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['X-Frame-Options']='SAMEORIGIN'
    if request.url.path.startswith(('/admin','/api')):response.headers['Cache-Control']='no-store'
    response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' https: data:; style-src 'self' 'unsafe-inline'; script-src 'self' https://www.gstatic.com https://cdn.jsdelivr.net https://pagead2.googlesyndication.com; connect-src 'self' https://*.mux.com https://*.googleapis.com https://*.firebaseio.com https://*.gstatic.com https://*.googlesyndication.com; media-src 'self' blob: https://*.mux.com; frame-src https://*.googlesyndication.com https://googleads.g.doubleclick.net; object-src 'none'; base-uri 'self'; form-action 'self'"
    from urllib.parse import urlsplit
    storage_origins=set()
    for value in [os.getenv('S3_ENDPOINT_URL',''),os.getenv('MEDIA_PUBLIC_URL','')]:
        parsed=urlsplit(value)
        if parsed.scheme=='https' and parsed.netloc and not parsed.username:
            storage_origins.add('https://'+parsed.netloc)
            if value==os.getenv('S3_ENDPOINT_URL') and os.getenv('S3_BUCKET') and re.fullmatch('[a-z0-9.-]+',os.environ['S3_BUCKET']):storage_origins.add('https://'+os.environ['S3_BUCKET']+'.'+parsed.netloc)
    bucket=os.getenv('S3_BUCKET','');region=os.getenv('S3_REGION','us-east-1')
    if re.fullmatch('[a-z0-9.-]+',bucket) and re.fullmatch('[a-z0-9-]+',region):storage_origins.update(['https://'+bucket+'.s3.amazonaws.com','https://'+bucket+'.s3.'+region+'.amazonaws.com'])
    if storage_origins:response.headers['Content-Security-Policy']=response.headers['Content-Security-Policy'].replace("connect-src 'self'","connect-src 'self' "+' '.join(sorted(storage_origins)))
    if getattr(request.state,'schema_hashes',[]):
        response.headers['Content-Security-Policy']=response.headers['Content-Security-Policy'].replace("script-src 'self'","script-src 'self' "+' '.join(request.state.schema_hashes))
    return response

@app.exception_handler(HTTPException)
async def http_error(request,exc):
    if request.url.path.startswith('/api') or request.headers.get('accept')=='application/json':return JSONResponse({'detail':exc.detail},status_code=exc.status_code)
    return HTMLResponse('<!doctype html><html lang="ht"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="/static/style.css"><body><main class="simple"><a class="logo" href="/">Geovyora<span>✦</span></a><h1>'+str(exc.status_code)+'</h1><p>'+html.escape(str(exc.detail))+'</p><a class="btn" href="/">Retounen sou sit la</a></main></body></html>',status_code=exc.status_code)

@app.get('/health')
def health():one('SELECT 1');return {'status':'ok'}
@app.get('/')
def root(request:Request):
    chosen=request.cookies.get('vyora_locale')
    if chosen not in language_map():
        chosen=settings().get('default_locale','ht')
        preferences=[]
        for part in request.headers.get('accept-language','').split(','):
            segments=part.strip().split(';');quality=1.0
            try:
                if len(segments)>1:quality=float(segments[1].strip().removeprefix('q='))
            except ValueError:quality=0
            key=normalize_language(segments[0])
            if key and quality>0:preferences.append((quality,key))
        if preferences:chosen=sorted(preferences,key=lambda x:x[0],reverse=True)[0][1]
    return RedirectResponse('/'+chosen,status_code=302)
@app.get('/robots.txt')
def robots():return Response('User-agent: *\nDisallow: /admin\nDisallow: /api\nDisallow: /*/search\nSitemap: '+os.getenv('SITE_URL','http://localhost:8000')+'/sitemap.xml\n',media_type='text/plain')
@app.get('/sitemap.xml')
def sitemap():
    site=os.getenv('SITE_URL','http://localhost:8000').rstrip('/')
    paths=['/'+l for l in LANGUAGES]
    for a in article_list(limit=5000):
        if a['demo']:continue
        langs={a['locale']}|{r['locale'] for r in rows("SELECT locale FROM translations WHERE target_type='article' AND target_id=? AND version=?",(a['id'],a['updated_at']))}
        for lang in langs:
            meta=one("SELECT noindex FROM seo_metadata WHERE target_type='article' AND target_id=? AND locale=?",(a['id'],lang))
            if not meta or not meta['noindex']:paths.append('/'+lang+'/article/'+a['slug'])
    for p in rows("SELECT * FROM influencers WHERE status='published' AND demo=0"):
        meta=one("SELECT noindex FROM seo_metadata WHERE target_type='influencer' AND target_id=? AND locale='ht'",(p['id'],))
        if not meta or not meta['noindex']:paths.append('/ht/influencer/'+p['slug'])
    return Response('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(site+p)+'</loc></url>' for p in paths)+'</urlset>',media_type='application/xml')
@app.get('/ads.txt')
def ads_txt():
    s=settings();pub=s.get('publisher_id','')
    return Response('google.com, '+pub+', DIRECT, f08c47fec0942fa0\n' if s.get('ads_enabled')=='1' and re.fullmatch('pub-[0-9]+',pub) else '# Advertising is not activated.\n',media_type='text/plain')

@app.get('/admin/login')
def login_page(request:Request):
    if session(request):return RedirectResponse('/admin',302)
    return render(request,'admin',mode='login',setup_needed=not one('SELECT id FROM staff LIMIT 1'),u=None)
@app.post('/admin/login')
def login(request:Request,email:str=Form(...),password:str=Form(...),csrf_token:str=Form(...)):
    same_origin(request);rate(request,'login',8,900)
    if not hmac.compare_digest(csrf_token,request.state.public_csrf):raise HTTPException(403,'Rechaje paj la.')
    u=one('SELECT * FROM staff WHERE email=? AND active=1',(email.lower().strip(),))
    valid=verify_password(password,u['password_hash'] if u else hash_password('dummy-value-for-timing'))
    if not u or not valid:return render(request,'admin',mode='login',setup_needed=False,u=None,error='Imel oswa modpas la pa kòrèk.')
    token=secrets.token_urlsafe(32);write('INSERT INTO sessions VALUES (?,?,?,?)',(digest(token),u['id'],int(time.time())+8*3600,secrets.token_urlsafe(32)))
    res=RedirectResponse('/admin',303);res.set_cookie('vyora_staff',token,httponly=True,secure=os.getenv('COOKIE_SECURE','0')=='1',samesite='lax',max_age=8*3600);return res
@app.post('/admin/logout')
def logout(request:Request,csrf_token:str=Form(...)):
    csrf(request,csrf_token);write('DELETE FROM sessions WHERE token_hash=?',(digest(request.cookies.get('vyora_staff','')),));res=RedirectResponse('/admin/login',303);res.delete_cookie('vyora_staff');return res

@app.get('/admin')
@app.get('/admin/{section}')
def admin(request:Request,section:str='overview',edit:str='',service_checks=None):
    u=session(request)
    if not u:return RedirectResponse('/admin/login',302)
    editable=['articles','influencers','videos','translations','categories','tags','media','seo']
    if section in editable and u['role'] not in EDITOR:raise HTTPException(403,'Aksè editoryal obligatwa.')
    if section in ['team','settings','ads','notifications','newsletter','audit'] and u['role'] not in ADMIN:raise HTTPException(403,'Aksè admin obligatwa.')
    allowed=['overview',*editable,'comments','reports','submissions','analytics','team','settings','ads','notifications','newsletter','audit','account']
    if section not in allowed:raise HTTPException(404,'Paj administrasyon sa a pa egziste.')
    data={};record=None
    if section in ['articles','influencers','videos','comments','reports','submissions','translations','audit']:
        table='audit_logs' if section=='audit' else section
        data=rows('SELECT * FROM '+table+' ORDER BY created_at DESC LIMIT 150')
        if section=='submissions':
            for item in data:item['attachments']=rows('SELECT id,content_type,size_bytes FROM submission_assets WHERE submission_id=?',(item['id'],))
        if edit:record=one('SELECT * FROM '+table+' WHERE id=?',(edit,))
        if section=='influencers' and record:record['socials']=json.loads(record['socials'])
    elif section in ['categories','tags']:
        data=rows('SELECT * FROM '+section+' ORDER BY name')
        if edit:record=one('SELECT * FROM '+section+' WHERE id=?',(edit,))
    elif section=='seo':data=rows('SELECT * FROM seo_metadata ORDER BY target_type,target_id')
    elif section=='newsletter':data=rows('SELECT id,email,locale,status,created_at FROM newsletter_subscribers ORDER BY created_at DESC')
    elif section=='media':data=rows('SELECT * FROM media_assets ORDER BY created_at DESC')
    elif section=='team':data=rows('SELECT id,email,name,role,active FROM staff')
    counts={}
    for table in ['articles','influencers','comments','reports','submissions','videos','push_subscriptions']:
        counts[table]=one('SELECT count(*) as n FROM '+table)['n']
    counts['pending_comments']=one("SELECT count(*) n FROM comments WHERE status='pending'")['n']
    counts['pending_reports']=one("SELECT count(*) n FROM reports WHERE status IN ('pending','in_review')")['n']
    counts['views']=one('SELECT count(*) n FROM page_views')['n']
    service_keys={'Mux':['MUX_TOKEN_ID','MUX_TOKEN_SECRET'],'Google Translation':['GOOGLE_TRANSLATION_KEY'],'Storage':['S3_BUCKET','S3_ENDPOINT_URL','S3_REGION','S3_ACCESS_KEY_ID','S3_SECRET_ACCESS_KEY','MEDIA_PUBLIC_URL','PRIVATE_SUBMISSION_BUCKET'],'Firebase':['FIREBASE_PUBLIC_CONFIG','FIREBASE_SERVICE_ACCOUNT','FIREBASE_VAPID_KEY']}
    service_details={name:{'missing':[key for key in keys if not os.getenv(key)],'optional':name=='Google Translation'} for name,keys in service_keys.items()}
    services={name:not detail['missing'] for name,detail in service_details.items()}
    services['AdSense']=settings().get('ads_enabled')=='1'
    service_details['AdSense']={'missing':[],'optional':True}

    popular=rows("SELECT a.title,count(v.id) views FROM articles a LEFT JOIN page_views v ON a.id=v.article_id GROUP BY a.id,a.title ORDER BY views DESC LIMIT 8")
    return render(request,'admin',u=u,mode=section,data=data,record=record,counts=counts,services=services,service_details=service_details,service_checks=service_checks or {},popular=popular,staff_csrf=u['csrf'],campaigns=rows('SELECT * FROM campaigns ORDER BY created_at DESC'),translation_jobs=rows('SELECT * FROM translation_jobs ORDER BY created_at DESC LIMIT 100'),usage=one('SELECT characters FROM usage_months WHERE month=?',(now()[:7],)) or {'characters':0},banners=rows('SELECT * FROM ad_placements ORDER BY created_at DESC') if section=='ads' else [],metrics=rows('SELECT * FROM influencer_metrics WHERE influencer_id=? ORDER BY observed_at DESC',(edit,)) if section=='influencers' and edit else [],deliveries=rows('SELECT status,count(*) n FROM deliveries GROUP BY status'))

@app.post('/admin/articles/save')
async def save_article(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,EDITOR)
    id=f.get('id') or uid();old=one('SELECT * FROM articles WHERE id=?',(id,))
    if old:
        revision=dict(old);revision['correction_note']=clean(f.get('correction_note'),1000)
        write('INSERT INTO revisions VALUES (?,?,?,?,?)',(uid(),id,json.dumps(revision),u['id'],now()))
    status=f.get('status','draft')
    if status not in ['draft','in_review','scheduled','published','archived']:raise HTTPException(422,'Invalid status')
    if status in ['published','scheduled'] and u['role']=='editor': status='in_review'
    publish_at=f.get('publish_at') or now()
    if status=='scheduled':
        try:
            d=datetime.fromisoformat(publish_at).replace(tzinfo=timezone.utc)
            if d<=datetime.now(timezone.utc):raise ValueError()
            publish_at=d.isoformat()
        except ValueError:raise HTTPException(422,'Mete yon dat UTC nan lavni.')
    slug=slugify(f.get('slug') or f.get('title'))
    clash=one('SELECT id FROM articles WHERE slug=? AND id<>?',(slug,id))
    if clash:raise HTTPException(409,'Slug sa a deja itilize.')
    locale=f.get('locale','ht')
    if locale not in language_map():raise HTTPException(422,'Lang pa valab.')
    values=(slug,clean(f.get('title'),220,3),clean(f.get('subtitle'),500),clean(f.get('body'),100000,10),clean(f.get('category'),80,1),f.get('region','haiti'),f.get('kind','article'),safe_url(f.get('image')),clean(f.get('image_credit'),500),clean(f.get('author'),100,1),locale,status,int(f.get('featured')=='on'),int(f.get('demo')=='on'),int(f.get('sponsored')=='on'),publish_at,now(),clean(f.get('sources'),5000),clean(f.get('tags'),500),f.get('influencer_id') or None)
    fields='slug,title,subtitle,body,category,region,kind,image,image_credit,author,locale,status,featured,demo,sponsored,publish_at,updated_at,sources,tags,influencer_id'
    if old and old['slug']!=slug:write('INSERT INTO redirects VALUES (?,?) ON CONFLICT(old_slug) DO UPDATE SET new_slug=excluded.new_slug',(old['slug'],slug))
    if old:write('UPDATE articles SET '+','.join(x+'=?' for x in fields.split(','))+' WHERE id=?',(*values,id))
    else:write('INSERT INTO articles(id,'+fields+',created_at) VALUES ('+','.join('?' for _ in range(22))+')',(id,*values,now()))
    # Preserve verified translations when only image or publishing metadata changes.
    if old:
        current=one('SELECT * FROM articles WHERE id=?',(id,))
        if all(old[k]==current[k] for k in ['title','subtitle','body','locale']):
            for tr in rows("SELECT * FROM translations WHERE target_type='article' AND target_id=? AND version=? AND manual=1",(id,old['updated_at'])):
                write('INSERT INTO translations(id,target_type,target_id,version,locale,data,manual,created_at) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO NOTHING',(uid(),'article',id,current['updated_at'],tr['locale'],tr['data'],1,now()))
    audit(u,'article.save',id,status);return RedirectResponse('/admin/articles?saved=1',303)

@app.post('/admin/influencers/save')
async def save_influencer(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,EDITOR)
    id=f.get('id') or uid();old=one('SELECT id FROM influencers WHERE id=?',(id,));socials={}
    for platform in ['Instagram','TikTok','YouTube','Facebook','X','Twitch']:
        val=safe_url(f.get(platform))
        if val:socials[platform]=val
    status=f.get('status','draft')
    if status not in ['draft','published','archived']:raise HTTPException(422,'Invalid status')
    if u['role']=='editor':status='draft'
    vals=(slugify(f.get('slug') or f.get('name')),clean(f.get('name'),120,2),clean(f.get('username'),100),clean(f.get('origin'),100),clean(f.get('residence'),100),clean(f.get('category'),100),clean(f.get('bio'),10000,10),safe_url(f.get('image')),json.dumps(socials),f.get('languages','ht'),int(f.get('demo')=='on'),status)
    fields='slug,name,username,origin,residence,category,bio,image,socials,languages,demo,status'
    clash=one('SELECT id FROM influencers WHERE slug=? AND id<>?',(vals[0],id))
    if clash:raise HTTPException(409,'Slug deja itilize.')
    if old:write('UPDATE influencers SET '+','.join(x+'=?' for x in fields.split(','))+' WHERE id=?',(*vals,id))
    else:write('INSERT INTO influencers(id,'+fields+',created_at) VALUES ('+','.join('?' for _ in range(14))+')',(id,*vals,now()))
    audit(u,'influencer.save',id);return RedirectResponse('/admin/influencers?saved=1',303)

@app.post('/admin/moderate')
async def moderate(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,MOD)
    table=f.get('table');status=f.get('status');id=f.get('id')
    allowed={'comments':['approved','rejected','hidden','deleted'],'reports':['pending','in_review','resolved','dismissed'],'submissions':['pending','in_review','accepted','rejected']}
    if table not in allowed or status not in allowed[table]:raise HTTPException(422,'Invalid moderation')
    if not one('SELECT id FROM '+table+' WHERE id=?',(id,)):raise HTTPException(404,'Pa jwenn dosye a.')
    if table=='comments' and status=='deleted':write("UPDATE comments SET status='deleted',body='[Kòmantè retire]',name='Anonyme',subscribe_reply=0 WHERE id=?",(id,))
    else:write('UPDATE '+table+' SET status=? WHERE id=?',(status,id))
    if table=='comments' and status=='approved':
        child=one('SELECT * FROM comments WHERE id=?',(id,))
        parent=one('SELECT * FROM comments WHERE id=?',(child['parent_id'],)) if child['parent_id'] else None
        if parent and parent['status']=='approved' and parent['subscribe_reply'] and parent['visitor_hash']!=child['visitor_hash']:
            sub=one('SELECT * FROM push_subscriptions WHERE visitor_hash=?',(parent['visitor_hash'],))
            if sub:
                typ=child['target_type'];tables={'article':'articles','influencer':'influencers','video':'videos'};record=one('SELECT slug FROM '+tables[typ]+' WHERE id=?',(child['target_id'],))
                link='/'+sub['locale']+'/'+typ+'/'+record['slug']
                cid='reply-'+id
                messages={'ht':('Nouvo repons','Yon moun reponn kòmantè ou a.'),'fr':('Nouvelle réponse','Quelqu’un a répondu à votre commentaire.'),'en':('New reply','Someone replied to your comment.'),'pt-BR':('Nova resposta','Alguém respondeu ao seu comentário.'),'es':('Nueva respuesta','Alguien respondió a tu comentario.')}
                title,message=messages.get(sub['locale'],messages['en'])
                write("INSERT INTO campaigns(id,title,body,url,locale,status,created_at,audience_hash) VALUES (?,?,?,?,?,'draft',?,?) ON CONFLICT(id) DO NOTHING",(cid,'Geovyora · '+title,message,link,sub['locale'],now(),parent['visitor_hash']))
                enqueue_campaign(cid)
    audit(u,table+'.'+status,id,clean(f.get('reason'),1000,3));return RedirectResponse('/admin/'+table,303)

@app.post('/admin/settings/save')
async def save_settings(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,ADMIN)
    for k in ['brand','contact_email','tagline','default_locale','translation_limit','publisher_id','ad_slot','push_daily_limit','contact_company','contact_address','homepage_sections']:
        if k in f:
            value=clean(f[k],500)
            if k=='push_daily_limit' and (not value.isdigit() or not 1<=int(value)<=10):raise HTTPException(422,'Limit push: 1 jiska 10 pa jou.')
            if k=='translation_limit' and (not value.isdigit() or int(value)>10000000):raise HTTPException(422,'Invalid budget')
            if k=='default_locale' and value not in language_map():raise HTTPException(422,'Invalid locale')
            if k=='homepage_sections' and (len(set(value.split(',')))!=len(value.split(',')) or any(x not in ['latest','creators','notifications'] for x in value.split(','))):raise HTTPException(422,'Seksyon dakèy pa valab.')
            if k=='publisher_id' and value and not re.fullmatch('pub-[0-9]+',value):raise HTTPException(422,'Publisher ID invalid')
            write('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(k,value))
    if 'ads_form' in f:write("UPDATE settings SET value=? WHERE key='ads_enabled'",('1' if f.get('ads_enabled')=='on' else '0',))
    audit(u,'settings.save','site');return RedirectResponse('/admin/settings?saved=1',303)

@app.post('/admin/team/save')
async def team_save(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,['super_admin'])
    role=f.get('role','editor')
    if role not in ['admin','editor','moderator']:raise HTTPException(422,'Invalid role')
    password=clean(f.get('password'),200,12);email=clean(f.get('email'),200,5).lower()
    if '@' not in email:raise HTTPException(422,'Invalid email')
    if one('SELECT id FROM staff WHERE email=?',(email,)):raise HTTPException(409,'Imel deja egziste.')
    id=uid();write('INSERT INTO staff(id,email,name,password_hash,role) VALUES (?,?,?,?,?)',(id,email,clean(f.get('name'),120,2),hash_password(password),role));audit(u,'staff.create',id);return RedirectResponse('/admin/team',303)

@app.post('/admin/revisions/restore')
async def restore(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,ADMIN)
    revision=one('SELECT * FROM revisions WHERE id=?',(f.get('id'),))
    if not revision:raise HTTPException(404,'Revision not found')
    record=json.loads(revision['data']);current=one('SELECT * FROM articles WHERE id=?',(revision['article_id'],))
    write('INSERT INTO revisions VALUES (?,?,?,?,?)',(uid(),current['id'],json.dumps(current),u['id'],now()))
    fields=['title','subtitle','body','category','sources','tags','image','image_credit']
    write('UPDATE articles SET '+','.join(k+'=?' for k in fields)+',updated_at=?,status=? WHERE id=?',(*[record[k] for k in fields],now(),'draft',current['id']));audit(u,'revision.restore',revision['id']);return RedirectResponse('/admin/articles?edit='+current['id'],303)

@app.get('/api/revisions/{article_id}')
def revisions(request:Request,article_id:str):require(request,EDITOR);return rows('SELECT id,created_at FROM revisions WHERE article_id=? ORDER BY created_at DESC',(article_id,))

async def public_form(request):
    same_origin(request);f=await request.json()
    if not hmac.compare_digest(f.get('csrf_token',''),request.state.public_csrf):raise HTTPException(403,'Rechaje paj la pou kontinye.')
    if f.get('website'):raise HTTPException(422,'Demann pa valab.')
    ban=one('SELECT expires_at FROM visitor_bans WHERE visitor_hash=?',(visitor(request),))
    if ban and ban['expires_at']>now():raise HTTPException(403,'Patisipasyon navigatè sa a limite tanporèman. Ou kapab kontakte ekip la.')
    return f

def target_ok(typ,id):
    tables={'article':'articles','influencer':'influencers','video':'videos','comment':'comments'}
    if typ not in tables:raise HTTPException(422,'Invalid target')
    status='approved' if typ=='comment' else 'ready' if typ=='video' else 'published'
    if not one('SELECT id FROM '+tables[typ]+' WHERE id=? AND status=?'+(public_demo_clause() if typ in ['article','influencer'] else ''),(id,status)):raise HTTPException(404,'Kontni pa disponib.')

@app.post('/api/comments')
async def comment_create(request:Request):
    f=await public_form(request);rate(request,'comment',8,600);typ=f.get('target_type');id=f.get('target_id');target_ok(typ,id)
    parent=f.get('parent_id') or None
    if parent and not one("SELECT id FROM comments WHERE id=? AND target_type=? AND target_id=? AND status='approved'",(parent,typ,id)):raise HTTPException(422,'Repons sa a pa valab.')
    name=clean(f.get('name'),80,2)
    if re.search(r'\b(admin|moderator|vyora|geovyora|staff|equipe|ekip)\b',name,re.I):raise HTTPException(422,'Chwazi yon pseudo ki pa sanble ak ekip sit la.')
    body=clean(f.get('body'),3000,3)
    idnew=uid();write('INSERT INTO comments(id,target_type,target_id,parent_id,visitor_hash,name,body,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',(idnew,typ,id,parent,visitor(request),name,body,'pending',now(),now()))
    if f.get('subscribe_reply'):
        if one('SELECT visitor_hash FROM push_subscriptions WHERE visitor_hash=?',(visitor(request),)):write('UPDATE comments SET subscribe_reply=1 WHERE id=?',(idnew,))
    return {'ok':True,'message':'Mèsi! Kòmantè ou a ap tann moderasyon.','id':idnew}
@app.get('/api/comments')
def comments(request:Request,target_type:str,target_id:str,page:int=1,sort:str='new'):
    target_ok(target_type,target_id);page=max(1,min(page,1000))
    order='likes DESC,c.created_at DESC' if sort=='liked' else 'c.created_at DESC'
    data=rows("SELECT c.id,c.parent_id,c.name,c.body,c.created_at,count(r.visitor_hash) likes,c.visitor_hash FROM comments c LEFT JOIN reactions r ON r.comment_id=c.id WHERE c.target_type=? AND c.target_id=? AND c.status='approved' GROUP BY c.id ORDER BY "+order+' LIMIT 30 OFFSET ?',(target_type,target_id,(page-1)*30))
    for x in data:x['mine']=x.pop('visitor_hash')==visitor(request);x['liked']=bool(one('SELECT comment_id FROM reactions WHERE comment_id=? AND visitor_hash=?',(x['id'],visitor(request))))
    pending=rows("SELECT id,name,body,status FROM comments WHERE target_type=? AND target_id=? AND visitor_hash=? AND status IN ('pending','rejected')",(target_type,target_id,visitor(request)))
    return {'comments':data,'pending':pending,'page':page,'has_more':len(data)==30}
@app.post('/api/comments/{id}/like')
async def like(request:Request,id:str):
    await public_form(request);rate(request,'like',50,600);target_ok('comment',id)
    with connection() as c:
        c.execute(sql('UPDATE comments SET status=status WHERE id=?'),(id,))
        old=c.execute(sql('SELECT comment_id FROM reactions WHERE comment_id=? AND visitor_hash=?'),(id,visitor(request))).fetchone()
        if old:c.execute(sql('DELETE FROM reactions WHERE comment_id=? AND visitor_hash=?'),(id,visitor(request)))
        else:c.execute(sql('INSERT INTO reactions VALUES (?,?)'),(id,visitor(request)))
    return {'ok':True}
@app.post('/api/comments/{id}/manage')
async def manage_comment(request:Request,id:str):
    f=await public_form(request);rate(request,'manage-comment',15,600)
    c=one('SELECT * FROM comments WHERE id=? AND visitor_hash=?',(id,visitor(request)))
    if not c:raise HTTPException(403,'Se sèlman navigatè ki te ekri kòmantè sa a ki ka jere li.')
    if f.get('action')=='delete':write("UPDATE comments SET status='deleted',body='[Kòmantè retire]',name='Anonyme',subscribe_reply=0 WHERE id=?",(id,))
    else:write("UPDATE comments SET body=?,status='pending',updated_at=? WHERE id=?",(clean(f.get('body'),3000,3),now(),id))
    return {'ok':True,'message':'Chanjman an sove.'}
@app.post('/api/reports')
async def report(request:Request):
    f=await public_form(request);rate(request,'report',8,600);target_ok(f.get('target_type'),f.get('target_id'))
    reason=f.get('reason')
    if reason not in REASONS:raise HTTPException(422,'Invalid reason')
    write('INSERT INTO reports VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(target_type,target_id,visitor_hash) DO NOTHING',(uid(),f['target_type'],f['target_id'],visitor(request),reason,clean(f.get('body'),2000),'pending',now()))
    return {'ok':True,'message':'Rapò ou a voye bay ekip moderasyon an.'}
@app.post('/api/submissions')
async def submission(request:Request):
    f=await public_form(request);rate(request,'submit',5,1800)
    kind=f.get('kind')
    if kind not in ['influencer','news','contact','advertising','correction','removal']:raise HTTPException(422,'Invalid submission')
    sid=uid();attachments=[x for x in str(f.get('attachments','')).split(',') if x]
    if len(attachments)>3:raise HTTPException(422,'Twa fichye maksimòm.')
    with connection() as c:
        for id in attachments:
            if not c.execute(sql('SELECT id FROM submission_assets WHERE id=? AND visitor_hash=? AND submission_id IS NULL'),(id,visitor(request))).fetchone():raise HTTPException(403,'Pyès joint sa a pa pou navigatè ou oswa li deja voye.')
        c.execute(sql('INSERT INTO submissions VALUES (?,?,?,?,?,?,?)'),(sid,kind,clean(f.get('name'),200,2),clean(f.get('body'),15000,10),clean(f.get('contact'),250),'pending',now()))
        for id in attachments:c.execute(sql('UPDATE submission_assets SET submission_id=? WHERE id=?'),(sid,id))
    return {'ok':True,'message':'Mèsi! Ekip Geovyora resevwa mesaj ou a.'}

@app.post('/api/translate')
async def translation(request:Request):
    f=await public_form(request);rate(request,'translate',10,600)
    locale=f.get('locale');typ=f.get('target_type');id=f.get('target_id')
    if locale not in language_map() or typ not in ['article','comment','influencer']:raise HTTPException(422,'Lang oswa kontni pa sipòte.')
    target_ok(typ,id);table={'article':'articles','comment':'comments','influencer':'influencers'}[typ];r=one('SELECT * FROM '+table+' WHERE id=?',(id,))
    return queue_translation(typ,r,locale)

@app.post('/admin/translations/save')
async def save_translation(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,EDITOR)
    typ=f.get('target_type','article');id=f.get('target_id');locale=f.get('locale')
    if typ not in ['article','influencer'] or locale not in language_map():raise HTTPException(422,'Invalid translation')
    table='articles' if typ=='article' else 'influencers';record=one('SELECT * FROM '+table+' WHERE id=?',(id,))
    if not record:raise HTTPException(404,'Content not found')
    version=record.get('updated_at',record.get('created_at'))
    data={k:clean(f.get(k),100000) for k in (['title','subtitle','body'] if typ=='article' else ['bio'])}
    write('INSERT INTO translations VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(target_type,target_id,version,locale) DO UPDATE SET data=excluded.data,manual=1',(uid(),typ,id,version,locale,json.dumps(data),1,now()))
    audit(u,'translation.save',id,locale);return RedirectResponse('/admin/translations',303)

@app.post('/admin/videos/upload')
async def mux_upload(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,EDITOR)
    if not os.getenv('MUX_TOKEN_ID') or not os.getenv('MUX_TOKEN_SECRET'):raise HTTPException(503,'Konekte kle Mux yo anvan ou chaje yon videyo.')
    title=clean(f.get('title'),200,3);description=clean(f.get('description'),3000)
    id=uid();video_slug=slugify(title)+'-'+id[:6];site=os.getenv('SITE_URL','http://localhost:8000').rstrip('/')
    async with httpx.AsyncClient(timeout=30) as client:
        resp=await client.post('https://api.mux.com/video/v1/uploads',auth=(os.environ['MUX_TOKEN_ID'],os.environ['MUX_TOKEN_SECRET']),json={'cors_origin':site,'new_asset_settings':{'playback_policies':['public'],'video_quality':'basic','passthrough':id}})
    if resp.status_code not in [200,201]:raise HTTPException(502,'Mux pa disponib. Eseye ankò.')
    data=resp.json()['data']
    write('INSERT INTO videos(id,slug,title,description,upload_id,status,locale,created_at) VALUES (?,?,?,?,?,?,?,?)',(id,video_slug,title,description,data['id'],'uploading',f.get('locale','ht'),now()))
    audit(u,'video.upload',id);return {'url':data['url'],'id':id,'slug':video_slug,'max_bytes':int(os.getenv('MAX_VIDEO_BYTES','1073741824'))}
@app.post('/api/webhooks/mux')
async def mux_webhook(request:Request):
    raw=await request.body();secret=os.getenv('MUX_WEBHOOK_SECRET','');header=request.headers.get('mux-signature','')
    sig={}
    for part in header.split(','):
        if '=' in part:k,v=part.strip().split('=',1);sig.setdefault(k,[]).append(v)
    try:timestamp=int(sig['t'][0])
    except Exception:raise HTTPException(401,'Invalid signature')
    expected=hmac.new(secret.encode(),str(timestamp).encode()+b'.'+raw,hashlib.sha256).hexdigest()
    if not secret or abs(time.time()-timestamp)>300 or not any(hmac.compare_digest(expected,s) for s in sig.get('v1',[])):raise HTTPException(401,'Invalid signature')
    try:event=json.loads(raw);event_id=event['id'];d=event['data'];kind=event['type']
    except Exception:raise HTTPException(400,'Invalid event')
    with connection() as c:
        n=c.execute(sql('INSERT INTO webhook_events VALUES (?,?) ON CONFLICT(id) DO NOTHING'),(event_id,now())).rowcount
        if not n:return {'ok':True,'duplicate':True}
        if kind=='video.upload.asset_created':c.execute(sql("UPDATE videos SET status='processing',asset_id=? WHERE upload_id=?"),(d.get('asset_id'),d.get('id')))
        elif kind=='video.asset.ready':
            ids=d.get('playback_ids',[]);playback=next((p['id'] for p in ids if p.get('policy')=='public'),None)
            if playback:c.execute(sql("UPDATE videos SET status='ready',asset_id=?,playback_id=? WHERE id=? OR asset_id=?"),(d.get('id'),playback,d.get('passthrough'),d.get('id')))
        elif kind in ['video.asset.errored','video.upload.errored']:c.execute(sql("UPDATE videos SET status='error' WHERE asset_id=? OR upload_id=? OR id=?"),(d.get('id'),d.get('id'),d.get('passthrough')))
    return {'ok':True}

@app.get('/api/push/config')
def push_config():
    try:config=json.loads(os.getenv('FIREBASE_PUBLIC_CONFIG','{}'))
    except Exception:config={}
    return {'configured':bool(config and os.getenv('FIREBASE_SERVICE_ACCOUNT') and os.getenv('FIREBASE_VAPID_KEY')),'config':config,'vapidKey':os.getenv('FIREBASE_VAPID_KEY','')}
@app.get('/firebase-messaging-sw.js')
def push_sw():
    try:config=json.loads(os.getenv('FIREBASE_PUBLIC_CONFIG','{}'))
    except Exception:config={}
    code="importScripts('https://www.gstatic.com/firebasejs/12.4.0/firebase-app-compat.js');importScripts('https://www.gstatic.com/firebasejs/12.4.0/firebase-messaging-compat.js');firebase.initializeApp("+json.dumps(config)+");firebase.messaging();" if config else "// Firebase is not configured."
    return Response(code,media_type='application/javascript',headers={'Service-Worker-Allowed':'/'})
@app.post('/api/push/subscribe')
async def push_subscribe(request:Request):
    f=await public_form(request);rate(request,'subscribe',10,3600)
    if not push_config()['configured']:raise HTTPException(503,'Notifikasyon push poko konekte.')
    locale=f.get('locale','ht')
    if locale not in language_map():raise HTTPException(422,'Invalid locale')
    token=clean(f.get('token'),2000,10);topics=clean(f.get('topics'),2000)
    existing=one('SELECT topics FROM push_subscriptions WHERE visitor_hash=?',(visitor(request),))
    if existing:
        followed=[x for x in existing['topics'].split(',') if x.startswith('influencer:')]
        topics=','.join(sorted(set(topics.split(',')+followed)))
    with connection() as c:
        c.execute(sql('DELETE FROM push_subscriptions WHERE token=? AND visitor_hash<>?'),(token,visitor(request)))
        c.execute(sql('INSERT INTO push_subscriptions VALUES (?,?,?,?,?) ON CONFLICT(visitor_hash) DO UPDATE SET token=excluded.token,locale=excluded.locale,topics=excluded.topics'),(visitor(request),token,locale,topics,now()))
    return {'ok':True,'message':'Abònman an aktive sou navigatè sa a.'}
@app.post('/api/push/unsubscribe')
async def unsubscribe(request:Request):
    await public_form(request)
    with connection() as c:
        c.execute(sql('DELETE FROM push_subscriptions WHERE visitor_hash=?'),(visitor(request),))
        c.execute(sql('UPDATE comments SET subscribe_reply=0 WHERE visitor_hash=?'),(visitor(request),))
        c.execute(sql("UPDATE deliveries SET status='cancelled',updated_at=? WHERE visitor_hash=? AND status='queued'"),(now(),visitor(request)))
    return {'ok':True,'message':'Ou dezabòne.'}

def public(request:Request,locale:str,section:str='home',slug:str='',q:str='',category:str='',country:str='',platform:str='',sort:str='recent',page:int=1,original:int=0):
    if locale not in language_map():raise HTTPException(404,'Lang sa a pa disponib.')
    page=max(1,min(page,1000));a=None;p=None;videos=[];data=[];title=labels(locale).get(section,section)
    allowed=['home','haiti','world','news','interviews','videos','video','trending','rankings','discoveries','influencers','influencer','article','search','notifications','saved','submit-influencer','submit-news','contact','advertising','about','privacy','terms','cookies','editorial','community','copyright','category','newsletter','newsletter-unsubscribe']
    if section not in allowed:raise HTTPException(404,'Paj sa a pa egziste.')
    if section=='article':
        raw=one("SELECT * FROM articles WHERE slug=? AND status='published'"+public_demo_clause(),(slug,))
        if not raw:
            redirect=one('SELECT new_slug FROM redirects WHERE old_slug=?',(slug,))
            if redirect:return RedirectResponse('/'+locale+'/article/'+redirect['new_slug'],301)
            raise HTTPException(404,'Atik sa a pa disponib.')
        a=translate_record(raw,raw['locale'] if original else locale);title=a['title']
        if a['fallback'] and not original:queue_translation('article',raw,locale)
        # Bot filtering and browser/day deduplication; this is site readership, never social ranking.
        if not re.search(r'bot|crawler|spider|headless',request.headers.get('user-agent',''),re.I):
            write('INSERT INTO page_views VALUES (?,?,?,?,?) ON CONFLICT(article_id,visitor_hash,day) DO NOTHING',(uid(),a['id'],visitor(request),now()[:10],now()))
        data=article_list('id<>?',(a['id'],),3)
    elif section=='influencer':
        p=one("SELECT * FROM influencers WHERE slug=? AND status='published'"+public_demo_clause(),(slug,))
        if not p:raise HTTPException(404,'Pwofil medya sa a pa disponib.')
        p.setdefault('locale','ht');p=translate_record(p,locale,'influencer');p['socials']=json.loads(p['socials']);p['metrics']=rows('SELECT * FROM influencer_metrics WHERE influencer_id=? ORDER BY observed_at DESC',(p['id'],));title=p['name'];data=article_list('influencer_id=?',(p['id'],))
    elif section=='video':
        a=one("SELECT * FROM videos WHERE slug=? AND status='ready'",(slug,))
        if not a:raise HTTPException(404,'Videyo sa a poko disponib.')
        title=a['title']
    elif section=='influencers':
        where="status='published'"+public_demo_clause();args=[]
        for name,value in [('category',category),('residence',country)]:
            if value:where+=' AND '+name+'=?';args.append(value)
        if platform:where+=' AND socials LIKE ?';args.append('%"'+platform+'"%')
        data=rows('SELECT * FROM influencers WHERE '+where+' ORDER BY '+('name' if sort=='name' else 'created_at DESC'),tuple(args))
        if q:data=[r for r in data if search_matches(r,q,['name','username','category','bio'])]
        data=data[(page-1)*24:page*24]
    elif section=='search':
        data=[r for r in article_list(limit=5000) if search_matches(r,q,['title','subtitle','body','tags'])] if q else []
        profiles=[r for r in rows("SELECT * FROM influencers WHERE status='published'"+public_demo_clause()) if search_matches(r,q,['name','username','category','bio'])] if q else []
        videos=[r for r in rows("SELECT * FROM videos WHERE status='ready'") if search_matches(r,q,['title','description','category'])] if q else []
        return render(request,section,locale,articles=[translate_record(x,locale) for x in data[(page-1)*24:page*24]],q=q,title=title,profiles=profiles[:24],videos=videos[:24],total_results=len(data)+len(profiles)+len(videos))
    elif section=='videos':videos=rows("SELECT * FROM videos WHERE status='ready' ORDER BY created_at DESC")
    elif section in ['trending','rankings']:
        data=rows("SELECT a.*,count(v.id) readership FROM articles a JOIN page_views v ON a.id=v.article_id WHERE a.status='published'"+public_demo_clause("a.")+" AND v.day>=? GROUP BY a.id ORDER BY readership DESC LIMIT 24",((datetime.now(timezone.utc)-timedelta(days=7)).date().isoformat(),))
    elif section in ['home','haiti','world','news','interviews','discoveries','category']:
        where='1=1';args=[]
        if section in ['haiti','world']:where+=' AND region=?';args.append(section)
        if section=='interviews':where+=" AND kind='interview'"
        if section=='discoveries':where+=" AND category='Dekouvèt'"
        if section=='category':
            cat=one('SELECT name FROM categories WHERE slug=? AND active=1',(slug,))
            if not cat:raise HTTPException(404,'Kategori pa jwenn.')
            where+=' AND category=?';args.append(cat['name']);title=cat['name']
        if category:where+=' AND category=?';args.append(category)
        data=article_list(where,tuple(args),5000)[(page-1)*12:page*12]
    return render(request,section,locale,articles=[translate_record(x,locale) for x in data] if section!='influencers' else [],profiles=data if section=='influencers' else rows("SELECT * FROM influencers WHERE status='published'"+public_demo_clause()+" LIMIT 4"),article=a,profile=p,videos=videos,title=title,q=q,category=category,country=country,platform=platform,sort=sort,pagination=page)

@app.post('/admin/campaigns/save')
async def save_campaign(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,ADMIN)
    link=clean(f.get('url'),500,2);locale=f.get('locale','ht')
    if not link.startswith('/'+locale+'/') or '\\' in link or locale not in language_map():raise HTTPException(422,'Lyen relatif ak lang lan pa valab.')
    scheduled=f.get('scheduled_at') or None;status='draft'
    if scheduled:
        try:
            stamp=datetime.fromisoformat(scheduled).replace(tzinfo=timezone.utc)
            if stamp<=datetime.now(timezone.utc):raise ValueError()
            scheduled=stamp.isoformat();status='scheduled'
        except ValueError:raise HTTPException(422,'Chwazi yon dat UTC nan lavni.')
    influencer=f.get('influencer_id') or None
    if influencer and not one("SELECT id FROM influencers WHERE id=? AND status='published'",(influencer,)):raise HTTPException(422,'Pwofil pa disponib.')
    id=uid();write('INSERT INTO campaigns(id,title,body,url,locale,status,created_at,topic,scheduled_at,influencer_id) VALUES (?,?,?,?,?,?,?,?,?,?)',(id,clean(f.get('title'),120,3),clean(f.get('body'),500,3),link,locale,status,now(),clean(f.get('topic'),80),scheduled,influencer));audit(u,'campaign.save',id);return RedirectResponse('/admin/notifications?saved=1',303)

@app.post('/admin/campaigns/send')
async def send_campaign(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,ADMIN)
    if not push_config()['configured']:raise HTTPException(503,'Firebase poko konekte.')
    if not enqueue_campaign(f.get('id')):raise HTTPException(409,'Kanpay sa a te deja kòmanse oswa li pa egziste.')
    audit(u,'campaign.queued',f.get('id'));return RedirectResponse('/admin/notifications?saved=1',303)

@app.post('/admin/campaigns/cancel')
async def cancel_campaign(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,ADMIN)
    id=f.get('id')
    write("UPDATE campaigns SET status='cancelled' WHERE id=? AND status IN ('draft','scheduled','queued')",(id,));write("UPDATE deliveries SET status='cancelled',updated_at=? WHERE campaign_id=? AND status='queued'",(now(),id));audit(u,'campaign.cancelled',id);return RedirectResponse('/admin/notifications',303)

@app.get('/admin/preview/{id}')
def preview(request:Request,id:str):
    require(request,EDITOR);article=one('SELECT * FROM articles WHERE id=?',(id,))
    if not article:raise HTTPException(404,'Atik pa jwenn.')
    article=translate_record(article,article['locale']);article['demo']=1
    return render(request,'article',article['locale'],article=article,articles=[],title='Preview · '+article['title'])

@app.post('/admin/media/upload-url')
async def media_upload(request:Request):
    f=await request.form();u=csrf(request,f.get('csrf_token'));require(request,EDITOR)
    mime=f.get('content_type');types={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}
    if mime not in types:raise HTTPException(422,'Sèlman JPG, PNG ak WebP.')
    if not all(os.getenv(k) for k in ['S3_BUCKET','S3_ACCESS_KEY_ID','S3_SECRET_ACCESS_KEY','MEDIA_PUBLIC_URL']):raise HTTPException(503,'Storage foto poko konekte.')
    import boto3
    from botocore.config import Config
    client=boto3.client('s3',endpoint_url=os.getenv('S3_ENDPOINT_URL') or None,region_name=os.getenv('S3_REGION','us-east-1'),aws_access_key_id=os.environ['S3_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['S3_SECRET_ACCESS_KEY'],config=Config(signature_version='s3v4'))
    id=uid();key='vyora/'+id+types[mime];url=os.environ['MEDIA_PUBLIC_URL'].rstrip('/')+'/'+key
    signed=client.generate_presigned_url('put_object',Params={'Bucket':os.environ['S3_BUCKET'],'Key':key,'ContentType':mime},ExpiresIn=300)
    write('INSERT INTO media_assets(id,object_key,url,content_type,status,staff_id,created_at) VALUES (?,?,?,?,?,?,?)',(id,key,url,mime,'pending',u['id'],now()));audit(u,'media.presign',id)
    return {'id':id,'url':signed,'method':'PUT','headers':{'Content-Type':mime},'public_url':url}

from extensions import install
install(app)

app.get("/{locale}")(public)
app.get("/{locale}/{section}")(public)
app.get("/{locale}/{section}/{slug}")(public)

@app.post('/admin/services/check')
async def check_services(request:Request):
    import asyncio
    from service_checks import run_check
    f=await request.form()
    csrf(request,f.get('csrf_token'));require(request,ADMIN)
    rate(request,'service-check',5,60)
    names=['Mux','Storage','Firebase']
    results=await asyncio.gather(*(asyncio.to_thread(run_check,name) for name in names))
    return admin(request,service_checks=dict(zip(names,results)))
