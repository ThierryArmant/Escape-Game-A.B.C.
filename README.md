# Escape Game A.B.C.

Jeu pédagogique coopératif pour les collégiens : comprendre les arbitrages d'une cantine et agir contre le gaspillage alimentaire.

## Scénario de référence

[Lire le scénario cantine, version 1](docs/scenario-cantine-v1.md)

- Collège fictif de 800 élèves, 600 repas par service.
- Trois équipes : familles et élèves, gestionnaires, producteurs et fournisseurs.
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
