"""Local staff-interface translations; never sends CMS content to a provider."""
from localization import Localizer, ui_text, LOCALES
from html.parser import HTMLParser
from i18n import KEYS,VALUES
BASE_LABELS={value:key for key,value in zip(KEYS,VALUES['ht'])}
COPY = {}
_ROWS = '''ESPAS EDITORYAL|ESPACE ÉDITORIAL|EDITORIAL WORKSPACE|ESPAÇO EDITORIAL|ESPACIO EDITORIAL
Apèsi|Vue d’ensemble|Overview|Visão geral|Resumen
Atik & entèvyou|Articles et entretiens|Stories and interviews|Artigos e entrevistas|Artículos y entrevistas
Enfliyansè|Créateurs|Creators|Criadores|Creadores
Videyo / Mux|Vidéos / Mux|Videos / Mux|Vídeos / Mux|Vídeos / Mux
Kòmantè|Commentaires|Comments|Comentários|Comentarios
Rapò|Signalements|Reports|Denúncias|Denuncias
Soumisyon|Messages reçus|Submissions|Mensagens recebidas|Mensajes recibidos
Tradiksyon|Traductions|Translations|Traduções|Traducciones
Foto / Medya|Photos / Médias|Photos / Media|Fotos / Mídia|Fotos / Medios
Analitik|Statistiques|Analytics|Estatísticas|Estadísticas
Ekip|Équipe|Team|Equipe|Equipo
Paramèt|Paramètres|Settings|Configurações|Configuración
Kont ekip la|Mon compte|My account|Minha conta|Mi cuenta
Jounal aksyon|Journal d’activité|Activity log|Registro de atividades|Registro de actividad
Bon retou.|Bon retour.|Welcome back.|Bem-vindo de volta.|Bienvenido de nuevo.
Administrasyon prive pou ekip Geovyora.|Administration privée pour l’équipe Geovyora.|Private administration for the Geovyora team.|Administração privada da equipe Geovyora.|Administración privada del equipo Geovyora.
Imel|Email|Email|Email|Correo
Modpas|Mot de passe|Password|Senha|Contraseña
Konekte|Se connecter|Sign in|Entrar|Entrar
Retounen sou magazin nan|Retour au magazine|Return to magazine|Voltar à revista|Volver a la revista
Kont yo egziste sèlman pou ekip administrasyon an.|Les comptes sont réservés à l’équipe.|Accounts are for staff only.|Contas são exclusivas da equipe.|Las cuentas son solo para el equipo.
Gade magazin nan|Voir le magazine|View magazine|Ver revista|Ver revista
Dekonekte|Se déconnecter|Sign out|Sair|Salir
Chanjman yo sove.|Modifications enregistrées.|Changes saved.|Alterações salvas.|Cambios guardados.
JOUNAL EDITORYAL|TABLEAU ÉDITORIAL|EDITORIAL DASHBOARD|PAINEL EDITORIAL|PANEL EDITORIAL
Kontni ou, kominote ou, nan yon sèl espas.|Votre contenu et votre communauté, au même endroit.|Your content and community in one place.|Seu conteúdo e sua comunidade em um só lugar.|Tu contenido y comunidad en un solo lugar.
Kreye yon atik|Créer un article|Create a story|Criar artigo|Crear artículo
Atik nan CMS|Articles dans le CMS|Stories in CMS|Artigos no CMS|Artículos en el CMS
Pwofil medya|Profils éditoriaux|Editorial profiles|Perfis editoriais|Perfiles editoriales
Kòmantè an atant|Commentaires en attente|Pending comments|Comentários pendentes|Comentarios pendientes
Rapò an atant|Signalements en attente|Pending reports|Denúncias pendentes|Denuncias pendientes
Done nan baz sit la|Données du site|Site database records|Dados do site|Datos del sitio
Revizyon k ap tann|À examiner|Awaiting review|Aguardando análise|Pendiente de revisión
Kòmantè pou modere|Commentaires à modérer|Comments to moderate|Comentários para moderar|Comentarios para moderar
Rapò pou egzamine|Signalements à examiner|Reports to review|Denúncias para analisar|Denuncias para revisar
Soumisyon resevwa|Messages reçus|Received submissions|Mensagens recebidas|Mensajes recibidos
Videyo nan bibliyotèk|Vidéos en bibliothèque|Videos in library|Vídeos na biblioteca|Vídeos en biblioteca
Sèvis|Services|Services|Serviços|Servicios
Pa konfigire|Non configuré|Not configured|Não configurado|No configurado
Kle konfigire|Clés configurées|Keys configured|Chaves configuradas|Claves configuradas
Kle konfigire · tès obligatwa|Clés configurées · test requis|Keys configured · test required|Chaves configuradas · teste necessário|Claves configuradas · prueba necesaria
Pa gen koneksyon ekstèn simulate.|Le statut indique la configuration, pas un test de connexion.|Status indicates configuration, not a connection test.|O status indica configuração, não um teste de conexão.|El estado indica configuración, no una prueba de conexión.
Atik ki plis li sou sit la|Articles les plus lus|Most read stories|Artigos mais lidos|Artículos más leídos
Nouvo atik|Nouvel article|New story|Novo artigo|Nuevo artículo
Draft, revizyon, planifikasyon ak piblikasyon.|Brouillons, révision, programmation et publication.|Drafts, review, scheduling and publication.|Rascunhos, revisão, agendamento e publicação.|Borradores, revisión, programación y publicación.
Tit|Titre|Title|Título|Título
Soutit|Sous-titre|Subtitle|Subtítulo|Subtítulo
Kò atik la|Corps de l’article|Story body|Corpo do artigo|Cuerpo del artículo
Nòt koreksyon (piblik, opsyonèl)|Note de correction (publique, facultative)|Correction note (public, optional)|Nota de correção (pública, opcional)|Nota de corrección (pública, opcional)
Sous|Sources|Sources|Fontes|Fuentes
Tags (separe pa vigil)|Tags (séparés par des virgules)|Tags (comma separated)|Tags (separadas por vírgulas)|Etiquetas (separadas por comas)
Otè|Auteur|Author|Autor|Autor
Rejyon|Région|Region|Região|Región
Ayiti / Dyaspora|Haïti / Diaspora|Haiti / Diaspora|Haiti / Diáspora|Haití / Diáspora
Fòma|Format|Format|Formato|Formato
Atik|Article|Story|Artigo|Artículo
Estati|Statut|Status|Status|Estado
Dat piblikasyon / UTC|Date de publication / UTC|Publish date / UTC|Data de publicação / UTC|Fecha de publicación / UTC
Foto · URL HTTPS|Photo · URL HTTPS|Photo · HTTPS URL|Foto · URL HTTPS|Foto · URL HTTPS
Kredi foto|Crédit photo|Photo credit|Crédito da foto|Crédito de la foto
ID enfliyansè asosye|ID du créateur associé|Related creator ID|ID do criador associado|ID del creador relacionado
An vedèt|En vedette|Featured|Em destaque|Destacado
Kontni demonstrasyon|Contenu de démonstration|Demo content|Conteúdo de demonstração|Contenido de demostración
Kontni patwone|Contenu sponsorisé|Sponsored content|Conteúdo patrocinado|Contenido patrocinado
Sove chanjman yo|Enregistrer les modifications|Save changes|Salvar alterações|Guardar cambios
Gade atik la|Voir l’article|View story|Ver artigo|Ver artículo
Preview prive|Aperçu privé|Private preview|Prévia privada|Vista previa privada
Istwa vèsyon yo|Historique des versions|Version history|Histórico de versões|Historial de versiones
Mizajou|Mis à jour|Updated|Atualizado|Actualizado
Modifye|Modifier|Edit|Editar|Editar
Pa gen atik. Kreye premye atik ou.|Aucun article. Créez votre premier article.|No stories yet. Create your first story.|Sem artigos. Crie seu primeiro artigo.|Sin artículos. Crea tu primer artículo.
Nouvo pwofil|Nouveau profil|New profile|Novo perfil|Nuevo perfil
Non piblik|Nom public|Public name|Nome público|Nombre público
Peyi orijin|Pays d’origine|Country of origin|País de origem|País de origen
Lang kontni|Langue du contenu|Content language|Idioma do conteúdo|Idioma del contenido
Bio editoryal|Biographie éditoriale|Editorial biography|Biografia editorial|Biografía editorial
Pwofil demonstrasyon|Profil de démonstration|Demo profile|Perfil de demonstração|Perfil de demostración
Sove pwofil la|Enregistrer le profil|Save profile|Salvar perfil|Guardar perfil
Non|Nom|Name|Nome|Nombre
Estatistik avèk sous|Statistiques sourcées|Sourced statistics|Estatísticas com fontes|Estadísticas con fuentes
Abonnés|Abonnés|Followers|Seguidores|Seguidores
Sous piblik HTTPS|Source publique HTTPS|Public HTTPS source|Fonte pública HTTPS|Fuente pública HTTPS
Dat verifikasyon / UTC|Date de vérification / UTC|Verification date / UTC|Data de verificação / UTC|Fecha de verificación / UTC
Sove estatistik la|Enregistrer les statistiques|Save statistics|Salvar estatísticas|Guardar estadísticas
MODERASYON|MODÉRATION|MODERATION|MODERAÇÃO|MODERACIÓN
Chak desizyon sove nan jounal aksyon an.|Chaque décision est enregistrée dans le journal.|Every decision is recorded in the activity log.|Cada decisão é registrada no histórico.|Cada decisión se registra en el historial.
Aplike|Appliquer|Apply|Aplicar|Aplicar
Limite patisipasyon navigatè sa a|Limiter ce navigateur|Restrict this browser|Restringir este navegador|Restringir este navegador
Limite tanporèman|Limiter temporairement|Temporarily restrict|Restringir temporariamente|Restringir temporalmente
Retire limit la|Retirer la restriction|Remove restriction|Remover restrição|Quitar restricción
Tout bagay annòd.|Tout est à jour.|All caught up.|Tudo em dia.|Todo al día.
Pa gen dosye pou kounye a.|Aucun dossier pour le moment.|No records yet.|Sem registros no momento.|Todavía no hay registros.
Nouvo videyo|Nouvelle vidéo|New video|Novo vídeo|Nuevo vídeo
Chajman dirèk nan Mux. Se sèlman videyo ki pare ki parèt sou sit la.|Envoi direct vers Mux. Seules les vidéos prêtes sont publiées.|Upload directly to Mux. Only ready videos appear on the site.|Envio direto ao Mux. Só vídeos prontos aparecem no site.|Subida directa a Mux. Solo vídeos listos aparecen en el sitio.
Deskripsyon|Description|Description|Descrição|Descripción
Fichye videyo|Fichier vidéo|Video file|Arquivo de vídeo|Archivo de vídeo
Chaje videyo a|Envoyer la vidéo|Upload video|Enviar vídeo|Subir vídeo
Videyo|Vidéo|Video|Vídeo|Vídeo
Pa gen videyo pou kounye a.|Aucune vidéo pour le moment.|No videos yet.|Ainda não há vídeos.|Todavía no hay vídeos.
Chaje yon foto|Envoyer une photo|Upload a photo|Enviar uma foto|Subir una foto
Foto|Photo|Photo|Foto|Foto
Chaje foto a|Envoyer la photo|Upload photo|Enviar foto|Subir foto
URL pou CMS|Lien du média|Media link|Link da mídia|Enlace del archivo
Verifye foto a|Vérifier la photo|Verify photo|Verificar foto|Verificar foto
Pa gen foto chaje.|Aucune photo envoyée.|No uploaded photos.|Nenhuma foto enviada.|Ninguna foto subida.
Non mak|Nom de marque|Brand name|Nome da marca|Nombre de marca
Imel kontak|Email de contact|Contact email|Email de contato|Correo de contacto
Tagline|Slogan|Tagline|Slogan|Eslogan
Lang default|Langue par défaut|Default language|Idioma padrão|Idioma predeterminado
Limit tradiksyon / karaktè pa mwa|Limite de traduction / caractères par mois|Translation limit / characters per month|Limite de tradução / caracteres por mês|Límite de traducción / caracteres por mes
Antrepriz / responsab|Entreprise / responsable|Company / responsible person|Empresa / responsável|Empresa / responsable
Adrès antrepriz|Adresse de l’entreprise|Company address|Endereço da empresa|Dirección de la empresa
Limit push pa jou|Limite push quotidienne|Daily push limit|Limite diário de notificações|Límite diario de notificaciones
Lòd seksyon dakèy|Ordre des sections d’accueil|Homepage section order|Ordem das seções iniciais|Orden de secciones de inicio
Prepare espas piblisite|Préparer les espaces publicitaires|Prepare advertising slots|Preparar espaços publicitários|Preparar espacios publicitarios
Sove paramèt yo|Enregistrer les paramètres|Save settings|Salvar configurações|Guardar configuración
Bannè piblisite dirèk|Bannières publicitaires|Advertising banners|Banners publicitários|Banners publicitarios
Non kanpay|Nom de campagne|Campaign name|Nome da campanha|Nombre de campaña
Tout lang|Toutes les langues|All languages|Todos os idiomas|Todos los idiomas
URL foto|Lien de la photo|Photo link|Link da foto|Enlace de la foto
Lyen patnè HTTPS|Lien partenaire HTTPS|Partner HTTPS link|Link HTTPS do parceiro|Enlace HTTPS del colaborador
Aktive bannè a|Activer la bannière|Enable banner|Ativar banner|Activar banner
Sove bannè|Enregistrer la bannière|Save banner|Salvar banner|Guardar banner
Tradiksyon editoryal|Traductions éditoriales|Editorial translations|Traduções editoriais|Traducciones editoriales
Kalite|Type|Type|Tipo|Tipo
ID kontni|ID du contenu|Content ID|ID do conteúdo|ID del contenido
Lang sib|Langue cible|Target language|Idioma de destino|Idioma de destino
Kò atik|Corps de l’article|Story body|Corpo do artigo|Cuerpo del artículo
Bio (pou pwofil sèlman)|Biographie (profils uniquement)|Biography (profiles only)|Biografia (apenas perfis)|Biografía (solo perfiles)
Sove tradiksyon an|Enregistrer la traduction|Save translation|Salvar tradução|Guardar traducción
Kontni|Contenu|Content|Conteúdo|Contenido
Vèsyon sous|Version source|Source version|Versão original|Versión original
Pa gen tradiksyon sove.|Aucune traduction enregistrée.|No saved translations.|Nenhuma tradução salva.|Ninguna traducción guardada.
Fil travay tradiksyon|File de traduction|Translation queue|Fila de tradução|Cola de traducción
Mete lis lang Google yo ajou|Actualiser les langues Google|Refresh Google languages|Atualizar idiomas Google|Actualizar idiomas Google
Repran travay la|Réessayer la tâche|Retry job|Tentar novamente|Reintentar tarea
Pa gen travay an fil.|Aucune tâche en attente.|No queued jobs.|Nenhuma tarefa na fila.|Ninguna tarea en cola.
Wòl|Rôle|Role|Função|Rol
Jere manm lan|Gérer le membre|Manage member|Gerenciar membro|Gestionar miembro
Aksyon|Action|Action|Ação|Acción
Chanje wòl|Changer le rôle|Change role|Alterar função|Cambiar rol
Dezaktive|Désactiver|Disable|Desativar|Desactivar
Reaktive|Réactiver|Reactivate|Reativar|Reactivar
Reset modpas|Réinitialiser le mot de passe|Reset password|Redefinir senha|Restablecer contraseña
Nouvo modpas (pou reset sèlman)|Nouveau mot de passe (réinitialisation uniquement)|New password (reset only)|Nova senha (apenas redefinição)|Nueva contraseña (solo restablecimiento)
Ajoute yon manm|Ajouter un membre|Add a member|Adicionar membro|Añadir miembro
Modpas tanporè (12 karaktè minimòm)|Mot de passe temporaire (12 caractères minimum)|Temporary password (minimum 12 characters)|Senha temporária (mínimo 12 caracteres)|Contraseña temporal (mínimo 12 caracteres)
Kreye manm lan|Créer le membre|Create member|Criar membro|Crear miembro
Lekti anrejistre|Lectures enregistrées|Recorded reads|Leituras registradas|Lecturas registradas
Abònman push|Abonnements push|Push subscriptions|Inscrições push|Suscripciones push
Dosye|Dossier|Record|Registro|Registro
Pa gen aksyon ankò.|Aucune activité pour le moment.|No activity yet.|Ainda não há atividades.|Todavía no hay actividad.
ÒGANIZASYON EDITORYAL|ORGANISATION ÉDITORIALE|EDITORIAL ORGANIZATION|ORGANIZAÇÃO EDITORIAL|ORGANIZACIÓN EDITORIAL
Ajoute|Ajouter|Add|Adicionar|Añadir
kategori|catégorie|category|categoria|categoría
Lòd|Ordre|Order|Ordem|Orden
Kategori aktif|Catégorie active|Active category|Categoria ativa|Categoría activa
Sove|Enregistrer|Save|Salvar|Guardar
Lòd / Estati|Ordre / Statut|Order / Status|Ordem / Status|Orden / Estado
MOTÈ RECHÈCH|MOTEURS DE RECHERCHE|SEARCH ENGINES|MOTORES DE BUSCA|MOTORES DE BÚSQUEDA
Pa indexe paj sa a|Ne pas indexer cette page|Do not index this page|Não indexar esta página|No indexar esta página
Sove SEO|Enregistrer le SEO|Save SEO|Salvar SEO|Guardar SEO
ABÒNMAN KONSANTAN|ABONNEMENTS CONSENTIS|OPT-IN SUBSCRIPTIONS|INSCRIÇÕES CONSENTIDAS|SUSCRIPCIONES CONSENTIDAS
Pa gen abònman newsletter.|Aucun abonnement newsletter.|No newsletter subscriptions.|Nenhuma inscrição na newsletter.|Ninguna suscripción a la newsletter.
Sekirite kont ekip la|Sécurité de mon compte|Account security|Segurança da conta|Seguridad de la cuenta
Modpas aktyèl|Mot de passe actuel|Current password|Senha atual|Contraseña actual
Nouvo modpas (12 karaktè minimòm)|Nouveau mot de passe (12 caractères minimum)|New password (minimum 12 characters)|Nova senha (mínimo 12 caracteres)|Nueva contraseña (mínimo 12 caracteres)
Konfime nouvo modpas la|Confirmer le nouveau mot de passe|Confirm new password|Confirmar nova senha|Confirmar nueva contraseña
Chanje modpas la|Changer le mot de passe|Change password|Alterar senha|Cambiar contraseña
KANPAY & LIVREZON|CAMPAGNES ET LIVRAISON|CAMPAIGNS AND DELIVERY|CAMPANHAS E ENTREGA|CAMPAÑAS Y ENTREGA
Kreye yon kanpay|Créer une campagne|Create a campaign|Criar campanha|Crear campaña
Mesaj|Message|Message|Mensagem|Mensaje
Lyen relatif|Lien relatif|Relative link|Link relativo|Enlace relativo
Sijè|Sujet|Topic|Tema|Tema
Tout sijè|Tous les sujets|All topics|Todos os temas|Todos los temas
Enfliyansè (ID opsyonèl)|Créateur (ID facultatif)|Creator (optional ID)|Criador (ID opcional)|Creador (ID opcional)
Planifye / UTC (opsyonèl)|Programmer / UTC (facultatif)|Schedule / UTC (optional)|Agendar / UTC (opcional)|Programar / UTC (opcional)
Sove / Planifye|Enregistrer / Programmer|Save / Schedule|Salvar / Agendar|Guardar / Programar
Livrezon yo|Livraisons|Deliveries|Entregas|Entregas
Pa gen livrezon pou kounye a.|Aucune livraison pour le moment.|No deliveries yet.|Nenhuma entrega no momento.|Todavía no hay entregas.
Kanpay yo|Campagnes|Campaigns|Campanhas|Campañas
Preview lyen|Aperçu du lien|Preview link|Prévia do link|Vista previa del enlace
Mete nan fil pou voye|Mettre en file d’envoi|Queue for delivery|Colocar na fila|Poner en cola
Anile|Annuler|Cancel|Cancelar|Cancelar
Pa gen kanpay.|Aucune campagne.|No campaigns.|Nenhuma campanha.|Ninguna campaña.
San dat|Sans date|No date|Sem data|Sin fecha
aktif|actif|active|ativo|activo
inaktif|inactif|inactive|inativo|inactivo
draft|brouillon|draft|rascunho|borrador
in_review|en révision|in review|em revisão|en revisión
scheduled|programmé|scheduled|agendado|programado
published|publié|published|publicado|publicado
archived|archivé|archived|arquivado|archivado
pending|en attente|pending|pendente|pendiente
ready|prêt|ready|pronto|listo
processing|en traitement|processing|processando|procesando
uploading|envoi en cours|uploading|enviando|subiendo
rejected|rejeté|rejected|rejeitado|rechazado
approved|approuvé|approved|aprovado|aprobado
resolved|résolu|resolved|resolvido|resuelto
dismissed|classé|dismissed|arquivado|descartado
hidden|masqué|hidden|oculto|oculto
accepted|accepté|accepted|aceito|aceptado
deleted|supprimé|deleted|excluído|eliminado
super_admin|administrateur principal|super administrator|administrador principal|administrador principal
editor|éditeur|editor|editor|editor
moderator|modérateur|moderator|moderador|moderador
admin|administrateur|administrator|administrador|administrador
Fichye sa a depase limit chajman an.|Le fichier dépasse la limite d’envoi.|File exceeds the upload limit.|Arquivo excede o limite de envio.|El archivo supera el límite de subida.
Prepare chajman an…|Préparation de l’envoi…|Preparing upload…|Preparando envio…|Preparando subida…
Ap voye videyo a nan Mux…|Envoi de la vidéo vers Mux…|Uploading video to Mux…|Enviando vídeo ao Mux…|Subiendo vídeo a Mux…
Chajman echwe.|Échec de l’envoi.|Upload failed.|Falha no envio.|Error al subir.
Chajman echwe. Eseye ankò.|Échec de l’envoi. Réessayez.|Upload failed. Try again.|Falha no envio. Tente novamente.|Error al subir. Inténtalo de nuevo.
Chajman fini. Mux ap trete videyo a. Rechaje paj la pou wè estati a.|Envoi terminé. Mux traite la vidéo. Actualisez pour voir son statut.|Upload complete. Mux is processing the video. Refresh to see its status.|Envio concluído. Mux está processando o vídeo. Atualize para ver o status.|Subida completa. Mux procesa el vídeo. Actualiza para ver el estado.
Ou pa gen aksè.|Accès refusé.|Access denied.|Acesso negado.|Acceso denegado.
Pa gen vèsyon anvan.|Aucune version précédente.|No previous versions.|Nenhuma versão anterior.|Ninguna versión anterior.
Restore nan draft|Restaurer en brouillon|Restore as draft|Restaurar como rascunho|Restaurar como borrador
Restore vèsyon sa a nan draft?|Restaurer cette version en brouillon ?|Restore this version as a draft?|Restaurar esta versão como rascunho?|¿Restaurar esta versión como borrador?
Aksè admin obligatwa.|Accès administrateur requis.|Administrator access required.|Acesso administrativo necessário.|Se requiere acceso administrativo.
10 MB maksimòm.|10 Mo maximum.|Maximum 10 MB.|Máximo de 10 MB.|Máximo 10 MB.
Storage pa aksepte foto a. Verifye CORS.|Stockage : photo refusée. Vérifiez CORS.|Storage rejected the photo. Check CORS.|O armazenamento recusou a foto. Verifique CORS.|El almacenamiento rechazó la foto. Revisa CORS.
Ap verifye foto a…|Vérification de la photo…|Verifying photo…|Verificando foto…|Verificando foto…
Verifikasyon echwe.|Échec de vérification.|Verification failed.|Falha na verificação.|Error de verificación.
Foto a ajoute nan atik la.|Photo ajoutée à l’article.|Photo added to the story.|Foto adicionada ao artigo.|Foto añadida al artículo.
Chwazi yon foto|Choisir une photo|Choose a photo|Escolher foto|Elegir foto
Bibliyotèk foto|Bibliothèque de photos|Photo library|Biblioteca de fotos|Biblioteca de fotos
Chwazi nan bibliyotèk la|Choisir dans la bibliothèque|Choose from library|Escolher da biblioteca|Elegir de la biblioteca
Ajoute foto nan tèks la|Insérer une photo dans le texte|Insert photo into text|Inserir foto no texto|Insertar foto en el texto
Ajoute videyo nan tèks la|Insérer une vidéo dans le texte|Insert video into text|Inserir vídeo no texto|Insertar vídeo en el texto
Chwazi yon videyo ki pare|Choisir une vidéo prête|Choose a ready video|Escolher vídeo pronto|Elegir vídeo listo
Louvri paj chajman videyo|Ouvrir l’envoi vidéo|Open video upload page|Abrir envio de vídeo|Abrir subida de vídeo
Videyo a ajoute nan atik la.|Vidéo ajoutée à l’article.|Video added to the story.|Vídeo adicionado ao artigo.|Vídeo añadido al artículo.
Chaje yon foto anvan.|Envoyez d’abord une photo.|Upload a photo first.|Envie uma foto primeiro.|Sube una foto primero.
Foto chaje avèk siksè.|Photo envoyée avec succès.|Photo uploaded successfully.|Foto enviada com sucesso.|Foto subida correctamente.
Kle ki manke sou Render|Clés manquantes sur Render|Missing Render settings|Chaves ausentes no Render|Claves que faltan en Render
Konfigirasyon disponib; koneksyon poko teste.|Configuration disponible ; connexion non testée.|Settings present; connection not tested.|Configuração presente; conexão não testada.|Configuración disponible; conexión no probada.
Sèvis sa a opsyonèl.|Ce service est facultatif.|This service is optional.|Este serviço é opcional.|Este servicio es opcional.
Kle yo dwe nan Environment sèvis Render la. Fichye .env lokal la pa pibliye sou GitHub.|Ajoutez les clés dans Environment sur Render. Le fichier .env local n’est pas publié sur GitHub.|Add keys in the Render service Environment. Your local .env file is not published to GitHub.|Adicione as chaves em Environment no Render. O arquivo .env local não é publicado no GitHub.|Añade las claves en Environment de Render. El archivo .env local no se publica en GitHub.
'''
_ROWS += '''
Paramèt sit la|Paramètres du site|Site settings|Configurações do site|Configuración del sitio
Non, slug ak lòd kategori yo configurable.|Configurez les noms, slugs et l’ordre des catégories.|Configure category names, slugs and order.|Configure nomes, slugs e ordem das categorias.|Configura nombres, slugs y orden de categorías.
Tit, deskripsyon ak indexation pa kontni ak lang.|Titres, descriptions et indexation par contenu et langue.|Titles, descriptions and indexing by content and language.|Títulos, descrições e indexação por conteúdo e idioma.|Títulos, descripciones e indexación por contenido e idioma.
Metadata default yo sèvi jiskaske ou ajoute metadata espesifik.|Les métadonnées par défaut sont utilisées jusqu’à personnalisation.|Default metadata applies until you add custom metadata.|Os metadados padrão são usados até a personalização.|Se usan metadatos predeterminados hasta personalizarlos.
Imel sa yo soti nan fòm newsletter sèlman. Yo pa kont lektè.|Ces emails proviennent de la newsletter. Ce ne sont pas des comptes lecteurs.|These emails come from newsletter subscriptions, not reader accounts.|Estes emails vêm da newsletter, não de contas de leitores.|Estos correos vienen de la newsletter, no de cuentas de lectores.
Lis abònman ak dezabònman an mache. Livrezon imel mande yon sèvis imel ki poko konekte.|Les abonnements et désabonnements fonctionnent. L’envoi nécessite un service email non connecté.|Subscription and unsubscribe management works. Email delivery requires an email service that is not connected yet.|Inscrições e cancelamentos funcionam. O envio requer um serviço de email ainda não conectado.|Las suscripciones y bajas funcionan. El envío requiere un servicio de correo aún no conectado.
Chanjman an ap revoke tout sesyon kont sa a. Ou ap konekte ankò.|Cette modification déconnectera toutes vos sessions. Reconnectez-vous ensuite.|This change signs out all sessions for this account. Sign in again afterward.|A alteração encerra todas as sessões desta conta. Entre novamente depois.|El cambio cierra todas las sesiones de esta cuenta. Vuelve a entrar después.
Design fonse sèlman. Kòmantè yo toujou pase nan moderasyon. Sekrè sèvis yo antre nan anviwònman sèvè a.|Le site reste en thème sombre et les commentaires sont modérés. Configurez les clés dans l’environnement serveur.|The site uses a dark theme and comments are moderated. Configure secrets in the server environment.|O site usa tema escuro e comentários são moderados. Configure chaves no ambiente do servidor.|El sitio usa tema oscuro y comentarios moderados. Configura claves en el entorno del servidor.
JPG, PNG oswa WebP · 10 MB maksimòm. Foto pwodiksyon yo ale nan S3-compatible storage.|JPG, PNG ou WebP · 10 Mo maximum. Les photos sont stockées dans votre bucket.|JPG, PNG or WebP · Maximum 10 MB. Photos are stored in your bucket.|JPG, PNG ou WebP · Máximo de 10 MB. Fotos são armazenadas no seu bucket.|JPG, PNG o WebP · Máximo 10 MB. Las fotos se guardan en tu bucket.
Kanpay yo filtre selon lang, sijè oswa enfliyansè. Dezabònman an anile livrezon ki poko fèt.|Les campagnes sont filtrées par langue, sujet ou créateur. Le désabonnement annule les envois en attente.|Campaigns filter by language, topic or creator. Unsubscribing cancels pending deliveries.|Campanhas filtram por idioma, tema ou criador. Cancelar a inscrição cancela entregas pendentes.|Las campañas filtran por idioma, tema o creador. La baja cancela entregas pendientes.
Travay yo pase nan worker la. Demann ki gen livrezon ensèten pa retounen otomatikman nan fil la pou evite push repete.|Les tâches nécessitent le worker. Les livraisons incertaines ne sont pas relancées automatiquement afin d’éviter les doublons.|Jobs require the worker. Uncertain deliveries are not retried automatically to avoid duplicate notifications.|Tarefas exigem o worker. Entregas incertas não são repetidas automaticamente para evitar notificações duplicadas.|Las tareas requieren el worker. Las entregas inciertas no se reintentan automáticamente para evitar duplicados.
Lekti inik pa navigatè, atik ak jou. Pa reprezante kantite moun inik atravè aparèy.|Lectures uniques par navigateur, article et jour. Ce ne sont pas des personnes uniques entre appareils.|Unique reads by browser, story and day. This does not count unique people across devices.|Leituras únicas por navegador, artigo e dia. Não representa pessoas únicas entre dispositivos.|Lecturas únicas por navegador, artículo y día. No cuenta personas únicas entre dispositivos.
AdSense dezaktive sou kontni demo ak paj Kreyòl. Konekte yon CMP apwopriye, jwenn apwobasyon Google epi verifye lang kò kontni an anvan aktivasyon.|AdSense reste désactivé sur les démonstrations et pages créoles. Avant activation : consentement approprié, approbation Google et vérification de la langue du contenu.|AdSense stays disabled on demo content and Creole pages. Activation requires appropriate consent management, Google approval and content language verification.|AdSense fica desativado em demonstrações e páginas em crioulo. Ativar exige gestão de consentimento, aprovação Google e verificação do idioma do conteúdo.|AdSense permanece desactivado en demostraciones y páginas en criollo. Activarlo requiere gestión de consentimiento, aprobación Google y verificación del idioma del contenido.
Script AdSense pa chaje nan vèsyon sa a san entegrasyon konsantman final la. Pa gen revni oswa apwobasyon pwomèt.|Le script AdSense nécessite l’intégration finale du consentement. Aucun revenu ni approbation n’est garanti.|AdSense scripts require final consent integration. Revenue and approval are not guaranteed.|Scripts AdSense exigem integração final de consentimento. Receita e aprovação não são garantidas.|Los scripts AdSense requieren la integración final del consentimiento. No se garantizan ingresos ni aprobación.
Opsyonèl · pa aktive|Facultatif · non activé|Optional · not enabled|Opcional · não ativado|Opcional · no activado
karaktè itilize mwa sa a.|caractères utilisés ce mois-ci.|characters used this month.|caracteres usados neste mês.|caracteres usados este mes.
navigatè abòne. Limit chak jou respekte pou chak navigatè.|navigateurs abonnés. Limite quotidienne appliquée par navigateur.|subscribed browsers. Daily limit applied per browser.|navegadores inscritos. Limite diário por navegador.|navegadores suscritos. Límite diario por navegador.
Modifye kategori|Modifier la catégorie|Edit category|Editar categoria|Editar categoría
Ajoute kategori|Ajouter une catégorie|Add category|Adicionar categoria|Añadir categoría
Modifye tag|Modifier le tag|Edit tag|Editar tag|Editar etiqueta
Ajoute tag|Ajouter un tag|Add tag|Adicionar tag|Añadir etiqueta
otomatik-si-vid|automatique-si-vide|automatic-if-empty|automático-se-vazio|automático-si-vacío
Desizyon|Décision|Decision|Decisão|Decisión
Rezon desizyon an|Motif de la décision|Decision reason|Motivo da decisão|Motivo de la decisión
Dire an èdtan|Durée en heures|Duration in hours|Duração em horas|Duración en horas
Rezon entèdiksyon|Motif de restriction|Restriction reason|Motivo da restrição|Motivo de la restricción
Voye sèlman bay navigatè ki chwazi kreyatè sa a|Envoyer uniquement aux abonnés de ce créateur|Send only to browsers following this creator|Enviar apenas a navegadores que seguem este criador|Enviar solo a navegadores que siguen a este creador
Pa gen kont admin pou kounye a. Kreye premye kont lan avèk etap sekirize ki nan README a. Pa gen modpas default.|Aucun compte administrateur. Créez-en un avec la commande sécurisée du README. Aucun mot de passe par défaut.|No administrator account. Create one using the secure README command. There is no default password.|Sem conta administrativa. Crie uma com o comando seguro do README. Não há senha padrão.|Sin cuenta administrativa. Crea una con el comando seguro del README. No hay contraseña predeterminada.
Modil sa a poko aktif nan premye vèsyon sa a.|Ce module n’est pas actif.|This module is not active.|Este módulo não está ativo.|Este módulo no está activo.
Paragraf: liy vid · Tit: ## · Sitasyon:|Paragraphes : ligne vide · Titres : ## · Citations :|Paragraphs: blank line · Headings: ## · Quotes:|Parágrafos: linha vazia · Títulos: ## · Citações:|Párrafos: línea vacía · Títulos: ## · Citas:
· Lyen: [tèks](https://…) · Foto: ![lejand](https://…) · Videyo: [video:slug]|· Liens : [texte](https://…) · Photos : ![légende](https://…) · Vidéos : [video:slug]|· Links: [text](https://…) · Photos: ![caption](https://…) · Videos: [video:slug]|· Links: [texto](https://…) · Fotos: ![legenda](https://…) · Vídeos: [video:slug]|· Enlaces: [texto](https://…) · Fotos: ![leyenda](https://…) · Vídeos: [video:slug]
'''
_ROWS += '''
Ekri tit atik la anvan.|Écrivez d’abord le titre de l’article.|Enter the story title first.|Preencha o título do artigo primeiro.|Escribe primero el título del artículo.
Videyo a chaje epi ajoute nan atik la. Mux ap trete li.|Vidéo envoyée et ajoutée à l’article. Mux la traite.|Video uploaded and added to the story. Mux is processing it.|Vídeo enviado e adicionado ao artigo. Mux está processando.|Vídeo subido y añadido al artículo. Mux lo está procesando.
'''
_ROWS += '''
Notifikasyon|Notifications|Notifications|Notificações|Notificaciones
Piblisite|Publicité|Advertising|Publicidade|Publicidad
Storage|Stockage|Storage|Armazenamento|Almacenamiento
Geovyora / ADMINISTRATION|Geovyora / ADMINISTRATION|Geovyora / ADMINISTRATION|Geovyora / ADMINISTRAÇÃO|Geovyora / ADMINISTRACIÓN
'''
for row in _ROWS.strip().splitlines():
    if not row.strip():continue
    source,*translations=row.split('|')
    assert len(translations)==4, source
    COPY[source]=translations

def admin_text(value,locale):
    index=LOCALES.get(locale)
    if index is None:return value
    if value in COPY:return COPY[value][index]
    if value in BASE_LABELS:return VALUES[locale][KEYS.index(BASE_LABELS[value])]
    return ui_text(value,locale)

class AdminLocalizer(Localizer):
    def __init__(self,locale):
        HTMLParser.__init__(self,convert_charrefs=False)
        self.locale=locale;self.parts=[];self.verbatim=0;self.catalog={};self.stack=[]
    def translated(self,value):
        if value.startswith('ID kontni: '):return admin_text('ID kontni',self.locale)+': '+admin_text(value[len('ID kontni: '):],self.locale)
        return admin_text(value,self.locale)
    def handle_starttag(self,tag,attrs):
        # Existing Localizer protects scripts and article prose. Protect editable
        # content as well, and make private UI attributes eligible for translation.
        protected=tag in ['textarea','code','pre'] or any(k=='data-no-translate' for k,v in attrs)
        if protected:attrs=attrs+[('class','article-body')]
        source=self.get_starttag_text()
        import html
        for key,value in attrs:
            if key in ['placeholder','aria-label','title'] and value:
                source=source.replace('"'+html.escape(value,quote=True)+'"','"'+html.escape(self.translated(value),quote=True)+'"')
        # Preserve the original markup and use only the inherited protection stack.
        start=len(self.parts)
        super().handle_starttag(tag,attrs)
        self.parts[start]=source

def localize_admin(source,locale):
    if locale=='ht':return source
    parser=AdminLocalizer(locale);parser.feed(source);return ''.join(parser.parts)

COPY.update({
'Teste koneksyon sèvis yo': ['Tester les connexions','Test service connections','Testar conexões','Probar conexiones'],
'Rezilta tès sa a sèlman; yo pa sove.': ['Résultats de ce test uniquement ; non enregistrés.','Results for this test only; not saved.','Resultados deste teste; não salvos.','Resultados de esta prueba; no guardados.'],
'Detay konfigirasyon': ['Détails de configuration','Configuration details','Detalhes da configuração','Detalles de configuración'],
'Aksè Mux verifye.': ['Accès Mux vérifié.','Mux access verified.','Acesso Mux verificado.','Acceso Mux verificado.'],
'Aksè de bucket yo verifye; teste chajman yon foto tou.': ['Accès aux deux buckets vérifié ; testez aussi un envoi de photo.','Access to both buckets verified; also test a photo upload.','Acesso aos dois buckets verificado; teste também o envio de foto.','Acceso a ambos buckets verificado; pruebe también subir una foto.'],
'Otantifikasyon Firebase verifye; livrezon notifikasyon poko teste.': ['Authentification Firebase vérifiée ; envoi de notifications non testé.','Firebase authentication verified; notification delivery not tested.','Autenticação Firebase verificada; entrega de notificações não testada.','Autenticación Firebase verificada; entrega de notificaciones no probada.'],
'Tès la echwe. Verifye kle yo, dwa aksè ak koneksyon sèvis la.': ['Échec du test. Vérifiez les clés, les autorisations et la connexion du service.','Test failed. Check keys, permissions and service connectivity.','Teste falhou. Verifique chaves, permissões e conexão do serviço.','Prueba fallida. Revise claves, permisos y conexión del servicio.']
})

COPY.update({'Tès reyisi':['Test réussi','Test passed','Teste aprovado','Prueba exitosa'],'Tès echwe':['Échec du test','Test failed','Teste falhou','Prueba fallida']})
