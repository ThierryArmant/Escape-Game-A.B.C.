# Escape Game A.B.C.

Jeu pédagogique coopératif pour les collégiens : comprendre les arbitrages d'une cantine et agir contre le gaspillage alimentaire.

## Scénario de référence

[Lire le scénario cantine, version 1](docs/scenario-cantine-v1.md)

- Collège fictif de 800 élèves, 600 repas par service.
- Trois équipes : familles et élèves, chef cuisinier, producteurs et fournisseurs.
- Séance de 30 minutes, trois manches.
- Sécheresse ou inondation déclenchée par le maître du jeu.
- Budget, catalogue, énigmes, indices et bilan A.B.C.

## État du projet

Le scénario et une première application synchronisée sont disponibles : trois vues tablette et un écran maître, avec un état partagé côté serveur. L'hébergement reste à configurer.

Les données économiques et les effets des aléas sont fictifs. Cette version n'est pas une référence réglementaire ou nutritionnelle.

## Première application jouable

Le dépôt contient désormais une première version avec écran maître, trois vues équipe, budget calculé côté serveur, mesure A.B.C., validations collectives et aléas manuels.

### Lancer

Node.js 22 ou supérieur, sans dépendance à installer :

```sh
npm start
```

Ouvrir `http://localhost:3000`. Le maître crée la partie. Les trois tablettes ouvrent l'adresse du même serveur puis rejoignent avec le code et leur rôle. Sur le réseau local, utiliser l'adresse IP de l'ordinateur hôte et le port 3000 ; le pare-feu et le réseau doivent permettre la connexion.

```sh
npm test
```

Un Dockerfile permet aussi de lancer le serveur sur un hébergeur compatible Node ou Docker. Le serveur écoute le port fourni par la variable `PORT`.

### Limites de cette première version

- Sessions en mémoire : un redémarrage du serveur les efface. Un seul processus serveur ; expiration après huit heures.
- Synchronisation par interrogation toutes les 1,5 seconde ; reconnexion conservée dans l'onglet.
- Le code de session permet de rejoindre une équipe : usage en classe de confiance, pas d'authentification nominative. Le jeton maître reste séparé et autorise seul les aléas et changements de manche.
- Les confirmations de stocks sont une mission pédagogique, avec les menus prédéfinis du scénario ; pas encore de commande ingrédient par ingrédient.
- Mesures simulées, sans connexion automatique à l'application A.B.C.
- Le bouton du maître passe les manches lorsque les validations sont complètes ; les indices n'outrepassent pas ces validations.
- Aucun hébergement public n'a encore été configuré. GitHub Pages seul ne permet pas les sessions synchronisées.

Les données réglementaires et nutritionnelles restent à documenter avant leur ajout au jeu.

## Hébergement gratuit avec Streamlit Community Cloud

Une version Python du jeu est disponible dans `app.py`. Elle partage les parties entre les écrans avec un cache serveur global protégé par verrou et actualise les vues toutes les deux secondes.

Dans Streamlit Community Cloud, créer une application avec :

- Dépôt : `ThierryArmant/Escape-Game-A.B.C.`
- Branche : `main`
- Fichier principal : `app.py`
- Python : 3.12
- Aucun secret nécessaire pour cette première version.

Localement : `pip install -r requirements.txt` puis `streamlit run app.py`.

Une seule application hébergée suffit pour le maître et les trois équipes. Tous ouvrent la même URL puis rejoignent le même code de partie. Le code est un accès de classe de confiance, pas une authentification personnelle. Ne saisissez pas de données nominatives.

Les parties sont conservées en mémoire : un redémarrage, une mise en veille ou une mise à jour du serveur peut les effacer. Quitter puis rejoindre est possible tant que le serveur conserve la partie ; le rôle maître est conservé seulement dans sa session navigateur. La fluidité doit être vérifiée avec les quatre appareils après publication. Cette version ne nécessite aucun appel payant à une IA.

Tests du moteur Python : `python -m unittest discover -s tests -p 'test_*.py'`.

## Parcours pédagogique actuel — version 2

La version Streamlit `app.py` est le parcours actuel. La première version Node reste dans le dépôt comme prototype antérieur ; elle ne contient pas ces nouvelles missions.

[Scénario et règles de la version 2](docs/scenario-cantine-v2.md)

- Producteurs : choix de production bio ou conventionnelle, calcul de récolte, comparaison avec la commande, complément si nécessaire.
- Familles et élèves : plat servi à l’assiette selon la faim, possibilité de goûter et choix d’entrées/desserts en libre-service.
- Chef cuisinier : choix de menu, calculs du gaspillage un par un, coût estimé des restes et adaptation du prochain repas.
- Aide progressive sans pénalité et calculatrice facultative. Les solutions complètes apparaissent seulement au troisième niveau d’aide.
- Un changement de commande demande une nouvelle vérification de récolte et de nouveaux accords. Un changement de service annule les mesures précédentes.

La mise à jour du serveur peut effacer une partie en cours : créer une nouvelle partie pour tester cette version.

## Version actuelle : décisions et réactions sur deux journées

[Scénario v3](docs/scenario-cantine-v3.md) — il remplace les parcours v1 et v2.

- Courtier en alimentation : choix des offres et préparation des deux livraisons.
- Chef cuisinier : deux menus préparés à l’avance ; budget, variété et conséquences affichés.
- Familles et élèves : choix de service à chaque journée, avec 30 minutes de pause.
- Aucun calcul à saisir : les résultats se mettent à jour selon les décisions.
- Les manches avancent automatiquement lorsque les accords sont obtenus et que le chef a pris connaissance du bilan.
- Après le jour 1 : pause commune illustrée sur quatre écrans, reprise par le maître, sécheresse automatique et adaptation du jour 2.
- Comparaison des deux journées en fin de partie.

Les prix sont des hypothèses, pas des cotations réelles. Les cartes carbone donnent des repères qualitatifs, pas une empreinte mesurée par fournisseur.
