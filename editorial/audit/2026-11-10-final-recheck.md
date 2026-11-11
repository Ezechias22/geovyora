# Nouvelle vérification publique à la demande du propriétaire

## Périmètre et résultats

- 120 URL du sitemap, puis 150 URL internes distinctes découvertes dans les liens de ces pages : toutes accessibles après les redirections attendues, aucune erreur HTTP.
- Neuf ressources locales uniques référencées (scripts, styles et images) : HTTP 200.
- Pour les 120 pages du sitemap : langue HTML attendue, un titre h1, URL canonique présente, pas de noindex involontaire ni de bannière de traduction de secours. Cela ne constitue pas une nouvelle vérification de chaque affirmation ou de toutes les références externes.
- Huit contrôles d'accueil : fr/en/pt-BR/es × mobile 390 px/ordinateur 1365 px. Aucun débordement horizontal, image chargée défectueuse ou fuite des expressions d'interface créoles recherchées. Menu mobile ouvert/fermé ; changement de français vers portugais sur un article confirmé ; formulaire de contact vide correctement invalide, sans envoyer de message.

## Problème découvert et corrigé

L'ancien contrôle ne recueillait que les exceptions JavaScript ; cette vérification examine aussi les messages CSP de la console. Le script Google de vérification tentait d'ouvrir deux cadres bloqués par la politique `frame-src` :

- `https://ep2.adtrafficquality.google/sodar/sodar2/257/runner.html`
- `https://www.google.com/recaptcha/api2/aframe`

Le commit `c8a207a` autorise uniquement les chemins nécessaires : `https://ep2.adtrafficquality.google/sodar/` et `https://www.google.com/recaptcha/api2/aframe`. Aucun joker de domaine supplémentaire, autorisation globale HTTPS, script inline ou nouvelle permission connect-src n'est ajouté. Les chemins des cadres Google réellement présents dans le DOM ont été examinés avant ce changement ; les paramètres de requête ne sont pas conservés dans les résultats.

Sept tests pertinents passent, dont un nouveau test qui vérifie la limitation aux chemins observés et le maintien des restrictions de script, d'objet et de formulaire. Après déploiement, huit nouvelles sessions Chromium couvrent les quatre langues et deux tailles d'écran : le document `runner.html` et le document `aframe` répondent HTTP 200, aucune violation CSP ni exception JavaScript observée, aucun débordement horizontal.

Le script de vérification AdSense reste installé ; les emplacements publicitaires restent désactivés. Ce correctif ne prouve pas que ces blocages étaient la cause du refus de qualité et ne garantit pas une approbation. Les limites concernant les références externes, les droits des médias et l'appréciation éditoriale restent celles du rapport précédent.

Les résultats sont conservés dans `2026-11-10-recheck-results.json`. Aucune photo, information de contact, date d'article ou publication existante n'a été remplacée lors de cette vérification.
