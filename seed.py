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
      ('voix-qui-traversent-les-frontieres','Des voix sans frontières','Une nouvelle génération de créateurs raconte Haïti, une histoire à la fois.','Kilti','haiti','article',1),
      ('kreyativite-san-limit','La créativité sans frontières','Rencontres et idées qui relient la diaspora à sa culture.','Lifestyle','haiti','interview',0),
      ('bati-kominote','Créer une communauté qui compte','Pourquoi les échanges sincères comptent plus que les grands chiffres.','Biznis','world','article',0),
      ('mizik-nouvo-jenerasyon','Musique, identité et nouvelle génération','Quand les traditions rencontrent de nouveaux sons et formats.','Mizik','haiti','article',0),
      ('ti-istwa-gwo-enpak','Une petite histoire, un grand impact','Découvrir une approche qui place la vie quotidienne devant la caméra.','Dekouvèt','haiti','article',0),
      ('kamera-kreyativite','Derrière la caméra : le travail invisible','Un regard sur la préparation, le montage et la recherche créative.','Teknoloji','world','article',0)]
    body="Ce contenu de démonstration original présente le format d’un article Geovyora. Il ne s’agit pas d’une actualité vérifiée sur une personne réelle.\n\nLa créativité commence par un regard personnel sur le monde. Cet exemple éditorial montre comment un créateur fictif peut partager des récits, créer un lien avec sa communauté et donner une place à la culture.\n\n## Raconter des histoires utiles\n\nUn bon récit demande du temps, de l’écoute, des sources et du respect pour les personnes concernées. Chaque véritable article de Geovyora doit inclure des sources, des crédits photo et une révision éditoriale avant publication.\n\n## Trouver sa propre voix\n\nLes créateurs ont des langues, des expériences et des rythmes différents. Ce magazine leur offre un espace pour faire découvrir cette diversité sans réduire une personne au nombre de ses abonnés.\n\nLes lecteurs peuvent commenter sous l’article. L’équipe de modération examine les commentaires avant leur publication."
    for slug,title,sub,cat,region,kind,featured in items:
        write('INSERT INTO articles(id,slug,title,subtitle,body,category,region,kind,image,image_credit,author,locale,status,featured,demo,publish_at,created_at,updated_at,tags) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),slug,title,sub,body,cat,region,kind,'/static/editorial.jpg','Illustration originale générée par IA · personnage fictif','Équipe Geovyora','fr','published',featured,1,now,now,now,'creativite,culture,diaspora'))
    for slug,name,handle,home,res,cat in [('naelle-jean','Naëlle Jean','@naelle.creative','Ayiti','Kanada','Kilti'),('noah-pierre','Noah Pierre','@noah.stories','Ayiti','Lafrans','Lifestyle'),('mila-louis','Mila Louis','@mila.atelier','Ayiti','Ayiti','Mòd'),('eli-martin','Eli Martin','@eli.creates','Matinik','Brezil','Mizik')]:
        write('INSERT INTO influencers(id,slug,name,username,origin,residence,category,bio,image,socials,demo,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),slug,name,handle,home,res,cat,'Profil de démonstration fictif. Cette page présente une biographie, une origine, une catégorie et des articles associés ; aucune statistique sociale n’est inventée.','',json.dumps({}),1,now,now))
    for k,v in {'initialized':'1','brand':'Geovyora','contact_email':'','tagline':'Culture. Créativité. Impact.','default_locale':'fr','translation_limit':'100000','ads_enabled':'0','publisher_id':'','ad_slot':'','push_enabled':'0','moderation':'prepublication'}.items(): write('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO NOTHING',(k,v))
