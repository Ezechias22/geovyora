# Préparation éditoriale et AdSense — 2 novembre 2026

Trois guides originaux sont disponibles dans `drafts/`. Ce sont des contenus de fond préparés avec une assistance IA, à relire ; ils ne sont pas présentés comme des nouvelles du jour, des interviews ou des enquêtes de terrain. Aucun revenu ni accord AdSense n’est garanti.

Depuis `/workspace/geovyora`, `.venv/bin/python import_editorial_drafts.py --apply` les importe dans la base configurée, avec le statut **draft**. La commande ne publie rien, ne remplace aucun article existant et peut être relancée. Sans `--apply`, elle ne modifie pas la base. Avant toute utilisation sur une autre machine, vérifier la base ciblée et disposer d’une sauvegarde adaptée. Le compte administrateur peut ensuite les relire dans le CMS, les compléter et choisir de les publier. Les contenus existants, dont Ariana et Haytiles, doivent être conservés.

## Travail technique préparé

- `/ads.txt` autorise l’éditeur `pub-2023569258267325` indépendamment de l’activation des annonces. Le réglage CMS `publisher_id` est prioritaire ; `ADSENSE_PUBLISHER_ID` permet une substitution pour une autre installation. Les identifiants mal formés sont refusés. Le script de vérification utilise le même identifiant.
- La méthode éditoriale est détaillée en français, anglais, portugais et espagnol : sources, indépendance, droits, IA, corrections et limites.
- La page de présentation identifie Geovyora comme un projet de Haytiles, selon l’information fournie par le propriétaire. Le nom de responsable, l’adresse et l’email configurés dans le CMS s’affichent lorsqu’ils sont renseignés. Aucun contact n’est inventé.
- Une incohérence de ponctuation dans la présentation anglaise des propositions de créateurs est corrigée.

## Recherche d’actualité et vérification externe

L’accès réseau a été débloqué le 2 novembre 2026. Trois articles d’actualité documentés sont enregistrés dans `news/2026-11-02.json` : sécurité dans les campagnes, prévision alimentaire de mars–juin 2027 et participation salvadorienne. Les sources consultées et leurs dates figurent dans `news/SOURCES.md`. La migration 017 les publie en français sans remplacer de contenu existant. Les trois guides du dossier `drafts/` restent des brouillons distincts.

Pour les prochains articles : conserver les liens des documents effectivement consultés, leurs dates de publication et de consultation, distinguer l’annonce de sa réalisation, identifier les déclarations d’entreprise, vérifier les droits des images et la traduction. Privilégier un sujet cohérent avec les créateurs, la culture et la diaspora plutôt que remplir le site de nouvelles sans lien éditorial.

## Mise en ligne

Ces changements locaux ne mettent pas à jour le site public. Utiliser le service existant et sa procédure habituelle, sans recréer la stack Render ni remplacer sa base. Après déploiement, contrôler `/ads.txt`, les quatre versions de `/editorial`, `/about`, le formulaire de contact, les articles et le sitemap sur le domaine public. Relire les contenus réellement publiés, retirer les démonstrations et compléter les informations d’entreprise avant de demander un nouvel examen dans AdSense.

L’activation des annonces et la CMP restent distinctes de la déclaration ads.txt. Ne pas activer les annonces pour contourner un refus de qualité. Ne demander le réexamen qu’après vérification des corrections sur le site public.
