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
 'Know a creator we should discover? Share their name, origin and official links.',
 'For direct banners, editorial partnerships and sponsored content, contact our team.'
])
VALUES['pt-BR'].extend([
 'Tem uma informação, uma correção ou uma pergunta? Escreva para a equipe editorial.',
 'Conhece um criador que deveríamos descobrir? Compartilhe o nome, a origem e os links oficiais.',
 'Para banners diretos, parcerias editoriais e conteúdo patrocinado, escreva para nossa equipe.'
])
VALUES['es'].extend([
 '¿Tienes información, una corrección o una pregunta? Escribe al equipo editorial.',
 '¿Conoces a un creador que deberíamos descubrir? Comparte su nombre, origen y enlaces oficiales.',
 'Para banners directos, colaboraciones editoriales y contenido patrocinado, contacta con nuestro equipo.'
])
def labels(locale): return dict(zip(KEYS,VALUES.get(locale,VALUES['en'])))
