from db import one,write,connection,sql,URL
from datetime import datetime,timezone
import uuid,json

def seed():
    with connection() as c:
        if URL:c.execute('SELECT pg_advisory_xact_lock(861410074)')
        else:c.execute('BEGIN IMMEDIATE')
        _seed(c)

def _seed(c):
    def one(query,args=()):
        row=c.execute(sql(query),args).fetchone();return dict(row) if row else None
    def write(query,args=()):return c.execute(sql(query),args).rowcount
    if one("SELECT key FROM settings WHERE key='initialized'"): return
    now=datetime.now(timezone.utc).isoformat()
    items=[
      ('voix-qui-traversent-les-frontieres','Vwa ki travèse fwontyè yo','Yon nouvo jenerasyon kreyatè ap rakonte Ayiti, yon istwa alafwa.','Kilti','haiti','article',1),
      ('kreyativite-san-limit','Kreyativite pa gen fwontyè','Rankont ak lide ki konekte dyaspora a ak kilti li.','Lifestyle','haiti','interview',0),
      ('bati-kominote','Kreye yon kominote ki gen sans','Poukisa bon konvèsasyon pi enpòtan pase gwo chif.','Biznis','world','article',0),
      ('mizik-nouvo-jenerasyon','Mizik, idantite ak nouvo jenerasyon an','Lè tradisyon rankontre nouvo son ak nouvo fòma.','Mizik','haiti','article',0),
      ('ti-istwa-gwo-enpak','Ti istwa, gwo enpak','Dekouvri yon apwòch ki mete lavi chak jou devan kamera a.','Dekouvèt','haiti','article',0),
      ('kamera-kreyativite','Dèyè kamera a: travay ou pa toujou wè','Yon gade sou preparasyon, montaj ak rechèch kreyatif.','Teknoloji','world','article',0)]
    body="Sa a se yon atik demonstrasyon orijinal Geovyora. Li montre jan yon atik ap parèt sou sit la; li pa yon nouvèl verifye sou yon moun reyèl.\n\nKreyativite kòmanse ak yon fason pèsonèl pou gade mond lan. Nan egzanp editoryal sa a, nou eksplore fason yon kreyatè fiktif pataje istwa, bati yon relasyon ak kominote li epi bay kilti a yon plas nan travay li.\n\n## Rakonte istwa ki gen sans\n\nYon bon istwa pran tan. Li mande koute, chèche sous epi respekte moun ki ladanl. Chak atik reyèl sou Geovyora ap bezwen sous, kredi foto ak yon revizyon editoryal anvan piblikasyon.\n\n## Kenbe yon vwa pa ou\n\nKreyatè yo gen diferan lang, diferan eksperyans ak diferan ritm. Magazin sa a kreye yon espas pou dekouvri diferans sa yo, san redui yon moun ak kantite abonnés li.\n\nOu kapab kite yon kòmantè anba paj la. Ekip moderasyon an ap li li anvan li parèt piblikman."
    for slug,title,sub,cat,region,kind,featured in items:
        write('INSERT INTO articles(id,slug,title,subtitle,body,category,region,kind,image,image_credit,author,locale,status,featured,demo,publish_at,created_at,updated_at,tags) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),slug,title,sub,body,cat,region,kind,'/static/editorial.jpg','Illustration originale générée par IA · personnage fictif','Ekip Geovyora','ht','published',featured,1,now,now,now,'kreyativite,kilti,dyaspora'))
    for slug,name,handle,home,res,cat in [('naelle-jean','Naëlle Jean','@naelle.creative','Ayiti','Kanada','Kilti'),('noah-pierre','Noah Pierre','@noah.stories','Ayiti','Lafrans','Lifestyle'),('mila-louis','Mila Louis','@mila.atelier','Ayiti','Ayiti','Mòd'),('eli-martin','Eli Martin','@eli.creates','Matinik','Brezil','Mizik')]:
        write('INSERT INTO influencers(id,slug,name,username,origin,residence,category,bio,image,socials,demo,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),slug,name,handle,home,res,cat,'Pwofil demonstrasyon. Moun sa a fiktif. Paj sa a montre bio, orijin, kategori ak atik asosye yo; pa gen estatistik rezo sosyal envante.','',json.dumps({}),1,now,now))
    for k,v in {'initialized':'1','brand':'Geovyora','contact_email':'','tagline':'Kilti. Kreyativite. Enpak.','default_locale':'ht','translation_limit':'100000','ads_enabled':'0','publisher_id':'','ad_slot':'','push_enabled':'0','moderation':'prepublication'}.items(): write('INSERT INTO settings(key,value) VALUES (?,?)',(k,v))
