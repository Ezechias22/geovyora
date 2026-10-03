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
PHRASES.update({'AYITI · DYASPORA · MOND': ['HAÏTI · DIASPORA · MONDE', 'HAITI · DIASPORA · WORLD', 'HAITI · DIÁSPORA · MUNDO', 'HAITÍ · DIÁSPORA · MUNDO'], 'AYITI. DYASPORA. MOND.': ['HAÏTI. DIASPORA. MONDE.', 'HAITI. DIASPORA. WORLD.', 'HAITI. DIÁSPORA. MUNDO.', 'HAITÍ. DIÁSPORA. MUNDO.'], 'AYITI & DYASPORA': ['HAÏTI & DIASPORA', 'HAITI & DIASPORA', 'HAITI & DIÁSPORA', 'HAITÍ & DIÁSPORA'], 'KILTI. KREYATIVITE. ENPAK.': ['CULTURE. CRÉATIVITÉ. IMPACT.', 'CULTURE. CREATIVITY. IMPACT.', 'CULTURA. CRIATIVIDADE. IMPACTO.', 'CULTURA. CREATIVIDAD. IMPACTO.'], 'Anvan': ['Précédent', 'Previous', 'Anterior', 'Anterior'], 'Apre': ['Suivant', 'Next', 'Próximo', 'Siguiente'], 'Dekouvri lòt vwa.': ['Découvrez d’autres voix.', 'Discover other voices.', 'Descubra outras vozes.', 'Descubre otras voces.'], 'Istwa kreyatè Ayisyen ak dyaspora a, nan yon sèl espas.': ['Les histoires des créateurs haïtiens et de la diaspora, en un seul lieu.', 'Stories from Haitian and diaspora creators, in one place.', 'Histórias de criadores haitianos e da diáspora em um só lugar.', 'Historias de creadores haitianos y de la diáspora en un solo lugar.'], 'Disponiblite depann de navigatè ou. Sou iPhone/iPad, ou ka bezwen ajoute sit la sou ekran dakèy ou.': ['La disponibilité dépend du navigateur. Sur iPhone/iPad, vous devrez peut-être ajouter le site à votre écran d’accueil.', 'Availability depends on your browser. On iPhone/iPad, you may need to add the site to your home screen.', 'A disponibilidade depende do navegador. No iPhone/iPad, pode ser necessário adicionar o site à tela inicial.', 'La disponibilidad depende del navegador. En iPhone/iPad, puede que debas añadir el sitio a la pantalla de inicio.'], 'Foto pou ekip revizyon an (opsyonèl, 3 maksimòm)': ['Photos pour la rédaction (facultatif, 3 maximum)', 'Photos for the editorial team (optional, up to 3)', 'Fotos para a equipe editorial (opcional, até 3)', 'Fotos para el equipo editorial (opcional, hasta 3)'], '10 MB maksimòm. Fichye yo rete prive.': ['10 Mo maximum. Les fichiers restent privés.', 'Maximum 10 MB. Files remain private.', 'Máximo de 10 MB. Os arquivos permanecem privados.', 'Máximo 10 MB. Los archivos permanecen privados.'], 'Chaje foto a': ['Envoyer la photo', 'Upload photo', 'Enviar foto', 'Subir foto'], 'Magazin': ['Magazine', 'Magazine', 'Revista', 'Revista'], 'Lang / Languages': ['Langues', 'Languages', 'Idiomas', 'Idiomas'], 'Lòt lang yo soti nan lis sèvis tradiksyon ki konekte a.': ['Les autres langues proviennent du service de traduction connecté.', 'Other languages come from the connected translation service.', 'Os outros idiomas vêm do serviço de tradução conectado.', 'Los demás idiomas proceden del servicio de traducción conectado.'], 'Rapò a ale bay ekip la pou revizyon.': ['Le signalement sera examiné par l’équipe.', 'The team will review your report.', 'A equipe analisará sua denúncia.', 'El equipo revisará tu denuncia.'], 'Rezon': ['Motif', 'Reason', 'Motivo', 'Motivo'], 'Jouman / arasman': ['Insultes / harcèlement', 'Abuse / harassment', 'Ofensas / assédio', 'Insultos / acoso'], 'Rayisman': ['Haine', 'Hate', 'Ódio', 'Odio'], 'Menas': ['Menaces', 'Threats', 'Ameaças', 'Amenazas'], 'Enfòmasyon prive': ['Informations privées', 'Private information', 'Informações privadas', 'Información privada'], 'Usurpasyon': ['Usurpation d’identité', 'Impersonation', 'Falsa identidade', 'Suplantación'], 'Fo enfòmasyon': ['Fausses informations', 'Misinformation', 'Informações falsas', 'Información falsa'], 'Lòt': ['Autre', 'Other', 'Outro', 'Otro'], 'Eksplikasyon (opsyonèl)': ['Explication (facultatif)', 'Explanation (optional)', 'Explicação (opcional)', 'Explicación (opcional)'], 'Voye rapò a': ['Envoyer le signalement', 'Submit report', 'Enviar denúncia', 'Enviar denuncia'], 'Rechèch': ['Recherche', 'Search', 'Pesquisa', 'Búsqueda'], 'Kategori': ['Catégorie', 'Category', 'Categoria', 'Categoría'], 'Peyi rezidans': ['Pays de résidence', 'Country of residence', 'País de residência', 'País de residencia'], 'Platfòm': ['Plateforme', 'Platform', 'Plataforma', 'Plataforma'], 'Kontak ou (opsyonèl)': ['Vos coordonnées (facultatif)', 'Your contact details (optional)', 'Seu contato (opcional)', 'Tu contacto (opcional)'], 'Lang / Langue': ['Langue', 'Language', 'Idioma', 'Idioma'], 'Koreksyon editoryal': ['Corrections éditoriales', 'Editorial corrections', 'Correções editoriais', 'Correcciones editoriales'], 'Lyen prive sa a pèmèt ou retire abònman ou. Nou pa efase yon abònman jis paske yon navigatè louvri lyen an.': ['Ce lien privé permet de vous désabonner. Ouvrir le lien ne supprime pas votre abonnement.', 'This private link lets you unsubscribe. Opening it does not cancel your subscription.', 'Este link privado permite cancelar sua inscrição. Abrir o link não cancela a inscrição.', 'Este enlace privado permite cancelar tu suscripción. Abrirlo no cancela la suscripción.'], 'Nou ka anrejistre abònman ou kounye a. Premye livrezon an ap fèt lè sèvis imel la konekte.': ['Votre abonnement peut être enregistré. Les envois commenceront une fois le service email connecté.', 'Your subscription can be saved now. Emails will start when the email service is connected.', 'Sua inscrição pode ser salva agora. Os envios começarão quando o serviço de email estiver conectado.', 'Tu suscripción puede guardarse ahora. Los envíos comenzarán cuando se conecte el servicio de correo.'], 'Geovyora se yon magazin dijital ki santre sou kreyatè Ayisyen, dyaspora a ak lòt vwa atravè mond lan. Nou bay kilti, lide ak istwa yo yon espas.': ['Geovyora est un magazine numérique consacré aux créateurs haïtiens, à la diaspora et aux voix du monde. Nous mettons en lumière leur culture, leurs idées et leurs histoires.', 'Geovyora is a digital magazine focused on Haitian creators, the diaspora and voices around the world. We make room for their culture, ideas and stories.', 'Geovyora é uma revista digital dedicada a criadores haitianos, à diáspora e a vozes do mundo. Damos espaço à cultura, às ideias e às histórias deles.', 'Geovyora es una revista digital dedicada a creadores haitianos, la diáspora y voces del mundo. Damos espacio a su cultura, ideas e historias.'], 'Yon medya, yon pwen rankont.': ['Un média, un lieu de rencontre.', 'A publication, a meeting place.', 'Uma revista, um ponto de encontro.', 'Una revista, un punto de encuentro.'], 'Nou pibliye atik, entèvyou ak pwofil editoryal. Lektè yo pa bezwen kreye kont pou li oswa patisipe.': ['Nous publions des articles, entretiens et portraits éditoriaux. Aucun compte n’est nécessaire pour lire ou participer.', 'We publish articles, interviews and editorial profiles. Readers do not need an account to read or participate.', 'Publicamos artigos, entrevistas e perfis editoriais. Não é necessário criar uma conta para ler ou participar.', 'Publicamos artículos, entrevistas y perfiles editoriales. No hace falta crear una cuenta para leer o participar.'], 'Vèsyon sa a gen atik ak pwofil demonstrasyon ki make klèman. Ekip la dwe ranplase yo ak kontni reyèl verifye anvan lansman piblik.': ['Cette version contient des articles et profils de démonstration clairement identifiés. La rédaction doit les remplacer par des contenus réels vérifiés avant le lancement public.', 'This version contains clearly labeled demo articles and profiles. The team must replace them with verified real content before public launch.', 'Esta versão contém artigos e perfis de demonstração identificados. A equipe deve substituí-los por conteúdo real verificado antes do lançamento público.', 'Esta versión contiene artículos y perfiles de demostración identificados. El equipo debe sustituirlos por contenido real verificado antes del lanzamiento público.'], 'Tèks pwovizwa pou premye vèsyon an. Enfòmasyon legal antrepriz la ak kontak responsab la dwe konplete anvan lansman piblik.': ['Texte provisoire. Les informations légales de l’entreprise et les coordonnées du responsable doivent être complétées avant le lancement public.', 'Provisional text. Company legal details and the responsible contact must be completed before public launch.', 'Texto provisório. Os dados legais da empresa e o contato responsável devem ser preenchidos antes do lançamento público.', 'Texto provisional. Los datos legales de la empresa y el contacto responsable deben completarse antes del lanzamiento público.'], 'Ou ka voye yon koreksyon atravè kontak. Koreksyon enpòtan yo dwe dokimante pa ekip la.': ['Envoyez vos corrections via le formulaire de contact. La rédaction doit documenter les corrections importantes.', 'Send corrections through the contact form. The team must document significant corrections.', 'Envie correções pelo formulário de contato. A equipe deve documentar correções importantes.', 'Envía correcciones mediante el formulario de contacto. El equipo debe documentar las correcciones importantes.'], 'Rapò yo pase nan revizyon; kantite rapò pa retire kontni otomatikman.': ['Les signalements sont examinés ; leur nombre ne supprime pas automatiquement le contenu.', 'Reports are reviewed; the number of reports does not automatically remove content.', 'As denúncias são analisadas; sua quantidade não remove o conteúdo automaticamente.', 'Las denuncias se revisan; su cantidad no elimina el contenido automáticamente.'], 'Kòmantè yo pase nan moderasyon anvan piblikasyon. Pa mete menas, rayisman, jouman, enfòmasyon prive oswa spam.': ['Les commentaires sont modérés avant publication. Ne publiez pas de menaces, de haine, d’insultes, d’informations privées ou de spam.', 'Comments are moderated before publication. Do not post threats, hate, abuse, private information or spam.', 'Os comentários são moderados antes da publicação. Não publique ameaças, ódio, ofensas, informações privadas ou spam.', 'Los comentarios se moderan antes de publicarse. No publiques amenazas, odio, insultos, información privada ni spam.'], 'Nou mande sous klè, kredi medya ak revizyon anvan piblikasyon. Opinyon, kontni patwone ak demonstrasyon dwe make.': ['Nous exigeons des sources claires, des crédits médias et une révision avant publication. Les opinions, contenus sponsorisés et démonstrations doivent être identifiés.', 'We require clear sources, media credits and review before publication. Opinions, sponsored content and demos must be labeled.', 'Exigimos fontes claras, créditos de mídia e revisão antes da publicação. Opiniões, conteúdo patrocinado e demonstrações devem ser identificados.', 'Exigimos fuentes claras, créditos de medios y revisión antes de publicar. Las opiniones, el contenido patrocinado y las demostraciones deben identificarse.']})
PHRASES.update({'Ayiti': ['Haïti', 'Haiti', 'Haiti', 'Haití'],
 'Kanada': ['Canada', 'Canada', 'Canadá', 'Canadá'],
 'Lafrans': ['France', 'France', 'França', 'Francia'],
 'Brezil': ['Brésil', 'Brazil', 'Brasil', 'Brasil'],
 'Etazini': ['États-Unis', 'United States', 'Estados Unidos', 'Estados Unidos'],
 'Matinik': ['Martinique', 'Martinique', 'Martinica', 'Martinica'],
 'Dyaspora': ['Diaspora', 'Diaspora', 'Diáspora', 'Diáspora'],
 'Entèvyou': ['Entretiens', 'Interviews', 'Entrevistas', 'Entrevistas'],
 'Mizik': ['Musique', 'Music', 'Música', 'Música'],
 'Kilti': ['Culture', 'Culture', 'Cultura', 'Cultura'],
 'Mond': ['Monde', 'World', 'Mundo', 'Mundo'],
 'Lang': ['Langue', 'Language', 'Idioma', 'Idioma'],
 'Meni': ['Menu', 'Menu', 'Menu', 'Menú'],
 'Chèche lòt lang': ['Autres langues', 'More languages', 'Outros idiomas', 'Otros idiomas'],
 'Chèche yon lang': ['Rechercher une langue', 'Search languages', 'Buscar idioma', 'Buscar idioma'],
 'Chèche yon lang…': ['Rechercher une langue…', 'Search languages…', 'Buscar idioma…', 'Buscar idioma…'],
 'Kilti. Kreyativite. Enpak.': ['Culture. Créativité. Impact.',
                                'Culture. Creativity. Impact.',
                                'Cultura. Criatividade. Impacto.',
                                'Cultura. Creatividad. Impacto.'],
 'Tout dwa rezève.': ['Tous droits réservés.',
                      'All rights reserved.',
                      'Todos os direitos reservados.',
                      'Todos los derechos reservados.'],
 'Ou poko sove atik. Sèvi ak bouton signet sou yon atik.': ['Aucun article enregistré. Utilisez le bouton favori sur '
                                                            'un article.',
                                                            'No saved articles yet. Use the bookmark button on an '
                                                            'article.',
                                                            'Nenhum artigo salvo. Use o botão de favoritos em um '
                                                            'artigo.',
                                                            'Todavía no hay artículos guardados. Usa el botón de '
                                                            'favoritos en un artículo.'],
 'Atik la retire nan lis sove a.': ['Article retiré des favoris.',
                                    'Article removed from saved items.',
                                    'Artigo removido dos favoritos.',
                                    'Artículo eliminado de favoritos.'],
 'Atik la sove sou aparèy sa a.': ['Article enregistré sur cet appareil.',
                                   'Article saved on this device.',
                                   'Artigo salvo neste dispositivo.',
                                   'Artículo guardado en este dispositivo.'],
 'Lyen an kopye.': ['Lien copié.', 'Link copied.', 'Link copiado.', 'Enlace copiado.'],
 'Ap voye…': ['Envoi…', 'Sending…', 'Enviando…', 'Enviando…'],
 'Sèvis la pa disponib. Eseye ankò.': ['Service indisponible. Réessayez.',
                                       'Service unavailable. Try again.',
                                       'Serviço indisponível. Tente novamente.',
                                       'Servicio no disponible. Inténtalo de nuevo.'],
 'Verifye chan yo epi eseye ankò.': ['Vérifiez les champs et réessayez.',
                                     'Check the fields and try again.',
                                     'Verifique os campos e tente novamente.',
                                     'Revisa los campos e inténtalo de nuevo.'],
 'Navigatè a pa pèmèt sove atik.': ['Le navigateur ne permet pas d’enregistrer les articles.',
                                    'Your browser cannot save articles.',
                                    'Seu navegador não permite salvar artigos.',
                                    'Tu navegador no permite guardar artículos.'],
 'Kopye lyen paj la nan ba adrès navigatè a.': ['Copiez le lien depuis la barre d’adresse.',
                                                'Copy the page link from the address bar.',
                                                'Copie o link da barra de endereços.',
                                                'Copia el enlace de la barra de direcciones.'],
 ' Lyen prive dezabònman': [' Lien privé de désabonnement',
                            ' Private unsubscribe link',
                            ' Link privado para cancelar inscrição',
                            ' Enlace privado para cancelar suscripción'],
 'Repons pou': ['Réponse à', 'Reply to', 'Resposta para', 'Respuesta para'],
 'Modifye kòmantè ou a:': ['Modifiez votre commentaire :',
                           'Edit your comment:',
                           'Edite seu comentário:',
                           'Edita tu comentario:'],
 'Retire kòmantè ou a?': ['Supprimer votre commentaire ?',
                          'Remove your comment?',
                          'Remover seu comentário?',
                          '¿Eliminar tu comentario?'],
 'An atant': ['En attente', 'Pending', 'Pendente', 'Pendiente'],
 'Pa apwouve': ['Non approuvé', 'Not approved', 'Não aprovado', 'No aprobado'],
 'Kòmanse konvèsasyon an.': ['Lancez la conversation.',
                             'Start the conversation.',
                             'Comece a conversa.',
                             'Inicia la conversación.'],
 'Kòmantè yo pa disponib.': ['Commentaires indisponibles.',
                             'Comments unavailable.',
                             'Comentários indisponíveis.',
                             'Comentarios no disponibles.'],
 'Lis lang yo pa disponib.': ['Liste des langues indisponible.',
                              'Language list unavailable.',
                              'Lista de idiomas indisponível.',
                              'Lista de idiomas no disponible.'],
 'Chwazi yon foto.': ['Choisissez une photo.', 'Choose a photo.', 'Escolha uma foto.', 'Elige una foto.'],
 'Twa foto maksimòm.': ['Trois photos maximum.', 'Up to three photos.', 'Até três fotos.', 'Hasta tres fotos.'],
 'Foto a depase 10 MB.': ['La photo dépasse 10 Mo.',
                          'Photo exceeds 10 MB.',
                          'A foto excede 10 MB.',
                          'La foto supera los 10 MB.'],
 'Chajman echwe.': ['Échec de l’envoi.', 'Upload failed.', 'Falha no envio.', 'Error al subir.'],
 'foto chaje an prive.': ['photos envoyées en privé.',
                          'photos uploaded privately.',
                          'fotos enviadas em privado.',
                          'fotos subidas en privado.'],
 'Mèsi! Kòmantè ou a ap tann moderasyon.': ['Merci ! Votre commentaire attend la modération.',
                                            'Thank you! Your comment is awaiting moderation.',
                                            'Obrigado! Seu comentário aguarda moderação.',
                                            '¡Gracias! Tu comentario está pendiente de moderación.'],
 'Chanjman an sove.': ['Modification enregistrée.', 'Change saved.', 'Alteração salva.', 'Cambio guardado.'],
 'Rapò ou a voye bay ekip moderasyon an.': ['Signalement envoyé à la modération.',
                                            'Report sent to the moderation team.',
                                            'Denúncia enviada à moderação.',
                                            'Denuncia enviada al equipo de moderación.'],
 'Mèsi! Ekip Geovyora resevwa mesaj ou a.': ['Merci ! L’équipe Geovyora a reçu votre message.',
                                             'Thank you! The Geovyora team received your message.',
                                             'Obrigado! A equipe Geovyora recebeu sua mensagem.',
                                             '¡Gracias! El equipo Geovyora recibió tu mensaje.'],
 'Abònman an aktive sou navigatè sa a.': ['Abonnement activé dans ce navigateur.',
                                          'Subscription enabled in this browser.',
                                          'Inscrição ativada neste navegador.',
                                          'Suscripción activada en este navegador.'],
 'Notifikasyon aktive sou navigatè sa a.': ['Notifications activées dans ce navigateur.',
                                            'Notifications enabled in this browser.',
                                            'Notificações ativadas neste navegador.',
                                            'Notificaciones activadas en este navegador.'],
 'Ou dezabòne.': ['Vous êtes désabonné.', 'You are unsubscribed.', 'Inscrição cancelada.', 'Suscripción cancelada.'],
 'Ou pa bay pèmisyon pou notifikasyon.': ['Permission de notification refusée.',
                                          'Notification permission was not granted.',
                                          'Permissão de notificações não concedida.',
                                          'No se concedió permiso para notificaciones.']})
PHRASES.update({'Cookie fonksyonèl yo sèvi pou sesyon admin, preferans lang, dwa kòmantè ak sekirite. Yo pa sèvi pou konstwi yon pwofil piblisite.': ['Les '
                                                                                                                                       'cookies '
                                                                                                                                       'fonctionnels '
                                                                                                                                       'servent '
                                                                                                                                       'aux '
                                                                                                                                       'sessions '
                                                                                                                                       'administrateur, '
                                                                                                                                       'à '
                                                                                                                                       'la '
                                                                                                                                       'langue, '
                                                                                                                                       'aux '
                                                                                                                                       'droits '
                                                                                                                                       'sur '
                                                                                                                                       'les '
                                                                                                                                       'commentaires '
                                                                                                                                       'et '
                                                                                                                                       'à '
                                                                                                                                       'la '
                                                                                                                                       'sécurité. '
                                                                                                                                       'Ils '
                                                                                                                                       'ne '
                                                                                                                                       'servent '
                                                                                                                                       'pas '
                                                                                                                                       'à '
                                                                                                                                       'créer '
                                                                                                                                       'un '
                                                                                                                                       'profil '
                                                                                                                                       'publicitaire.',
                                                                                                                                       'Functional '
                                                                                                                                       'cookies '
                                                                                                                                       'support '
                                                                                                                                       'admin '
                                                                                                                                       'sessions, '
                                                                                                                                       'language '
                                                                                                                                       'preferences, '
                                                                                                                                       'comment '
                                                                                                                                       'permissions '
                                                                                                                                       'and '
                                                                                                                                       'security. '
                                                                                                                                       'They '
                                                                                                                                       'are '
                                                                                                                                       'not '
                                                                                                                                       'used '
                                                                                                                                       'to '
                                                                                                                                       'build '
                                                                                                                                       'advertising '
                                                                                                                                       'profiles.',
                                                                                                                                       'Cookies '
                                                                                                                                       'funcionais '
                                                                                                                                       'servem '
                                                                                                                                       'para '
                                                                                                                                       'sessões '
                                                                                                                                       'administrativas, '
                                                                                                                                       'preferências '
                                                                                                                                       'de '
                                                                                                                                       'idioma, '
                                                                                                                                       'permissões '
                                                                                                                                       'de '
                                                                                                                                       'comentários '
                                                                                                                                       'e '
                                                                                                                                       'segurança. '
                                                                                                                                       'Não '
                                                                                                                                       'são '
                                                                                                                                       'usados '
                                                                                                                                       'para '
                                                                                                                                       'criar '
                                                                                                                                       'perfis '
                                                                                                                                       'publicitários.',
                                                                                                                                       'Las '
                                                                                                                                       'cookies '
                                                                                                                                       'funcionales '
                                                                                                                                       'sirven '
                                                                                                                                       'para '
                                                                                                                                       'sesiones '
                                                                                                                                       'administrativas, '
                                                                                                                                       'idioma, '
                                                                                                                                       'permisos '
                                                                                                                                       'de '
                                                                                                                                       'comentarios '
                                                                                                                                       'y '
                                                                                                                                       'seguridad. '
                                                                                                                                       'No '
                                                                                                                                       'se '
                                                                                                                                       'usan '
                                                                                                                                       'para '
                                                                                                                                       'crear '
                                                                                                                                       'perfiles '
                                                                                                                                       'publicitarios.'],
 'Kontni demonstrasyon ak tradiksyon otomatik pa dwe itilize tankou enfòmasyon verifye. Ekip la responsab revizyon kontni anvan lansman.': ['Les '
                                                                                                                                            'démonstrations '
                                                                                                                                            'et '
                                                                                                                                            'traductions '
                                                                                                                                            'automatiques '
                                                                                                                                            'ne '
                                                                                                                                            'doivent '
                                                                                                                                            'pas '
                                                                                                                                            'être '
                                                                                                                                            'considérées '
                                                                                                                                            'comme '
                                                                                                                                            'des '
                                                                                                                                            'informations '
                                                                                                                                            'vérifiées. '
                                                                                                                                            'La '
                                                                                                                                            'rédaction '
                                                                                                                                            'est '
                                                                                                                                            'responsable '
                                                                                                                                            'de '
                                                                                                                                            'la '
                                                                                                                                            'révision '
                                                                                                                                            'du '
                                                                                                                                            'contenu '
                                                                                                                                            'avant '
                                                                                                                                            'le '
                                                                                                                                            'lancement.',
                                                                                                                                            'Demo '
                                                                                                                                            'content '
                                                                                                                                            'and '
                                                                                                                                            'automatic '
                                                                                                                                            'translations '
                                                                                                                                            'must '
                                                                                                                                            'not '
                                                                                                                                            'be '
                                                                                                                                            'treated '
                                                                                                                                            'as '
                                                                                                                                            'verified '
                                                                                                                                            'information. '
                                                                                                                                            'The '
                                                                                                                                            'team '
                                                                                                                                            'is '
                                                                                                                                            'responsible '
                                                                                                                                            'for '
                                                                                                                                            'reviewing '
                                                                                                                                            'content '
                                                                                                                                            'before '
                                                                                                                                            'launch.',
                                                                                                                                            'Conteúdo '
                                                                                                                                            'de '
                                                                                                                                            'demonstração '
                                                                                                                                            'e '
                                                                                                                                            'traduções '
                                                                                                                                            'automáticas '
                                                                                                                                            'não '
                                                                                                                                            'devem '
                                                                                                                                            'ser '
                                                                                                                                            'tratados '
                                                                                                                                            'como '
                                                                                                                                            'informação '
                                                                                                                                            'verificada. '
                                                                                                                                            'A '
                                                                                                                                            'equipe '
                                                                                                                                            'deve '
                                                                                                                                            'revisar '
                                                                                                                                            'o '
                                                                                                                                            'conteúdo '
                                                                                                                                            'antes '
                                                                                                                                            'do '
                                                                                                                                            'lançamento.',
                                                                                                                                            'El '
                                                                                                                                            'contenido '
                                                                                                                                            'de '
                                                                                                                                            'demostración '
                                                                                                                                            'y '
                                                                                                                                            'las '
                                                                                                                                            'traducciones '
                                                                                                                                            'automáticas '
                                                                                                                                            'no '
                                                                                                                                            'deben '
                                                                                                                                            'tratarse '
                                                                                                                                            'como '
                                                                                                                                            'información '
                                                                                                                                            'verificada. '
                                                                                                                                            'El '
                                                                                                                                            'equipo '
                                                                                                                                            'debe '
                                                                                                                                            'revisar '
                                                                                                                                            'el '
                                                                                                                                            'contenido '
                                                                                                                                            'antes '
                                                                                                                                            'del '
                                                                                                                                            'lanzamiento.'],
 'Mesaj kontak ak sous ou voye yo rete nan administrasyon an. Si ou abòne ak push, token navigatè ou ak sijè ou chwazi yo sove. Atik sove ak lang rete sou aparèy ou.': ['Vos '
                                                                                                                                                                         'messages '
                                                                                                                                                                         'de '
                                                                                                                                                                         'contact '
                                                                                                                                                                         'et '
                                                                                                                                                                         'sources '
                                                                                                                                                                         'restent '
                                                                                                                                                                         'dans '
                                                                                                                                                                         'l’administration. '
                                                                                                                                                                         'En '
                                                                                                                                                                         'cas '
                                                                                                                                                                         'd’abonnement '
                                                                                                                                                                         'push, '
                                                                                                                                                                         'le '
                                                                                                                                                                         'jeton '
                                                                                                                                                                         'du '
                                                                                                                                                                         'navigateur '
                                                                                                                                                                         'et '
                                                                                                                                                                         'les '
                                                                                                                                                                         'sujets '
                                                                                                                                                                         'choisis '
                                                                                                                                                                         'sont '
                                                                                                                                                                         'enregistrés. '
                                                                                                                                                                         'Les '
                                                                                                                                                                         'favoris '
                                                                                                                                                                         'et '
                                                                                                                                                                         'la '
                                                                                                                                                                         'langue '
                                                                                                                                                                         'restent '
                                                                                                                                                                         'sur '
                                                                                                                                                                         'votre '
                                                                                                                                                                         'appareil.',
                                                                                                                                                                         'Contact '
                                                                                                                                                                         'messages '
                                                                                                                                                                         'and '
                                                                                                                                                                         'submitted '
                                                                                                                                                                         'sources '
                                                                                                                                                                         'remain '
                                                                                                                                                                         'in '
                                                                                                                                                                         'the '
                                                                                                                                                                         'administration '
                                                                                                                                                                         'area. '
                                                                                                                                                                         'If '
                                                                                                                                                                         'you '
                                                                                                                                                                         'subscribe '
                                                                                                                                                                         'to '
                                                                                                                                                                         'push, '
                                                                                                                                                                         'your '
                                                                                                                                                                         'browser '
                                                                                                                                                                         'token '
                                                                                                                                                                         'and '
                                                                                                                                                                         'selected '
                                                                                                                                                                         'topics '
                                                                                                                                                                         'are '
                                                                                                                                                                         'stored. '
                                                                                                                                                                         'Saved '
                                                                                                                                                                         'articles '
                                                                                                                                                                         'and '
                                                                                                                                                                         'language '
                                                                                                                                                                         'preferences '
                                                                                                                                                                         'remain '
                                                                                                                                                                         'on '
                                                                                                                                                                         'your '
                                                                                                                                                                         'device.',
                                                                                                                                                                         'Mensagens '
                                                                                                                                                                         'de '
                                                                                                                                                                         'contato '
                                                                                                                                                                         'e '
                                                                                                                                                                         'fontes '
                                                                                                                                                                         'enviadas '
                                                                                                                                                                         'ficam '
                                                                                                                                                                         'na '
                                                                                                                                                                         'administração. '
                                                                                                                                                                         'Ao '
                                                                                                                                                                         'assinar '
                                                                                                                                                                         'notificações '
                                                                                                                                                                         'push, '
                                                                                                                                                                         'o '
                                                                                                                                                                         'token '
                                                                                                                                                                         'do '
                                                                                                                                                                         'navegador '
                                                                                                                                                                         'e '
                                                                                                                                                                         'os '
                                                                                                                                                                         'temas '
                                                                                                                                                                         'escolhidos '
                                                                                                                                                                         'são '
                                                                                                                                                                         'salvos. '
                                                                                                                                                                         'Artigos '
                                                                                                                                                                         'salvos '
                                                                                                                                                                         'e '
                                                                                                                                                                         'idioma '
                                                                                                                                                                         'ficam '
                                                                                                                                                                         'no '
                                                                                                                                                                         'seu '
                                                                                                                                                                         'dispositivo.',
                                                                                                                                                                         'Los '
                                                                                                                                                                         'mensajes '
                                                                                                                                                                         'de '
                                                                                                                                                                         'contacto '
                                                                                                                                                                         'y '
                                                                                                                                                                         'fuentes '
                                                                                                                                                                         'enviadas '
                                                                                                                                                                         'quedan '
                                                                                                                                                                         'en '
                                                                                                                                                                         'la '
                                                                                                                                                                         'administración. '
                                                                                                                                                                         'Si '
                                                                                                                                                                         'te '
                                                                                                                                                                         'suscribes '
                                                                                                                                                                         'a '
                                                                                                                                                                         'push, '
                                                                                                                                                                         'se '
                                                                                                                                                                         'guardan '
                                                                                                                                                                         'el '
                                                                                                                                                                         'token '
                                                                                                                                                                         'del '
                                                                                                                                                                         'navegador '
                                                                                                                                                                         'y '
                                                                                                                                                                         'los '
                                                                                                                                                                         'temas '
                                                                                                                                                                         'elegidos. '
                                                                                                                                                                         'Los '
                                                                                                                                                                         'artículos '
                                                                                                                                                                         'guardados '
                                                                                                                                                                         'y '
                                                                                                                                                                         'el '
                                                                                                                                                                         'idioma '
                                                                                                                                                                         'quedan '
                                                                                                                                                                         'en '
                                                                                                                                                                         'tu '
                                                                                                                                                                         'dispositivo.'],
 'Nou dwe gen dwa itilize foto, videyo ak tèks nou pibliye yo. Pou mande yon retrè, voye lyen kontni an, rezon demann lan ak prèv dwa ou atravè fòm kontak la.': ['Nous '
                                                                                                                                                                  'devons '
                                                                                                                                                                  'disposer '
                                                                                                                                                                  'des '
                                                                                                                                                                  'droits '
                                                                                                                                                                  'nécessaires '
                                                                                                                                                                  'pour '
                                                                                                                                                                  'publier '
                                                                                                                                                                  'photos, '
                                                                                                                                                                  'vidéos '
                                                                                                                                                                  'et '
                                                                                                                                                                  'textes. '
                                                                                                                                                                  'Pour '
                                                                                                                                                                  'demander '
                                                                                                                                                                  'un '
                                                                                                                                                                  'retrait, '
                                                                                                                                                                  'envoyez '
                                                                                                                                                                  'le '
                                                                                                                                                                  'lien '
                                                                                                                                                                  'du '
                                                                                                                                                                  'contenu, '
                                                                                                                                                                  'le '
                                                                                                                                                                  'motif '
                                                                                                                                                                  'et '
                                                                                                                                                                  'une '
                                                                                                                                                                  'preuve '
                                                                                                                                                                  'de '
                                                                                                                                                                  'vos '
                                                                                                                                                                  'droits '
                                                                                                                                                                  'via '
                                                                                                                                                                  'le '
                                                                                                                                                                  'formulaire '
                                                                                                                                                                  'de '
                                                                                                                                                                  'contact.',
                                                                                                                                                                  'We '
                                                                                                                                                                  'must '
                                                                                                                                                                  'have '
                                                                                                                                                                  'the '
                                                                                                                                                                  'rights '
                                                                                                                                                                  'to '
                                                                                                                                                                  'use '
                                                                                                                                                                  'the '
                                                                                                                                                                  'photos, '
                                                                                                                                                                  'videos '
                                                                                                                                                                  'and '
                                                                                                                                                                  'text '
                                                                                                                                                                  'we '
                                                                                                                                                                  'publish. '
                                                                                                                                                                  'To '
                                                                                                                                                                  'request '
                                                                                                                                                                  'removal, '
                                                                                                                                                                  'send '
                                                                                                                                                                  'the '
                                                                                                                                                                  'content '
                                                                                                                                                                  'link, '
                                                                                                                                                                  'the '
                                                                                                                                                                  'reason '
                                                                                                                                                                  'and '
                                                                                                                                                                  'evidence '
                                                                                                                                                                  'of '
                                                                                                                                                                  'your '
                                                                                                                                                                  'rights '
                                                                                                                                                                  'through '
                                                                                                                                                                  'the '
                                                                                                                                                                  'contact '
                                                                                                                                                                  'form.',
                                                                                                                                                                  'Precisamos '
                                                                                                                                                                  'ter '
                                                                                                                                                                  'os '
                                                                                                                                                                  'direitos '
                                                                                                                                                                  'de '
                                                                                                                                                                  'uso '
                                                                                                                                                                  'das '
                                                                                                                                                                  'fotos, '
                                                                                                                                                                  'vídeos '
                                                                                                                                                                  'e '
                                                                                                                                                                  'textos '
                                                                                                                                                                  'publicados. '
                                                                                                                                                                  'Para '
                                                                                                                                                                  'pedir '
                                                                                                                                                                  'remoção, '
                                                                                                                                                                  'envie '
                                                                                                                                                                  'o '
                                                                                                                                                                  'link '
                                                                                                                                                                  'do '
                                                                                                                                                                  'conteúdo, '
                                                                                                                                                                  'o '
                                                                                                                                                                  'motivo '
                                                                                                                                                                  'e '
                                                                                                                                                                  'provas '
                                                                                                                                                                  'dos '
                                                                                                                                                                  'seus '
                                                                                                                                                                  'direitos '
                                                                                                                                                                  'pelo '
                                                                                                                                                                  'formulário '
                                                                                                                                                                  'de '
                                                                                                                                                                  'contato.',
                                                                                                                                                                  'Debemos '
                                                                                                                                                                  'tener '
                                                                                                                                                                  'derechos '
                                                                                                                                                                  'para '
                                                                                                                                                                  'usar '
                                                                                                                                                                  'las '
                                                                                                                                                                  'fotos, '
                                                                                                                                                                  'vídeos '
                                                                                                                                                                  'y '
                                                                                                                                                                  'textos '
                                                                                                                                                                  'publicados. '
                                                                                                                                                                  'Para '
                                                                                                                                                                  'solicitar '
                                                                                                                                                                  'una '
                                                                                                                                                                  'retirada, '
                                                                                                                                                                  'envía '
                                                                                                                                                                  'el '
                                                                                                                                                                  'enlace, '
                                                                                                                                                                  'el '
                                                                                                                                                                  'motivo '
                                                                                                                                                                  'y '
                                                                                                                                                                  'pruebas '
                                                                                                                                                                  'de '
                                                                                                                                                                  'tus '
                                                                                                                                                                  'derechos '
                                                                                                                                                                  'mediante '
                                                                                                                                                                  'el '
                                                                                                                                                                  'formulario '
                                                                                                                                                                  'de '
                                                                                                                                                                  'contacto.'],
 'Nou pa envante estatistik rezo sosyal. Chif verifye bezwen yon sous ak yon dat. Tandans sou sit la baze sou lekti sou Geovyora sèlman.': ['Nous '
                                                                                                                                            'n’inventons '
                                                                                                                                            'pas '
                                                                                                                                            'de '
                                                                                                                                            'statistiques '
                                                                                                                                            'sociales. '
                                                                                                                                            'Les '
                                                                                                                                            'chiffres '
                                                                                                                                            'vérifiés '
                                                                                                                                            'nécessitent '
                                                                                                                                            'une '
                                                                                                                                            'source '
                                                                                                                                            'et '
                                                                                                                                            'une '
                                                                                                                                            'date. '
                                                                                                                                            'Les '
                                                                                                                                            'tendances '
                                                                                                                                            'du '
                                                                                                                                            'site '
                                                                                                                                            'reposent '
                                                                                                                                            'uniquement '
                                                                                                                                            'sur '
                                                                                                                                            'les '
                                                                                                                                            'lectures '
                                                                                                                                            'sur '
                                                                                                                                            'Geovyora.',
                                                                                                                                            'We '
                                                                                                                                            'do '
                                                                                                                                            'not '
                                                                                                                                            'invent '
                                                                                                                                            'social '
                                                                                                                                            'media '
                                                                                                                                            'statistics. '
                                                                                                                                            'Verified '
                                                                                                                                            'figures '
                                                                                                                                            'require '
                                                                                                                                            'a '
                                                                                                                                            'source '
                                                                                                                                            'and '
                                                                                                                                            'date. '
                                                                                                                                            'Site '
                                                                                                                                            'trends '
                                                                                                                                            'are '
                                                                                                                                            'based '
                                                                                                                                            'only '
                                                                                                                                            'on '
                                                                                                                                            'reads '
                                                                                                                                            'on '
                                                                                                                                            'Geovyora.',
                                                                                                                                            'Não '
                                                                                                                                            'inventamos '
                                                                                                                                            'estatísticas '
                                                                                                                                            'de '
                                                                                                                                            'redes '
                                                                                                                                            'sociais. '
                                                                                                                                            'Números '
                                                                                                                                            'verificados '
                                                                                                                                            'precisam '
                                                                                                                                            'de '
                                                                                                                                            'fonte '
                                                                                                                                            'e '
                                                                                                                                            'data. '
                                                                                                                                            'Tendências '
                                                                                                                                            'do '
                                                                                                                                            'site '
                                                                                                                                            'são '
                                                                                                                                            'baseadas '
                                                                                                                                            'apenas '
                                                                                                                                            'nas '
                                                                                                                                            'leituras '
                                                                                                                                            'no '
                                                                                                                                            'Geovyora.',
                                                                                                                                            'No '
                                                                                                                                            'inventamos '
                                                                                                                                            'estadísticas '
                                                                                                                                            'de '
                                                                                                                                            'redes '
                                                                                                                                            'sociales. '
                                                                                                                                            'Las '
                                                                                                                                            'cifras '
                                                                                                                                            'verificadas '
                                                                                                                                            'necesitan '
                                                                                                                                            'fuente '
                                                                                                                                            'y '
                                                                                                                                            'fecha. '
                                                                                                                                            'Las '
                                                                                                                                            'tendencias '
                                                                                                                                            'del '
                                                                                                                                            'sitio '
                                                                                                                                            'se '
                                                                                                                                            'basan '
                                                                                                                                            'únicamente '
                                                                                                                                            'en '
                                                                                                                                            'lecturas '
                                                                                                                                            'en '
                                                                                                                                            'Geovyora.'],
 'Pa voye enfòmasyon sansib nan kòmantè. Pou retire done oswa kontni, itilize fòm kontak la. Enfòmasyon antrepriz ak delè konsèvasyon dwe konplete anvan lansman.': ['Ne '
                                                                                                                                                                     'publiez '
                                                                                                                                                                     'pas '
                                                                                                                                                                     'de '
                                                                                                                                                                     'données '
                                                                                                                                                                     'sensibles '
                                                                                                                                                                     'dans '
                                                                                                                                                                     'les '
                                                                                                                                                                     'commentaires. '
                                                                                                                                                                     'Utilisez '
                                                                                                                                                                     'le '
                                                                                                                                                                     'formulaire '
                                                                                                                                                                     'de '
                                                                                                                                                                     'contact '
                                                                                                                                                                     'pour '
                                                                                                                                                                     'demander '
                                                                                                                                                                     'une '
                                                                                                                                                                     'suppression. '
                                                                                                                                                                     'Les '
                                                                                                                                                                     'informations '
                                                                                                                                                                     'de '
                                                                                                                                                                     'l’entreprise '
                                                                                                                                                                     'et '
                                                                                                                                                                     'les '
                                                                                                                                                                     'durées '
                                                                                                                                                                     'de '
                                                                                                                                                                     'conservation '
                                                                                                                                                                     'doivent '
                                                                                                                                                                     'être '
                                                                                                                                                                     'complétées '
                                                                                                                                                                     'avant '
                                                                                                                                                                     'le '
                                                                                                                                                                     'lancement.',
                                                                                                                                                                     'Do '
                                                                                                                                                                     'not '
                                                                                                                                                                     'post '
                                                                                                                                                                     'sensitive '
                                                                                                                                                                     'information '
                                                                                                                                                                     'in '
                                                                                                                                                                     'comments. '
                                                                                                                                                                     'Use '
                                                                                                                                                                     'the '
                                                                                                                                                                     'contact '
                                                                                                                                                                     'form '
                                                                                                                                                                     'to '
                                                                                                                                                                     'request '
                                                                                                                                                                     'removal '
                                                                                                                                                                     'of '
                                                                                                                                                                     'data '
                                                                                                                                                                     'or '
                                                                                                                                                                     'content. '
                                                                                                                                                                     'Company '
                                                                                                                                                                     'details '
                                                                                                                                                                     'and '
                                                                                                                                                                     'retention '
                                                                                                                                                                     'periods '
                                                                                                                                                                     'must '
                                                                                                                                                                     'be '
                                                                                                                                                                     'completed '
                                                                                                                                                                     'before '
                                                                                                                                                                     'launch.',
                                                                                                                                                                     'Não '
                                                                                                                                                                     'publique '
                                                                                                                                                                     'dados '
                                                                                                                                                                     'sensíveis '
                                                                                                                                                                     'nos '
                                                                                                                                                                     'comentários. '
                                                                                                                                                                     'Use '
                                                                                                                                                                     'o '
                                                                                                                                                                     'formulário '
                                                                                                                                                                     'de '
                                                                                                                                                                     'contato '
                                                                                                                                                                     'para '
                                                                                                                                                                     'pedir '
                                                                                                                                                                     'a '
                                                                                                                                                                     'remoção '
                                                                                                                                                                     'de '
                                                                                                                                                                     'dados '
                                                                                                                                                                     'ou '
                                                                                                                                                                     'conteúdo. '
                                                                                                                                                                     'Dados '
                                                                                                                                                                     'da '
                                                                                                                                                                     'empresa '
                                                                                                                                                                     'e '
                                                                                                                                                                     'prazos '
                                                                                                                                                                     'de '
                                                                                                                                                                     'retenção '
                                                                                                                                                                     'devem '
                                                                                                                                                                     'ser '
                                                                                                                                                                     'preenchidos '
                                                                                                                                                                     'antes '
                                                                                                                                                                     'do '
                                                                                                                                                                     'lançamento.',
                                                                                                                                                                     'No '
                                                                                                                                                                     'publiques '
                                                                                                                                                                     'información '
                                                                                                                                                                     'sensible '
                                                                                                                                                                     'en '
                                                                                                                                                                     'comentarios. '
                                                                                                                                                                     'Usa '
                                                                                                                                                                     'el '
                                                                                                                                                                     'formulario '
                                                                                                                                                                     'de '
                                                                                                                                                                     'contacto '
                                                                                                                                                                     'para '
                                                                                                                                                                     'solicitar '
                                                                                                                                                                     'la '
                                                                                                                                                                     'eliminación '
                                                                                                                                                                     'de '
                                                                                                                                                                     'datos '
                                                                                                                                                                     'o '
                                                                                                                                                                     'contenido. '
                                                                                                                                                                     'Los '
                                                                                                                                                                     'datos '
                                                                                                                                                                     'de '
                                                                                                                                                                     'la '
                                                                                                                                                                     'empresa '
                                                                                                                                                                     'y '
                                                                                                                                                                     'plazos '
                                                                                                                                                                     'de '
                                                                                                                                                                     'conservación '
                                                                                                                                                                     'deben '
                                                                                                                                                                     'completarse '
                                                                                                                                                                     'antes '
                                                                                                                                                                     'del '
                                                                                                                                                                     'lanzamiento.'],
 'Piblisite ak tracking opsyonèl yo dezaktive pa default. Yon jesyon konsantman apwopriye dwe konekte anvan aktivasyon.': ['La '
                                                                                                                           'publicité '
                                                                                                                           'et '
                                                                                                                           'le '
                                                                                                                           'suivi '
                                                                                                                           'facultatif '
                                                                                                                           'sont '
                                                                                                                           'désactivés '
                                                                                                                           'par '
                                                                                                                           'défaut. '
                                                                                                                           'Un '
                                                                                                                           'système '
                                                                                                                           'de '
                                                                                                                           'gestion '
                                                                                                                           'du '
                                                                                                                           'consentement '
                                                                                                                           'approprié '
                                                                                                                           'doit '
                                                                                                                           'être '
                                                                                                                           'connecté '
                                                                                                                           'avant '
                                                                                                                           'leur '
                                                                                                                           'activation.',
                                                                                                                           'Advertising '
                                                                                                                           'and '
                                                                                                                           'optional '
                                                                                                                           'tracking '
                                                                                                                           'are '
                                                                                                                           'disabled '
                                                                                                                           'by '
                                                                                                                           'default. '
                                                                                                                           'Appropriate '
                                                                                                                           'consent '
                                                                                                                           'management '
                                                                                                                           'must '
                                                                                                                           'be '
                                                                                                                           'connected '
                                                                                                                           'before '
                                                                                                                           'activation.',
                                                                                                                           'Publicidade '
                                                                                                                           'e '
                                                                                                                           'rastreamento '
                                                                                                                           'opcional '
                                                                                                                           'estão '
                                                                                                                           'desativados '
                                                                                                                           'por '
                                                                                                                           'padrão. '
                                                                                                                           'Um '
                                                                                                                           'sistema '
                                                                                                                           'adequado '
                                                                                                                           'de '
                                                                                                                           'gestão '
                                                                                                                           'de '
                                                                                                                           'consentimento '
                                                                                                                           'deve '
                                                                                                                           'ser '
                                                                                                                           'conectado '
                                                                                                                           'antes '
                                                                                                                           'da '
                                                                                                                           'ativação.',
                                                                                                                           'La '
                                                                                                                           'publicidad '
                                                                                                                           'y '
                                                                                                                           'el '
                                                                                                                           'seguimiento '
                                                                                                                           'opcional '
                                                                                                                           'están '
                                                                                                                           'desactivados '
                                                                                                                           'por '
                                                                                                                           'defecto. '
                                                                                                                           'Debe '
                                                                                                                           'conectarse '
                                                                                                                           'una '
                                                                                                                           'gestión '
                                                                                                                           'adecuada '
                                                                                                                           'del '
                                                                                                                           'consentimiento '
                                                                                                                           'antes '
                                                                                                                           'de '
                                                                                                                           'activarlos.'],
 'Pseudo yo pa idantite verifye. Ou ka modifye oswa retire kòmantè ou sèlman sou navigatè kote ou te ekri li a, si cookie ou toujou disponib.': ['Les '
                                                                                                                                                 'pseudos '
                                                                                                                                                 'ne '
                                                                                                                                                 'sont '
                                                                                                                                                 'pas '
                                                                                                                                                 'des '
                                                                                                                                                 'identités '
                                                                                                                                                 'vérifiées. '
                                                                                                                                                 'Vous '
                                                                                                                                                 'pouvez '
                                                                                                                                                 'modifier '
                                                                                                                                                 'ou '
                                                                                                                                                 'supprimer '
                                                                                                                                                 'votre '
                                                                                                                                                 'commentaire '
                                                                                                                                                 'uniquement '
                                                                                                                                                 'dans '
                                                                                                                                                 'le '
                                                                                                                                                 'navigateur '
                                                                                                                                                 'utilisé '
                                                                                                                                                 'pour '
                                                                                                                                                 'le '
                                                                                                                                                 'publier, '
                                                                                                                                                 'tant '
                                                                                                                                                 'que '
                                                                                                                                                 'son '
                                                                                                                                                 'cookie '
                                                                                                                                                 'est '
                                                                                                                                                 'disponible.',
                                                                                                                                                 'Usernames '
                                                                                                                                                 'are '
                                                                                                                                                 'not '
                                                                                                                                                 'verified '
                                                                                                                                                 'identities. '
                                                                                                                                                 'You '
                                                                                                                                                 'can '
                                                                                                                                                 'edit '
                                                                                                                                                 'or '
                                                                                                                                                 'remove '
                                                                                                                                                 'your '
                                                                                                                                                 'comments '
                                                                                                                                                 'only '
                                                                                                                                                 'in '
                                                                                                                                                 'the '
                                                                                                                                                 'browser '
                                                                                                                                                 'where '
                                                                                                                                                 'you '
                                                                                                                                                 'posted '
                                                                                                                                                 'them, '
                                                                                                                                                 'while '
                                                                                                                                                 'your '
                                                                                                                                                 'cookie '
                                                                                                                                                 'remains '
                                                                                                                                                 'available.',
                                                                                                                                                 'Pseudônimos '
                                                                                                                                                 'não '
                                                                                                                                                 'são '
                                                                                                                                                 'identidades '
                                                                                                                                                 'verificadas. '
                                                                                                                                                 'Você '
                                                                                                                                                 'só '
                                                                                                                                                 'pode '
                                                                                                                                                 'editar '
                                                                                                                                                 'ou '
                                                                                                                                                 'remover '
                                                                                                                                                 'seus '
                                                                                                                                                 'comentários '
                                                                                                                                                 'no '
                                                                                                                                                 'navegador '
                                                                                                                                                 'onde '
                                                                                                                                                 'os '
                                                                                                                                                 'publicou, '
                                                                                                                                                 'enquanto '
                                                                                                                                                 'o '
                                                                                                                                                 'cookie '
                                                                                                                                                 'estiver '
                                                                                                                                                 'disponível.',
                                                                                                                                                 'Los '
                                                                                                                                                 'seudónimos '
                                                                                                                                                 'no '
                                                                                                                                                 'son '
                                                                                                                                                 'identidades '
                                                                                                                                                 'verificadas. '
                                                                                                                                                 'Solo '
                                                                                                                                                 'puedes '
                                                                                                                                                 'editar '
                                                                                                                                                 'o '
                                                                                                                                                 'eliminar '
                                                                                                                                                 'tus '
                                                                                                                                                 'comentarios '
                                                                                                                                                 'en '
                                                                                                                                                 'el '
                                                                                                                                                 'navegador '
                                                                                                                                                 'donde '
                                                                                                                                                 'los '
                                                                                                                                                 'publicaste, '
                                                                                                                                                 'mientras '
                                                                                                                                                 'la '
                                                                                                                                                 'cookie '
                                                                                                                                                 'siga '
                                                                                                                                                 'disponible.'],
 'Sit la sèvi ak yon cookie o aza pou idantifye navigatè ou, pwoteje demann, jere kòmantè ak limite abi. Non/pseudo kòmantè ou se piblik apre moderasyon; idantifyan prive ou pa piblik.': ['Le '
                                                                                                                                                                                            'site '
                                                                                                                                                                                            'utilise '
                                                                                                                                                                                            'un '
                                                                                                                                                                                            'cookie '
                                                                                                                                                                                            'aléatoire '
                                                                                                                                                                                            'pour '
                                                                                                                                                                                            'reconnaître '
                                                                                                                                                                                            'votre '
                                                                                                                                                                                            'navigateur, '
                                                                                                                                                                                            'protéger '
                                                                                                                                                                                            'les '
                                                                                                                                                                                            'requêtes, '
                                                                                                                                                                                            'gérer '
                                                                                                                                                                                            'les '
                                                                                                                                                                                            'commentaires '
                                                                                                                                                                                            'et '
                                                                                                                                                                                            'limiter '
                                                                                                                                                                                            'les '
                                                                                                                                                                                            'abus. '
                                                                                                                                                                                            'Votre '
                                                                                                                                                                                            'nom '
                                                                                                                                                                                            'ou '
                                                                                                                                                                                            'pseudo '
                                                                                                                                                                                            'est '
                                                                                                                                                                                            'public '
                                                                                                                                                                                            'après '
                                                                                                                                                                                            'modération '
                                                                                                                                                                                            '; '
                                                                                                                                                                                            'votre '
                                                                                                                                                                                            'identifiant '
                                                                                                                                                                                            'privé '
                                                                                                                                                                                            'reste '
                                                                                                                                                                                            'confidentiel.',
                                                                                                                                                                                            'The '
                                                                                                                                                                                            'site '
                                                                                                                                                                                            'uses '
                                                                                                                                                                                            'a '
                                                                                                                                                                                            'random '
                                                                                                                                                                                            'cookie '
                                                                                                                                                                                            'to '
                                                                                                                                                                                            'identify '
                                                                                                                                                                                            'your '
                                                                                                                                                                                            'browser, '
                                                                                                                                                                                            'protect '
                                                                                                                                                                                            'requests, '
                                                                                                                                                                                            'manage '
                                                                                                                                                                                            'comments '
                                                                                                                                                                                            'and '
                                                                                                                                                                                            'limit '
                                                                                                                                                                                            'abuse. '
                                                                                                                                                                                            'Your '
                                                                                                                                                                                            'comment '
                                                                                                                                                                                            'name '
                                                                                                                                                                                            'is '
                                                                                                                                                                                            'public '
                                                                                                                                                                                            'after '
                                                                                                                                                                                            'moderation; '
                                                                                                                                                                                            'your '
                                                                                                                                                                                            'private '
                                                                                                                                                                                            'identifier '
                                                                                                                                                                                            'is '
                                                                                                                                                                                            'not '
                                                                                                                                                                                            'public.',
                                                                                                                                                                                            'O '
                                                                                                                                                                                            'site '
                                                                                                                                                                                            'usa '
                                                                                                                                                                                            'um '
                                                                                                                                                                                            'cookie '
                                                                                                                                                                                            'aleatório '
                                                                                                                                                                                            'para '
                                                                                                                                                                                            'identificar '
                                                                                                                                                                                            'seu '
                                                                                                                                                                                            'navegador, '
                                                                                                                                                                                            'proteger '
                                                                                                                                                                                            'solicitações, '
                                                                                                                                                                                            'gerenciar '
                                                                                                                                                                                            'comentários '
                                                                                                                                                                                            'e '
                                                                                                                                                                                            'limitar '
                                                                                                                                                                                            'abusos. '
                                                                                                                                                                                            'Seu '
                                                                                                                                                                                            'nome '
                                                                                                                                                                                            'fica '
                                                                                                                                                                                            'público '
                                                                                                                                                                                            'após '
                                                                                                                                                                                            'moderação; '
                                                                                                                                                                                            'seu '
                                                                                                                                                                                            'identificador '
                                                                                                                                                                                            'privado '
                                                                                                                                                                                            'não '
                                                                                                                                                                                            'é '
                                                                                                                                                                                            'público.',
                                                                                                                                                                                            'El '
                                                                                                                                                                                            'sitio '
                                                                                                                                                                                            'usa '
                                                                                                                                                                                            'una '
                                                                                                                                                                                            'cookie '
                                                                                                                                                                                            'aleatoria '
                                                                                                                                                                                            'para '
                                                                                                                                                                                            'identificar '
                                                                                                                                                                                            'tu '
                                                                                                                                                                                            'navegador, '
                                                                                                                                                                                            'proteger '
                                                                                                                                                                                            'solicitudes, '
                                                                                                                                                                                            'gestionar '
                                                                                                                                                                                            'comentarios '
                                                                                                                                                                                            'y '
                                                                                                                                                                                            'limitar '
                                                                                                                                                                                            'abusos. '
                                                                                                                                                                                            'Tu '
                                                                                                                                                                                            'nombre '
                                                                                                                                                                                            'es '
                                                                                                                                                                                            'público '
                                                                                                                                                                                            'tras '
                                                                                                                                                                                            'la '
                                                                                                                                                                                            'moderación; '
                                                                                                                                                                                            'tu '
                                                                                                                                                                                            'identificador '
                                                                                                                                                                                            'privado '
                                                                                                                                                                                            'no '
                                                                                                                                                                                            'es '
                                                                                                                                                                                            'público.']})
LOCALES={'fr':0,'en':1,'pt-BR':2,'es':3}
def ui_text(value,locale):
    i=LOCALES.get(locale)
    return PHRASES[value][i] if i is not None and value in PHRASES else value
class Localizer(HTMLParser):
    def __init__(self,locale):super().__init__(convert_charrefs=False);self.locale=locale;self.parts=[];self.verbatim=0;self.catalog=ui_translation(locale) if locale!='ht' else {};self.stack=[]
    def translated(self,value):
        local=ui_text(value,self.locale)
        if local!=value:return local
        for phrase in ['Tout dwa rezève.', 'kategori']:
            if phrase=='Tout dwa rezève.' and value.startswith('© ') and value.endswith(phrase):
                return value[:-len(phrase)]+ui_text(phrase,self.locale)
            if phrase=='kategori' and value.endswith(' · kategori'):
                return value[:-len(phrase)]+ui_text('Kategori',self.locale).lower()
        return self.catalog.get('phrase:'+value,value)
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
