# Escape Game A.B.C. — parcours cantine, version 2

Le parcours actuel est `app.py` sur Streamlit. Tous les prix, rendements, quantités de restes et effets des aléas sont fictifs. Collège de 800 élèves, 600 repas par service, 30 minutes, trois équipes composées d'élèves et un maître du jeu.

## Trois rôles actifs

### Producteurs et fournisseurs
Au début, choisir conventionnel ou bio. Dans ce scénario, les rendements initiaux sont identiques ; les frais et les prix de vente du bio sont plus élevés. Cela ne constitue pas une règle sur l'agriculture réelle.

| Produit | Frais conventionnels €/kg | Vente conventionnelle €/kg | Frais bio €/kg | Vente bio €/kg |
|---|---:|---:|---:|---:|
| Pommes de terre | 0,80 | 1,20 | 1,00 | 1,40 |
| Carottes | 1,20 | 2,00 | 1,50 | 2,40 |

Dès que le chef commande, calculer une quantité disponible : pommes de terre, 4 parcelles × 30 kg = 120 kg ; carottes, 3 parcelles × 30 kg = 90 kg. Le produit demandé dépend du menu. Comparer ensuite la récolte à la quantité commandée, puis confirmer la livraison. En cas de manque, organiser le complément disponible avant de confirmer.

### Chef cuisinier
Choisir le premier menu en fonction des prix du producteur. Budget alimentaire de 1 500 € au premier repas, et de 3 000 € pour les deux services. Base fixe de 540 € incluse ; personnel et énergie hors simulation.

| Menu | Conventionnel | Bio |
|---|---:|---:|
| Poulet régional, pommes de terre, carottes | 1 440 € | 1 500 € |
| Poulet importé, riz, carottes | 1 242 € | 1 278 € |
| Lentilles, riz, carottes | 918 € | 954 € |
| Menu de réserve | 900 € | 900 € |

Après les choix du service par les élèves, résoudre deux questions successives : grammes de restes par convive, puis pourcentage jeté. La deuxième n'apparaît qu'après la réussite de la première. Le jeu affiche ensuite une estimation de la valeur des restes : coût du repas × kg jetés / 300. C'est une dépense engagée, pas une somme récupérée.

Au prochain repas, utiliser les mesures pour proposer une adaptation : présenter le plat et proposer de goûter, servir selon la faim avec complément, ou conserver le service prévu. Cette recommandation est affichée aux autres équipes ; la deuxième distribution n'est pas simulée dans cette version.

Le chef peut mobiliser un stock fictif utilisable : 12 kg de pommes de terre crues ou 9 kg de carottes crues, non servies et conservées dans des conditions adaptées. Ce stock a été acheté avant les deux repas du jeu. Il ne provient jamais des déchets des plateaux. Le menu régional utilise les pommes de terre : 108 kg à acheter au lieu de 120. Les autres menus ordinaires utilisent les carottes : 81 kg au lieu de 90. La diminution des nouveaux achats se déduit au prix du scénario ; ce n'est pas un remboursement du stock ancien. Le menu de réserve utilise son propre stock.

### Familles et élèves
D'abord, donner leur avis sur le menu proposé. Puis choisir deux éléments du service :

| Plat servi à l'assiette | Fonctionnement | Restes de base simulés |
|---|---|---:|
| Même portion pour tous | L'agent sert la même quantité ; petite et grande faim ne sont pas distinguées. | 60 kg |
| Selon la faim, avec complément | L'élève annonce son appétit ; un complément reste possible. | 36 kg |
| Selon la faim, possibilité de goûter | Le plat est présenté, l'élève peut goûter puis demander une portion adaptée. | 24 kg |

| Entrées et desserts en libre-service | Modification fictive des restes |
|---|---:|
| Prendre entrée et dessert systématiquement | 0 kg |
| Choisir selon sa faim | −6 kg |
| Goûter une petite quantité avant de choisir | −12 kg |

La masse totale servie reste fixée à 300 kg pour simplifier les calculs. Les restes deviennent 60, 54, 48, 36, 30, 24, 18 ou 12 kg selon les choix. Ces valeurs ne sont pas des effets mesurés ni une prédiction de la réalité. Le service doit toujours permettre de manger à sa faim. La possibilité de goûter demande une organisation prévue par la cantine.

## Aléas décidés par le maître
Une sécheresse ou une inondation, une seule par partie, déclenchable manuellement. Elle affecte le repas suivant et ne modifie pas rétroactivement le repas servi.

- Sécheresse : rendement des pommes de terre de 30 à 24 kg par parcelle (96 kg au total), carottes de 30 à 15 kg (45 kg au total). Le producteur recalcule, compare, puis peut mobiliser un partenaire pour les pommes de terre ou des légumes surgelés pour les carottes. Les prix affichés comprennent le surcoût du remplacement : +45 € pour le menu régional conventionnel, +9 € pour les autres menus avec carottes. En bio, seuls les achats de carottes locales encore disponibles portent le supplément bio ; le supplément bio de pommes de terre reste 24 € sur le menu régional. Le stock cru ancien peut réduire les quantités à acheter.
- Inondation : récoltes du fournisseur touché détruites, frais engagés et revenus attendus perdus. Les menus reposant sur ces récoltes ne sont plus proposés. Le fournisseur calcule son stock de légumes surgelés non touchés : 6 caisses × 15 kg = 90 kg, puis vérifie la commande de 90 kg. Le menu de réserve passe de 900 € à 1 080 € : lentilles 144 €, riz 126 €, légumes surgelés 270 €, base fixe 540 €. Hausse fictive de 20 % du repas, motivée par la rareté et la demande de substitution dans le scénario.

## Guidage et réussite
Fenêtre de prochaine action automatique à chaque véritable étape, bouton pour la rouvrir, rappel visible sur la page. Le maître ne passe à la suite que lorsque les missions nécessaires sont terminées.

Chaque calcul a sa calculatrice facultative et trois niveaux d'aide : méthode, opération avec les données, solution complète en dernier recours. Aucun point retiré ; essais illimités. Il faut saisir et vérifier la réponse pour poursuivre, même après une aide complète.

Réussite : deux services de 600 repas possibles, budget respecté, quantité du fournisseur vérifiée, choix de service enregistrés et mesures A.B.C. résolues. Bilan sur les interdépendances, les impacts du gaspillage et un geste transférable à la vraie cantine.

## Limites
A.B.C. est simulé, sans liaison à un appareil ou à une base externe. Les règles nutritionnelles et réglementaires ne sont pas modélisées. Le stock utilisable n'est pas une consigne de réemploi des restes de repas réels. Sessions partagées en mémoire : les redémarrages effacent les parties. Les codes servent à un usage de classe de confiance. L'hébergement Streamlit ne nécessite aucun appel payant à une IA.
