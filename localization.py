"""Local UI phrases. Never sends visitor data or translates usernames/URLs."""
from html.parser import HTMLParser
import html
# HT source phrase -> FR, EN, PT-BR, ES. Content articles remain separate translations.
PHRASES={
'Pa rate pwochen istwa a.':['Ne manquez pas la prochaine histoire.','Don’t miss the next story.','Não perca a próxima história.','No te pierdas la próxima historia.'],
'Chwazi nouvèl ou vle resevwa, sou navigatè ou.':['Choisissez les actualités à recevoir dans votre navigateur.','Choose the stories to receive in your browser.','Escolha as notícias para receber no seu navegador.','Elige las noticias para recibir en tu navegador.'],
'RESTE KONEKTE':['RESTEZ INFORMÉ','STAY INFORMED','FIQUE POR DENTRO','MANTENTE AL DÍA'],
'Yon lòt gade sou kreyativite.':['Un autre regard sur la créativité.','A fresh perspective on creativity.','Um novo olhar sobre a criatividade.','Otra mirada a la creatividad.'],
'Enfòmasyon':['Informations','Information','Informações','Información'],
'Règleman editoryal':['Politique éditoriale','Editorial policy','Política editorial','Política editorial'],
'Kominote':['Communauté','Community','Comunidade','Comunidad'],
'Administrasyon':['Administration','Administration','Administração','Administración'],
'Copyright / Retrè':['Copyright / Retrait','Copyright / Removal','Direitos autorais / Remoção','Derechos de autor / Retirada'],
'FÈ AK KREYATIVITE':['CRÉÉ AVEC CRÉATIVITÉ','MADE WITH CREATIVITY','FEITO COM CRIATIVIDADE','HECHO CON CREATIVIDAD'],
'Kreyatè Ayisyen, kilti nou, istwa nou. Ayiti ak dyaspora a.':['Créateurs haïtiens, notre culture, nos histoires. Haïti et la diaspora.','Haitian creators, our culture, our stories. Haiti and the diaspora.','Criadores haitianos, nossa cultura, nossas histórias. Haiti e a diáspora.','Creadores haitianos, nuestra cultura, nuestras historias. Haití y la diáspora.'],
'Lòt vwa, lòt kilti. Kreyativite atravè mond lan.':['D’autres voix, d’autres cultures. La créativité dans le monde.','Other voices, other cultures. Creativity around the world.','Outras vozes, outras culturas. Criatividade pelo mundo.','Otras voces, otras culturas. Creatividad por el mundo.'],
'Konvèsasyon sou lide, eksperyans ak travay kreyatif.':['Des conversations sur les idées, les expériences et la création.','Conversations about ideas, experiences and creative work.','Conversas sobre ideias, experiências e trabalho criativo.','Conversaciones sobre ideas, experiencias y trabajo creativo.'],
'Atik ki plis li sou Geovyora pandan 7 dènye jou yo. Done sou sit sa a sèlman.':['Les articles les plus lus sur Geovyora sur 7 jours. Données de ce site uniquement.','The most read Geovyora stories over the last 7 days. Data from this site only.','Artigos mais lidos no Geovyora nos últimos 7 dias. Dados apenas deste site.','Artículos más leídos en Geovyora durante los últimos 7 días. Datos solo de este sitio.'],
'ANYÈ EDITORYAL':['ANNUAIRE ÉDITORIAL','EDITORIAL DIRECTORY','DIRETÓRIO EDITORIAL','DIRECTORIO EDITORIAL'],
'Yon espas pou dekouvri vwa Ayiti, dyaspora a ak mond lan.':['Un espace pour découvrir les voix d’Haïti, de la diaspora et du monde.','Discover voices from Haiti, the diaspora and around the world.','Descubra vozes do Haiti, da diáspora e do mundo.','Descubre voces de Haití, la diáspora y el mundo.'],
'Non, pseudo, kategori':['Nom, pseudo, catégorie','Name, alias, category','Nome, apelido, categoria','Nombre, alias, categoría'],
'Tout peyi rezidans':['Tous les pays de résidence','All countries of residence','Todos os países de residência','Todos los países de residencia'],
'Tout platfòm':['Toutes les plateformes','All platforms','Todas as plataformas','Todas las plataformas'],
'Dènye ajoute':['Derniers ajouts','Recently added','Adicionados recentemente','Añadidos recientemente'],
'Orijin':['Origine','Origin','Origem','Origen'],
'Rezidans':['Résidence','Residence','Residência','Residencia'],
'Lang':['Langue','Language','Idioma','Idioma'],
'Sous piblik':['Source publique','Public source','Fonte pública','Fuente pública'],
'Estatistik piblik: done verifye poko disponib.':['Statistiques publiques : aucune donnée vérifiée disponible.','Public statistics: verified data is not available yet.','Estatísticas públicas: dados verificados ainda indisponíveis.','Estadísticas públicas: aún no hay datos verificados.'],
'Resevwa nouvèl sou kreyatè sa a':['Recevoir les actualités de ce créateur','Receive news about this creator','Receber notícias deste criador','Recibir noticias de este creador'],
'Pwopoze yon koreksyon':['Proposer une correction','Suggest a correction','Sugerir uma correção','Proponer una corrección'],
'Pa gen atik asosye pou kounye a.':['Aucun article associé pour le moment.','There are no related stories yet.','Ainda não há artigos relacionados.','Aún no hay artículos relacionados.'],
'Entèvyou, rankont ak istwa dèyè kamera a.':['Entretiens, rencontres et récits en coulisses.','Interviews, encounters and stories behind the camera.','Entrevistas, encontros e histórias nos bastidores.','Entrevistas, encuentros e historias detrás de cámaras.'],
'Nouvo konvèsasyon ap vini.':['De nouvelles conversations arrivent.','New conversations are coming.','Novas conversas estão chegando.','Llegan nuevas conversaciones.'],
'Videyo yo ap parèt isit la lè ekip la fin pibliye yo.':['Les vidéos apparaîtront ici après leur publication.','Videos will appear here once the team publishes them.','Os vídeos aparecerão aqui após a publicação.','Los vídeos aparecerán aquí cuando el equipo los publique.'],
'Chwazi istwa ki enterese ou.':['Choisissez les histoires qui vous intéressent.','Choose the stories that interest you.','Escolha as histórias que interessam a você.','Elige las historias que te interesan.'],
'Resevwa nouvèl sou navigatè sa a, san kreye kont. Ou kapab dezabòne nenpòt lè.':['Recevez les actualités dans ce navigateur, sans compte. Désabonnez-vous à tout moment.','Receive stories in this browser, without an account. Unsubscribe at any time.','Receba notícias neste navegador, sem conta. Cancele a inscrição a qualquer momento.','Recibe noticias en este navegador, sin cuenta. Puedes cancelar en cualquier momento.'],
'Aktive notifikasyon':['Activer les notifications','Enable notifications','Ativar notificações','Activar notificaciones'],
'Dezabòne':['Se désabonner','Unsubscribe','Cancelar inscrição','Cancelar suscripción'],
'SOU NAVIGATÈ SA A':['DANS CE NAVIGATEUR','IN THIS BROWSER','NESTE NAVEGADOR','EN ESTE NAVEGADOR'],
'Atik ou konsève yo rete sou aparèy sa a.':['Vos articles enregistrés restent sur cet appareil.','Your saved stories stay on this device.','Seus artigos salvos ficam neste dispositivo.','Tus artículos guardados permanecen en este dispositivo.'],
'ANN PALE':['PARLONS-EN','LET’S TALK','VAMOS CONVERSAR','HABLEMOS'],
'Chak soumisyon pase nan revizyon. Nou pa pibliye enfòmasyon otomatikman.':['Chaque proposition est examinée. Rien n’est publié automatiquement.','Every submission is reviewed. Information is not published automatically.','Toda submissão é revisada. Nada é publicado automaticamente.','Cada envío se revisa. Nada se publica automáticamente.'],
'Non / Sijè':['Nom / Sujet','Name / Subject','Nome / Assunto','Nombre / Asunto'],
'Non, orijin, kategori ak lyen sosyal':['Nom, origine, catégorie et liens sociaux','Name, origin, category and social links','Nome, origem, categoria e links sociais','Nombre, origen, categoría y enlaces sociales'],
'Enfòmasyon an ak sous li yo':['Information et sources','Information and sources','Informações e fontes','Información y fuentes'],
'Mesaj ou':['Votre message','Your message','Sua mensagem','Tu mensaje'],
'Kontak ou':['Vos coordonnées','Your contact details','Seu contato','Tu contacto'],
'(opsyonèl)':['(facultatif)','(optional)','(opcional)','(opcional)'],
'Imel oswa nimewo telefòn':['Email ou téléphone','Email or phone number','Email ou telefone','Correo o teléfono'],
'Voye mesaj la':['Envoyer le message','Send message','Enviar mensagem','Enviar mensaje'],
'Pseudo yo pa idantite verifye. Kòmantè yo pase nan moderasyon anvan piblikasyon.':['Les pseudos ne sont pas des identités vérifiées. Les commentaires sont modérés avant publication.','Aliases are not verified identities. Comments are moderated before publication.','Apelidos não são identidades verificadas. Comentários são moderados antes da publicação.','Los alias no son identidades verificadas. Los comentarios se moderan antes de publicarse.'],
'Pi resan':['Plus récents','Newest','Mais recentes','Más recientes'],
'Pi apresye':['Plus appréciés','Most liked','Mais curtidos','Más valorados'],
'Plis kòmantè':['Plus de commentaires','More comments','Mais comentários','Más comentarios'],
'Resevwa repons yo si push deja aktive sou navigatè sa a':['Recevoir les réponses si les notifications sont activées ici','Receive replies if push is already enabled in this browser','Receber respostas se o push estiver ativo neste navegador','Recibir respuestas si el push está activo en este navegador'],
'Chèche lòt lang':['Rechercher d’autres langues','Find more languages','Buscar outros idiomas','Buscar otros idiomas'],
'Chèche yon lang…':['Rechercher une langue…','Search a language…','Buscar um idioma…','Buscar un idioma…'],
'Tradiksyon editoryal':['Traduction éditoriale','Editorial translation','Tradução editorial','Traducción editorial'],
'Abòne':['S’abonner','Subscribe','Inscrever-se','Suscribirse'],
'Imel':['Email','Email','Email','Correo electrónico'],
'Konfime dezabònman':['Confirmer le désabonnement','Confirm unsubscribe','Confirmar cancelamento','Confirmar cancelación'],
'Istwa Geovyora nan imel ou.':['Les histoires Geovyora dans votre boîte mail.','Geovyora stories in your inbox.','Histórias Geovyora no seu email.','Historias Geovyora en tu correo.'],
'Newsletter la opsyonèl. Imel ou sèvi sèlman pou abònman sa a; li pa kreye yon kont.':['La newsletter est facultative. Votre email sert uniquement à cet abonnement, sans compte.','The newsletter is optional. Your email is only used for this subscription; it does not create an account.','A newsletter é opcional. Seu email serve apenas para esta assinatura; não cria uma conta.','La newsletter es opcional. Tu correo solo se usa para esta suscripción; no crea una cuenta.'],
'Mwen dakò resevwa newsletter Geovyora.':['J’accepte de recevoir la newsletter Geovyora.','I agree to receive the Geovyora newsletter.','Concordo em receber a newsletter Geovyora.','Acepto recibir la newsletter Geovyora.'],
}
LOCALES={'fr':0,'en':1,'pt-BR':2,'es':3}
def ui_text(value,locale):
    i=LOCALES.get(locale)
    return PHRASES[value][i] if i is not None and value in PHRASES else value
class Localizer(HTMLParser):
    def __init__(self,locale):super().__init__(convert_charrefs=False);self.locale=locale;self.parts=[];self.verbatim=0;self.catalog=ui_translation(locale) if locale!='ht' else {};self.stack=[]
    def translated(self,value):
        local=ui_text(value,self.locale)
        return local if local!=value else self.catalog.get('phrase:'+value,value)
    def handle_starttag(self,tag,attrs):
        source=self.get_starttag_text()
        for key,value in attrs:
            if key in ['placeholder','aria-label','title'] and (value in PHRASES or 'phrase:'+str(value) in self.catalog):
                old=html.escape(value,quote=True);new=html.escape(self.translated(value),quote=True);source=source.replace('"'+old+'"','"'+new+'"')
        self.parts.append(source)
        protected=tag in ['script','style'] or any(key=='class' and ('article-body' in (val or '') or 'profile-bio' in (val or '')) for key,val in attrs)
        if tag not in ['meta','link','input','img','br','hr','source','wbr','area','base','embed','param','track','col']:
            self.stack.append((tag,protected))
        if protected:self.verbatim+=1
    def handle_startendtag(self,tag,attrs):self.parts.append(self.get_starttag_text())
    def handle_endtag(self,tag):
        self.parts.append('</'+tag+'>')
        if self.stack and self.stack[-1][0]==tag:
            _,protected=self.stack.pop()
            if protected:self.verbatim=max(0,self.verbatim-1)
    def handle_data(self,text):
        stripped=text.strip()
        self.parts.append(text.replace(stripped,html.escape(self.translated(stripped)),1) if stripped and not self.verbatim else text)
    def handle_entityref(self,name):self.parts.append('&'+name+';')
    def handle_charref(self,name):self.parts.append('&#'+name+';')
    def handle_decl(self,decl):self.parts.append('<!'+decl+'>')
    def handle_comment(self,text):self.parts.append('<!--'+text+'-->')
def localize_html(source,locale):
    if locale=='ht':return source
    parser=Localizer(locale);parser.feed(source);return ''.join(parser.parts)

def ui_catalog():
    from pathlib import Path
    from i18n import KEYS,VALUES
    catalog={'label:'+k:v for k,v in zip(KEYS,VALUES['en'])}
    # Only repository-authored interface phrases; never user comments, bio or article text.
    for phrase,translations in PHRASES.items():catalog['phrase:'+phrase]=translations[1]
    for name in ['site.html','comments.html','newsletter.html','home_notifications.html']:
        source=(Path(__file__).parent/'templates'/name).read_text()
        import re
        for text in re.findall(r'>([^<>]+)<',source):
            text=text.strip()
            if not text or '{' in text or len(text)<3 or 'Geovyora /' in text or text in ['Geovyora','AYITI · DYASPORA · MOND','KILTI. KREYATIVITE. ENPAK.','AYITI. DYASPORA. MOND.']:continue
            catalog.setdefault('phrase:'+text,ui_text(text,'en'))
    return catalog

def catalog_version():
    import hashlib,json
    return hashlib.sha256(json.dumps(ui_catalog(),sort_keys=True).encode()).hexdigest()

def ui_translation(locale):
    from db import one
    import json
    r=one("SELECT data FROM translations WHERE target_type='ui' AND target_id='ui' AND version=? AND locale=?",(catalog_version(),locale))
    return json.loads(r['data']) if r else {}

def queue_ui(locale):
    from jobs import queue_translation
    from i18n import LANGUAGES
    # Local dictionaries already cover core navigation; queue remaining interface copy too.
    return queue_translation('ui',{'id':'ui','updated_at':catalog_version(),'payload':ui_catalog()},locale)
