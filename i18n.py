LANGUAGES={'fr':'Français','en':'English','pt-BR':'Português','es':'Español'}
KEYS=['home','haiti','world','news','interviews','videos','trending','discoveries','influencers','search','latest','see_all','spotlight','creators','read','editorial','saved','notifications','submit','about','contact','advertising','privacy','terms','comments','reply','publish','report','name','comment','save','share','demo','all','read_time','original','auto','no_results','explore','search_placeholder','submit_news','new_talents']
VALUES={
'source':['Dakèy','Ayiti','Mond','Aktyalite','Entèvyou','Videyo','Tandans','Dekouvèt','Enfliyansè','Rechèch','Dènye nouvèl','Wè tout','An vedèt','Kreyatè pou dekouvri','Li atik la','Seleksyon editoryal','Atik sove','Notifikasyon','Pwopoze yon kreyatè','Kiyès nou ye','Kontak','Piblisite','Konfidansyalite','Kondisyon','Kòmantè','Reponn','Pibliye','Rapòte','Non / Pseudo','Kòmantè ou','Sove','Pataje','Kontni demonstrasyon','Tout','min lekti','Wè orijinal','Tradiksyon otomatik','Pa gen rezilta pou kounye a.','Dekouvri','Chèche yon atik, yon kreyatè…','Soumèt yon nouvèl','Nouvo talan'],
'fr':['Accueil','Haïti','Monde','Actualités','Entretiens','Vidéos','Tendances','Découvertes','Créateurs','Recherche','À la une','Tout voir','En couverture','Créateurs à découvrir','Lire l’article','Sélection éditoriale','Articles enregistrés','Notifications','Proposer un créateur','À propos','Contact','Publicité','Confidentialité','Conditions','Commentaires','Répondre','Publier','Signaler','Nom / Pseudo','Votre commentaire','Enregistrer','Partager','Contenu de démonstration','Tous','min de lecture','Voir l’original','Traduction automatique','Aucun résultat pour le moment.','Découvrir','Rechercher un article, un créateur…','Soumettre une information','Nouveaux talents'],
'en':['Home','Haiti','World','News','Interviews','Videos','Trending','Discoveries','Creators','Search','Latest stories','View all','In focus','Creators to discover','Read the story','Editor’s selection','Saved stories','Notifications','Suggest a creator','About us','Contact','Advertise','Privacy','Terms','Comments','Reply','Publish','Report','Name / Alias','Your comment','Save','Share','Demonstration content','All','min read','View original','Machine translation','No results yet.','Explore','Search a story, a creator…','Submit a story','Emerging voices'],
'pt-BR':['Início','Haiti','Mundo','Notícias','Entrevistas','Vídeos','Tendências','Descobertas','Criadores','Busca','Últimas notícias','Ver todos','Em destaque','Criadores para descobrir','Ler a matéria','Seleção editorial','Artigos salvos','Notificações','Sugerir um criador','Sobre nós','Contato','Publicidade','Privacidade','Termos','Comentários','Responder','Publicar','Denunciar','Nome / Apelido','Seu comentário','Salvar','Compartilhar','Conteúdo de demonstração','Todos','min de leitura','Ver original','Tradução automática','Nenhum resultado ainda.','Descobrir','Buscar artigo, criador…','Enviar uma notícia','Novos talentos'],
'es':['Inicio','Haití','Mundo','Noticias','Entrevistas','Vídeos','Tendencias','Descubrimientos','Creadores','Buscar','Últimas noticias','Ver todos','En portada','Creadores por descubrir','Leer artículo','Selección editorial','Artículos guardados','Notificaciones','Proponer un creador','Quiénes somos','Contacto','Publicidad','Privacidad','Condiciones','Comentarios','Responder','Publicar','Denunciar','Nombre / Alias','Tu comentario','Guardar','Compartir','Contenido de demostración','Todos','min de lectura','Ver original','Traducción automática','Sin resultados por ahora.','Explorar','Buscar artículo, creador…','Enviar una noticia','Nuevos talentos']}
KEYS.extend(['contact_intro','creator_intro','advertising_intro'])
VALUES['fr'].extend([
 'Une information, une correction ou une question ? Écrivez à l’équipe éditoriale.',
 'Vous connaissez un créateur à découvrir ? Partagez son nom, son origine et ses liens officiels.',
 'Pour les bannières directes, les partenariats éditoriaux et les contenus sponsorisés, écrivez-nous.'
])
VALUES['en'].extend([
 'Have information, a correction or a question? Write to the editorial team.',
 'Know a creator we should discover? Share their name, origin, and official links.',
 'For direct banners, editorial partnerships and sponsored content, contact our team.'
])
VALUES['pt-BR'].extend([
 'Tem uma informação, uma correção ou uma pergunta? Escreva para a equipe editorial.',
 'Conhece um criador que deveríamos descobrir? Compartilhe seu nome, origem e links oficiais.',
 'Para banners diretos, parcerias editoriais e conteúdo patrocinado, escreva para nossa equipe.'
])
VALUES['es'].extend([
 '¿Tienes información, una corrección o una pregunta? Escribe al equipo editorial.',
 '¿Conoces a un creador que deberíamos descubrir? Comparte su nombre, origen y enlaces oficiales.',
 'Para banners directos, colaboraciones editoriales y contenido patrocinado, contacta con nuestro equipo.'
])
KEYS.extend(['article_available_in','editorial_translation','article_sources','article_corrections','article_demo_notice'])
VALUES['fr'].extend(['Cet article est disponible en {language}.','Traduction éditoriale','Sources et documents','Corrections éditoriales','Article de démonstration. La personne illustrée est fictive ; l’image a été générée par IA.'])
VALUES['en'].extend(['This article is available in {language}.','Editorial translation','Sources and documents','Editorial corrections','Demonstration article. The illustrated person is fictional; the image was generated with AI.'])
VALUES['pt-BR'].extend(['Este artigo está disponível em {language}.','Tradução editorial','Fontes e documentos','Correções editoriais','Artigo de demonstração. A pessoa ilustrada é fictícia; a imagem foi gerada por IA.'])
VALUES['es'].extend(['Este artículo está disponible en {language}.','Traducción editorial','Fuentes y documentos','Correcciones editoriales','Artículo de demostración. La persona ilustrada es ficticia; la imagen se generó con IA.'])
KEYS.extend(['about_scope_heading','about_scope','about_participation_heading','about_participation','site_summary','publisher_relationship'])
VALUES['fr'].extend(['Créateurs, société et actualité.','Geovyora est un média consacré aux créateurs, à la culture et à l’actualité d’Haïti, de sa diaspora et du monde. Nos articles proposent des portraits, des synthèses documentées et des explications sur la vie publique et les usages numériques. Les sources et les limites des informations sont indiquées pour permettre au lecteur de les examiner.','Lire, découvrir, participer.','Vous pouvez lire et partager les articles sans compte. Les commentaires sont modérés. Les favoris restent sur votre appareil. Le formulaire de contact permet de proposer un sujet, transmettre un document, demander une correction ou exercer un droit de réponse.','Créateurs, culture et actualité. Haïti, sa diaspora et le monde.','Transparence : Geovyora est un projet de Haytiles, l’entreprise présentée dans cet article. Ce lien doit être pris en compte dans la lecture.'])
VALUES['en'].extend(['Creators, society and current affairs.','Geovyora covers creators, culture and news from Haiti, its diaspora and the world. Our articles offer profiles, documented summaries and explanations of public life and digital practices. Sources and the limits of the information are identified so readers can examine them.','Read, discover, participate.','You can read and share articles without an account. Comments are moderated. Saved articles remain on your device. The contact form can be used to suggest a topic, submit a document, request a correction or exercise a right of reply.','Creators, culture and news. Haiti, its diaspora and the world.','Transparency: Geovyora is a project of Haytiles, the company featured in this article. Readers should take this relationship into account.'])
VALUES['pt-BR'].extend(['Criadores, sociedade e atualidade.','A Geovyora aborda criadores, cultura e notícias do Haiti, de sua diáspora e do mundo. Nossos artigos oferecem perfis, sínteses documentadas e explicações sobre a vida pública e as práticas digitais. As fontes e os limites das informações são indicados para que o leitor possa examiná-los.','Ler, descobrir, participar.','Você pode ler e compartilhar artigos sem criar uma conta. Os comentários são moderados. Os artigos salvos ficam no seu dispositivo. O formulário de contato permite sugerir uma pauta, enviar um documento, pedir uma correção ou exercer o direito de resposta.','Criadores, cultura e notícias. Haiti, sua diáspora e o mundo.','Transparência: a Geovyora é um projeto da Haytiles, empresa apresentada neste artigo. Essa relação deve ser considerada na leitura.'])
VALUES['es'].extend(['Creadores, sociedad y actualidad.','Geovyora aborda creadores, cultura y noticias de Haití, su diáspora y el mundo. Nuestros artículos ofrecen perfiles, síntesis documentadas y explicaciones sobre la vida pública y los usos digitales. Se indican las fuentes y los límites de la información para que el lector pueda examinarlos.','Leer, descubrir, participar.','Puede leer y compartir artículos sin una cuenta. Los comentarios se moderan. Los artículos guardados permanecen en su dispositivo. El formulario de contacto permite proponer un tema, enviar un documento, pedir una corrección o ejercer el derecho de respuesta.','Creadores, cultura y noticias. Haití, su diáspora y el mundo.','Transparencia: Geovyora es un proyecto de Haytiles, la empresa presentada en este artículo. Esta relación debe tenerse en cuenta al leerlo.'])
KEYS.extend(['world_summary','world_count'])
VALUES['fr'].extend(['Tous les articles de Geovyora : Haïti, diaspora et actualité du monde.','Articles disponibles : {count}'])
VALUES['en'].extend(['All Geovyora articles: Haiti, the diaspora and news from around the world.','Available articles: {count}'])
VALUES['pt-BR'].extend(['Todos os artigos da Geovyora: Haiti, diáspora e notícias do mundo.','Artigos disponíveis: {count}'])
VALUES['es'].extend(['Todos los artículos de Geovyora: Haití, diáspora y actualidad del mundo.','Artículos disponibles: {count}'])
LANGUAGE_NAMES={
 'fr':{'fr':'français','en':'anglais','pt-BR':'portugais (Brésil)','es':'espagnol'},
 'en':{'fr':'French','en':'English','pt-BR':'Brazilian Portuguese','es':'Spanish'},
 'pt-BR':{'fr':'francês','en':'inglês','pt-BR':'português (Brasil)','es':'espanhol'},
 'es':{'fr':'francés','en':'inglés','pt-BR':'portugués (Brasil)','es':'español'},
}
def labels(locale): return dict(zip(KEYS,VALUES.get(locale,VALUES['en'])))

# Public accountability and documentary context, explicitly localized on the server.
KEYS.extend(['public_contact_person', 'published_on', 'documentary_context', 'editorial_method_link'])
VALUES['fr'].extend(['Responsable et contact public', 'Publié le', 'Les annonces et chiffres de cet article sont situés à sa date de publication. Une annonce ne confirme pas son résultat ultérieur. Les références et les éventuelles corrections figurent ci-dessous.', 'Sources, méthode et corrections'])
VALUES['en'].extend(['Responsible person and public contact', 'Published on', 'Announcements and figures in this article are placed in the context of its publication date. An announcement does not confirm its subsequent outcome. References and any corrections appear below.', 'Sources, method and corrections'])
VALUES['pt-BR'].extend(['Responsável e contato público', 'Publicado em', 'Os anúncios e números deste artigo são apresentados no contexto da data de publicação. Um anúncio não confirma seu resultado posterior. As referências e eventuais correções estão abaixo.', 'Fontes, método e correções'])
VALUES['es'].extend(['Responsable y contacto público', 'Publicado el', 'Los anuncios y cifras de este artículo se sitúan en el contexto de su fecha de publicación. Un anuncio no confirma su resultado posterior. Las referencias y las posibles correcciones figuran abajo.', 'Fuentes, método y correcciones'])

KEYS.extend(['guides','guides_summary'])
VALUES['fr'].extend(['Guides et outils','Des méthodes, des exemples et des outils Geovyora pour les créateurs et la diaspora.'])
VALUES['en'].extend(['Guides and tools','Geovyora methods, worked examples and tools for creators and the diaspora.'])
VALUES['pt-BR'].extend(['Guias e ferramentas','Métodos, exemplos e ferramentas Geovyora para criadores e a diáspora.'])
VALUES['es'].extend(['Guías y herramientas','Métodos, ejemplos y herramientas Geovyora para creadores y la diáspora.'])
# Keep the repeated notice brief; detailed limitations live in the linked method.
for language, text in {
 'fr':'Repères et annonces à la date de publication ; voir les références et corrections ci-dessous.',
 'en':'Facts and announcements as of publication; see references and corrections below.',
 'pt-BR':'Informações e anúncios na data da publicação; veja as referências e correções abaixo.',
 'es':'Información y anuncios a la fecha de publicación; véanse las referencias y correcciones abajo.'
}.items():
 VALUES[language][KEYS.index('documentary_context')]=text
KEYS.append('tools_privacy')
VALUES['fr'].append('Les calculs des outils éditoriaux sont effectués dans votre navigateur. Les valeurs saisies ne sont pas envoyées au serveur Geovyora et ne sont pas enregistrées par ces outils. Les pages restent soumises aux autres traitements décrits ci-dessus, notamment le chargement du script Google de vérification.')
VALUES['en'].append('Editorial tool calculations run in your browser. Entered values are not sent to the Geovyora server or saved by these tools. Pages remain subject to the other processing described above, including loading the Google verification script.')
VALUES['pt-BR'].append('Os cálculos das ferramentas editoriais são feitos no navegador. Os valores digitados não são enviados ao servidor Geovyora nem armazenados pelas ferramentas. As páginas continuam sujeitas aos outros tratamentos descritos acima, incluindo o carregamento do script de verificação do Google.')
VALUES['es'].append('Los cálculos de las herramientas editoriales se realizan en el navegador. Los valores no se envían al servidor Geovyora ni se guardan mediante estas herramientas. Las páginas siguen sujetas a los demás tratamientos descritos arriba, incluida la carga del script de verificación de Google.')
