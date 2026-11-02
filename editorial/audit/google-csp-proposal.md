# Ajustement CSP Google — autorisé par le propriétaire

Le propriétaire a explicitement autorisé cet ajustement dans la conversation, après explication de ses effets. Les deux autorisations ci-dessous sont ajoutées ; leur déploiement fait l’objet de contrôles HTTP et navigateur.

## Modification exacte proposée

Dans l’en-tête `Content-Security-Policy` construit par `main.py` :

- Ajouter uniquement `https://ep1.adtrafficquality.google` à `connect-src`.
- Ajouter uniquement `https://ep2.adtrafficquality.google` à `script-src`.
- Conserver toutes les autres directives et origines existantes, sans joker supplémentaire.

Le script de vérification AdSense déjà présent demande une configuration à la première origine, puis un script auxiliaire à la seconde. Le navigateur a permis d’observer ces requêtes. Un essai limité à une réponse modifiée dans le navigateur de contrôle, sans changement du serveur, a permis de charger ces deux ressources sans erreur JavaScript ni violation CSP.

L’ajout permettrait au navigateur de communiquer avec la première origine et d’exécuter du code tiers fourni par la seconde sur les pages chargeant le script AdSense. Il ne déclenche pas l’activation des emplacements publicitaires, ne configure pas une CMP et ne garantit pas l’approbation AdSense.

La revue automatique d’approbation a rejeté la modification persistante, au motif que l’objectif d’audit n’autorisait pas explicitement cet élargissement d’une frontière de sécurité en production. L’ajustement partiel de `connect-src` a donc été retiré ; les réparations éditoriales restent en place. Le propriétaire a ensuite donné son autorisation explicite : « ebyen fe sa ». Cette autorisation permet maintenant d’appliquer les deux changements précisément décrits.

## Vérification après déploiement

Les deux origines sont présentes dans les directives prévues sur le domaine public. Six tests concernés ont passé. Sur la page d’accueil française et un article portugais, aux largeurs 1440 et 390 pixels, Chromium a observé les deux ressources Google en HTTP 200, sans erreur JavaScript ni requête bloquée. Les réponses du site n’ont pas été interceptées ou modifiées pour cette vérification finale.
