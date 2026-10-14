"""Moteur coopératif sans dépendance ; état partagé protégé par verrou."""
import copy
import secrets
import threading
import time

MENUS = {
    'abc_cantine': ('Paupiette de bœuf, chou-fleur en gratin, pommes noisettes · A.B.C.', 1380),
    'boeuf_bresil': ('Bœuf brésilien, pommes de terre, carottes', 1260),
    'boeuf_argentine': ('Bœuf argentin, pommes de terre, carottes', 1314),
    'porc_ventoux': ('Porc du Ventoux, pommes de terre, carottes', 1368),
    'poisson': ('Colin, riz, carottes · référence lieu jaune cru', 1350),
    'boeuf': ('Bœuf, pommes de terre, carottes', 1620),
    'regional': ('Poulet régional, pommes de terre, carottes', 1440),
    'importe': ('Poulet importé, riz, carottes', 1242),
    'vegetal': ('Lentilles, riz, carottes', 918),
    'secours': ('Lentilles, riz de réserve, légumes surgelés', 900),
}
CRISIS_RECIPES = {'chou_veloute': ('Velouté de chou-fleur, lentilles et pain', 960), 'chou_puree': ('Poulet, purée chou-fleur et pommes de terre', 1260), 'chou_galettes': ('Galettes de chou-fleur et lentilles, riz', 1020)}
MENUS.update(CRISIS_RECIPES)

SERVICES = {'unique': ('Portion unique', 60), 'adapte': ('Petite portion et complément', 36), 'explique': ('Portion adaptée et recette présentée', 24)}
ROLES = {'master': 'Maître du jeu', 'students': 'Familles et élèves', 'manager': 'Chef cuisinier', 'supplier': 'Responsable des achats'}

BEEF = {'boeuf', 'boeuf_bresil', 'boeuf_argentine'}
POTATO = BEEF | {'regional', 'porc_ventoux'}
ANIMAL = POTATO | {'importe', 'poisson'}

PRODUCTION = {
    'conventionnel': {'name': 'Production conventionnelle', 'potato_price': 1.20, 'carrot_price': 2.00, 'potato_cost': .80, 'carrot_cost': 1.20},
    'bio': {'name': 'Production biologique', 'potato_price': 1.40, 'carrot_price': 2.40, 'potato_cost': 1.00, 'carrot_cost': 1.50},
}
SERVICE_LABELS = {'unique': 'Même portion de plat pour tous', 'adapte': 'Plat selon la faim, avec complément', 'explique': 'Plat selon la faim, possibilité de goûter'}
SELF_SERVICE = {'tout': ('Prendre entrée et dessert systématiquement', 0), 'faim': ('Choisir entrée et dessert selon sa faim', -6), 'gouter': ('Goûter une petite quantité avant de choisir', -12)}

CRISIS_OFFERS = {'espagne': 135, 'argentine': 450, 'reserve': 0}

def crisis_cost(recipe, offer):
    if recipe not in CRISIS_RECIPES or offer not in CRISIS_OFFERS:
        raise ValueError('Choix inconnu.')
    # Le bœuf remplace le poulet dans la purée : une seule facturation.
    base = CRISIS_RECIPES[recipe][1] - (576 if recipe == 'chou_puree' and offer == 'argentine' else 0)
    return base + CRISIS_OFFERS[offer]

def cost(menu, event=None, mode='conventionnel', reuse=False, beef_source='regional'):
    if menu in CRISIS_RECIPES and mode in PRODUCTION:
        return CRISIS_RECIPES[menu][1]
    if menu not in MENUS or mode not in PRODUCTION:
        raise ValueError('Choix inconnu.')
    if event == 'inondation' and menu != 'secours':
        raise ValueError('Récoltes détruites : choisissez les produits de réserve.')
    extra = (60 if menu in POTATO else 36) if mode == 'bio' and menu != 'secours' else 0
    # En sécheresse : seule une demi-récolte de carottes est achetée au producteur.
    if event == 'secheresse' and mode == 'bio' and menu != 'secours':
        extra = 18 + (24 if menu in POTATO else 0)
    saving = stock_saving(menu, event, mode) if reuse else 0
    return round(MENUS[menu][1] - (204 if menu == 'boeuf' and beef_source == 'importe' else 0) + extra + (180 if event == 'inondation' else 0) + (9 + (36 if menu in POTATO else 0) if event == 'secheresse' and menu != 'secours' else 0) - saving, 2)

def stock_saving(menu, event, mode):
    if menu == 'secours':
        return 0
    if menu in POTATO:
        return 12 * (PRODUCTION[mode]['potato_price'] + (.30 if event == 'secheresse' else 0))
    return 9 * PRODUCTION[mode]['carrot_price']

def harvest(s):
    if s.get('crisis_recipe') and s['phase'] == 3:
        return {'name': 'Chou-fleur cru non servi en stock', 'plots': 6, 'yield': 15, 'quantity': 90, 'unit': 'caisses', 'need': 90}
    selected = [s.get('first'), s.get('second')] if s['phase'] == 1 else [s.get('second')]
    abc_count = sum(bool(m and m['id'] == 'abc_cantine') for m in selected)
    if abc_count:
        return {'name': 'Produits préparés du menu A.B.C.', 'plots': abc_count, 'yield': 282, 'quantity': 282 * abc_count, 'unit': 'lots', 'need': 282 * abc_count}
    event = s['event'] if s['phase'] == 3 else None
    if s['phase'] == 1:
        return {'name': 'Carottes pour les deux journées', 'plots': 6, 'yield': 30, 'quantity': 180, 'unit': 'caisses', 'need': 180}
    planned = s['second']
    if event == 'inondation' or planned and planned['id'] == 'secours':
        return {'name': 'Légumes surgelés de réserve', 'plots': 6, 'yield': 15, 'quantity': 90, 'unit': 'caisses', 'need': 90}
    potato = s['first' if s['phase'] == 1 else 'second']
    if potato and potato['id'] in POTATO:
        y = 24 if event == 'secheresse' else 30
        return {'name': 'Pommes de terre', 'plots': 4, 'yield': y, 'quantity': 4 * y, 'unit': 'parcelles', 'need': 108 if s['phase'] == 3 and potato.get('reuse') else 120}
    y = 15 if event == 'secheresse' else 30
    return {'name': 'Carottes', 'plots': 3, 'yield': y, 'quantity': 3 * y, 'unit': 'parcelles', 'need': 81 if s['phase'] == 3 and potato and potato.get('reuse') else 90}

def requirements(s):
    quantities = {'Carottes': 0, 'Pommes de terre': 0, 'Poulet': 0, 'Bœuf': 0, 'Porc': 0, 'Poisson': 0, 'Lentilles sèches': 0, 'Riz sec': 0, 'Légumes surgelés': 0, 'Paupiettes préparées': 0, 'Chou-fleur en gratin': 0, 'Pommes noisettes': 0}
    menus = [s['first'], s['second']] if s['phase'] == 1 else [s['second']]
    for menu in menus:
        if not menu:
            continue
        m = menu['id']
        if m in CRISIS_RECIPES:
            quantities.setdefault('Chou-fleur cru du stock non servi', 0)
            quantities['Chou-fleur cru du stock non servi'] += 90
            protein = 'Bœuf' if m == 'chou_puree' and s.get('crisis_offer') == 'argentine' else 'Poulet' if m == 'chou_puree' else 'Lentilles sèches'
            quantities[protein] += 72 if m == 'chou_puree' else 36
            quantities['Pommes de terre' if m == 'chou_puree' else 'Riz sec'] += 120 if m == 'chou_puree' else 36
            continue
        if m == 'abc_cantine':
            quantities['Paupiettes préparées'] += 72
            quantities['Chou-fleur en gratin'] += 90
            quantities['Pommes noisettes'] += 120
            continue
        if m in ('regional', 'importe'):
            quantities['Poulet'] += 72
        elif m in BEEF:
            quantities['Bœuf'] += 72
        elif m == 'porc_ventoux':
            quantities['Porc'] += 72
        elif m == 'poisson':
            quantities['Poisson'] += 72
        else:
            quantities['Lentilles sèches'] += 36
        if m in POTATO:
            quantities['Pommes de terre'] += 108 if menu.get('reuse') else 120
        else:
            quantities['Riz sec'] += 36
        if m == 'secours':
            quantities['Légumes surgelés'] += 90
        else:
            quantities['Carottes'] += 81 if menu.get('reuse') and m not in POTATO else 90
    return {k: v for k, v in quantities.items() if v}

def waste(s):
    if not s['service']:
        return None
    menu = s.get('first' if s['phase'] == 2 else 'second')
    # Scenario portions; rejection rates from ABC scans, not college-wide measurements.
    baseline = round(72 * .33 + 90 * .74 + 120 * .13) if menu and menu['id'] == 'abc_cantine' else 60
    simulated = round(baseline * SERVICES[s['service']][1] / 60)
    return max(0, simulated + SELF_SERVICE[s.get('self_service', 'tout')][1])

def initial():
    return dict(session_since=None, drought_discussed=False, crisis_pause=False, crisis_offer=None, crisis_recipe=None, first_effect_shown=False, waste_policy={}, game_started=False, active_elapsed=0, active_since=None, reflection=None, notices=[], preferences=None, final_card_visible=False, debate_votes={}, debate_decision=None, waste_reviewed=False, climate_ack=False, animal_offer='boeuf', beef_source='regional', meat_source=None, original_second=None, reviewed=False, day1=None, day2=None, phase=1, event=None, started=time.time(), hint=False, first=None, second=None, service=None, self_service='tout', measure=False, grams_done=False, production=None, harvest_done=False, supply_done=False, supply_strategy=None, approvals={'supplier': False, 'students': False})

def reset_supply(s):
    ready = bool(s['first'] and s['second']) and (s['phase'] == 1 or s['reviewed'])
    h = harvest(s) if ready else None
    s.update(harvest_done=ready, supply_done=ready, supply_strategy='direct' if h and h['quantity'] >= h['need'] else None)
    s['approvals'] = {'supplier': False, 'students': False}

def apply_core(s, role, action, **values):
    if role == 'master':
        if action == 'event':
            event = values.get('value')
            if event not in ('secheresse', 'inondation') or s['event'] or s['phase'] not in (1, 2, 3):
                raise ValueError('Un seul aléa par partie.')
            s['active_elapsed'] = elapsed(s)
            s.update(event=event, reviewed=False, crisis_pause=True, active_since=None)
            if s['phase'] == 3:
                reset_supply(s)
        elif action == 'crisis_resume':
            if not s.get('crisis_pause'):
                raise ValueError('Aucune discussion climatique en cours.')
            s.update(crisis_pause=False, drought_discussed=True, climate_ack=True, active_since=time.time())
        elif action == 'climate_resume':
            if s['phase'] != 3:
                raise ValueError('La pause apparaît après le premier repas.')
            s['climate_ack'] = True
        elif action == 'show_final_card':
            if s['phase'] == 4:
                apply(s, 'master', 'next')
            if s['phase'] != 5:
                raise ValueError('Cette carte se partage après le deuxième repas.')
            s['final_card_visible'] = True
        elif action == 'debate_close':
            if s['phase'] != 5 or len(s.get('debate_votes', {})) != 3 or values.get('value') not in ('A', 'B', 'C', 'D', 'E'):
                raise ValueError('Les trois équipes doivent proposer leur choix avant la décision collective.')
            s['debate_decision'] = values['value']
        elif action == 'hint':
            s['hint'] = True
        elif action == 'next':
            p = s['phase']
            if p == 1 and 'first_effect_shown' in s and not s['first_effect_shown']:
                raise ValueError('Attendez les choix de toutes les équipes et la lecture commune des effets n°1.')
            if p == 3 and not s['climate_ack']:
                raise ValueError('Terminez la pause commune avant de poursuivre.')
            if p in (1, 3) and (not s['first'] or not s['second'] or not all(s['approvals'].values()) or p == 3 and not s['reviewed']):
                raise ValueError('Les trois équipes ont encore une mission à terminer.')
            if p in (2, 4) and not s['waste_reviewed']:
                raise ValueError('Le chef cuisinier termine les deux petits calculs avant la suite.')
            if p in (2, 4):
                field = 'first' if p == 2 else 'second'
                s['day1' if p == 2 else 'day2'] = {'waste': waste(s), 'cost': s[field]['cost'], 'service': s['service'], 'self_service': s['self_service']}
            s['phase'] = min(5, p + 1)
            s['hint'] = False
            if s['phase'] == 3:
                s['climate_ack'] = s.get('drought_discussed', False) or not s['event']
                reset_supply(s)
                s['reviewed'] = False
            if s['phase'] == 4:
                s.update(service=None, self_service='tout', grams_done=False, measure=False, waste_reviewed=False)
        else:
            raise ValueError('Action inconnue.')
        return
    if s['phase'] == 3 and not s['climate_ack']:
        raise ValueError('Lisez les cartes : le maître du jeu va reprendre la mission.')
    if action == 'debate' and s['phase'] == 5 and role in ('students', 'manager', 'supplier'):
        if values.get('value') not in ('A', 'B', 'C', 'D', 'E') or values.get('reason') not in ('Budget de la cantine', 'Émissions de gaz à effet de serre', 'Lien avec les producteurs proches', 'Variété des repas', 'Informations et traçabilité'):
            raise ValueError('Choisissez une proposition et un argument.')
        s.setdefault('debate_votes', {})[role] = {'choice': values['value'], 'reason': values['reason']}
        s['debate_decision'] = None
        return
    if action == 'production' and role == 'supplier' and s['phase'] == 1:
        mode = values.get('value')
        if mode not in PRODUCTION:
            raise ValueError('Choisissez un mode de production.')
        if s['production'] == mode:
            return
        source = values.get('source', 'regional')
        if source not in ('regional', 'importe'):
            raise ValueError('Choisissez une origine pour la viande.')
        s['production'] = mode
        s['meat_source'] = source
        s['animal_offer'] = values.get('animal_offer', 'boeuf')
        if s['animal_offer'] not in BEEF | {'porc_ventoux', 'poisson'}:
            raise ValueError('Offre inconnue.')
        s['beef_source'] = values.get('beef_source', 'regional')
        if s['beef_source'] not in ('regional', 'importe'):
            raise ValueError('Offre de bœuf inconnue.')
        for key in ('first', 'second'):
            if s[key]:
                s[key]['cost'] = cost(s[key]['id'], mode=mode, beef_source=s['beef_source'])
        reset_supply(s)
    elif action == 'plans' and role == 'manager' and s['phase'] == 1:
        first, second = values.get('first'), values.get('second')
        allowed = tuple(k for k in MENUS if k != 'secours')
        if first not in allowed or second not in allowed:
            raise ValueError('Choisissez deux menus du catalogue publié par le courtier.')
        c1, c2 = cost(first, mode=s['production'] or 'conventionnel', beef_source=s['beef_source']), cost(second, mode=s['production'] or 'conventionnel', beef_source=s['beef_source'])
        s['first'] = {'id': first, 'cost': c1, 'reuse': False, 'adaptation': None}
        s['second'] = {'id': second, 'cost': c2, 'reuse': False, 'adaptation': None}
        s['original_second'] = copy.deepcopy(s['second'])
        reset_supply(s)
    elif action == 'menu' and role == 'manager' and s['phase'] == 3:
        if not s['production']:
            raise ValueError('Le producteur choisit d’abord son mode de production. Les prix seront alors disponibles.')
        menu = values.get('value')
        reuse = bool(values.get('reuse')) and s['phase'] == 3
        price = cost(menu, s['event'] if s['phase'] == 3 else None, s['production'], reuse, s['beef_source'])
        if s['phase'] == 1 and (menu == 'secours' or price > 1500):
            raise ValueError('Choisissez un menu ordinaire dans le budget.')
        if s['phase'] == 3 and price + s['first']['cost'] > 3000:
            raise ValueError('Ce menu dépasse le budget des deux repas. Essayez une autre recette : aucune pénalité.')
        s['first' if s['phase'] == 1 else 'second'] = {'id': menu, 'cost': price, 'reuse': reuse, 'adaptation': values.get('adaptation') if s['phase'] == 3 else None}
        s['reviewed'] = s['phase'] == 3
        reset_supply(s)
    elif action == 'harvest' and role == 'supplier' and s['phase'] in (1, 3):
        if not s['first'] or not s['second'] or s['phase'] == 3 and not s['reviewed']:
            raise ValueError('Attendez la commande du chef cuisinier.')
        h = harvest(s)
        if values.get('answer') != h['quantity']:
            raise ValueError('Essayez encore : multipliez le nombre de ' + h['unit'] + ' par les kilogrammes de chacune. Vous pouvez ouvrir l’aide.')
        s['harvest_done'] = True
    elif action == 'supply' and role == 'supplier' and s['phase'] in (1, 3):
        if not s['harvest_done']:
            raise ValueError('Calculez d’abord votre récolte disponible.')
        h = harvest(s)
        enough = h['quantity'] >= h['need']
        if values.get('value') != ('oui' if enough else 'non'):
            raise ValueError('Comparez la récolte disponible avec la commande. Vous pouvez demander une aide, sans pénalité.')
        s['supply_done'] = True
        s['supply_strategy'] = 'direct' if enough else None
    elif action == 'strategy' and role == 'supplier' and s['phase'] in (1, 3):
        if not s['supply_done'] or s['supply_strategy']:
            raise ValueError('Cette étape n’est pas disponible.')
        if values.get('value') != 'complement':
            raise ValueError('Pour fournir tout le repas, choisissez le complément disponible.')
        s['supply_strategy'] = 'complement'
    elif action == 'approve' and role in ('supplier', 'students') and s['phase'] in (1, 3):
        if not s['first'] or not s['second'] or s['phase'] == 3 and not s['reviewed']:
            raise ValueError('Attendez la proposition du chef cuisinier.')
        if s['first']['cost'] + s['second']['cost'] > 3000:
            raise ValueError('Les deux menus dépassent le budget. Le chef doit revoir sa prévision avant de commander.')
        if role == 'supplier' and not (s['production'] and s['harvest_done'] and s['supply_done'] and s['supply_strategy']):
            raise ValueError('Terminez votre calcul et la vérification de la commande avant de confirmer.')
        s['approvals'][role] = True
    elif action == 'service' and role == 'students' and s['phase'] in (2, 4):
        if values.get('value') not in SERVICES or values.get('self_service') not in SELF_SERVICE:
            raise ValueError('Choisissez le service du plat et le libre-service.')
        s.update(service=values['value'], self_service=values['self_service'], measure=True, grams_done=True, waste_reviewed=False)
    elif action == 'review_waste' and role == 'manager' and s['phase'] in (2, 4):
        if not s['service']:
            raise ValueError('Attendez les choix des convives.')
        s['waste_reviewed'] = True
    elif action == 'grams' and role == 'manager' and s['phase'] in (2, 4):
        if not s['service']:
            raise ValueError('Attendez le choix du service.')
        if values.get('answer') != waste(s) * 1000 / 600:
            raise ValueError('Pas encore : convertissez les kg en grammes, puis partagez entre les 600 convives. Ouvrez l’aide pour avancer.')
        s['grams_done'] = True
    elif action == 'percent' and role == 'manager' and s['phase'] in (2, 4):
        if not s['grams_done']:
            raise ValueError('Terminez d’abord la question des grammes par élève.')
        if values.get('answer') != waste(s) / 3:
            raise ValueError('Essayez encore : divisez les kg de restes par les 300 kg servis, puis multipliez par 100. L’aide est disponible.')
        s['measure'] = True
    else:
        raise ValueError('Action non disponible pour votre rôle.')

def elapsed(s, now=None):
    now = time.time() if now is None else now
    if 'game_started' not in s:
        return max(0, now - s['started'])
    return s.get('active_elapsed', 0) + (max(0, now - s['active_since']) if s.get('active_since') else 0)

REFLECTIONS = {
    'valorisation': ('supplier', 'Les biodéchets ont une destination', 'L’équipe achats propose une filière pour les biodéchets triés.', 'Compostage ou méthanisation valorisent les restes. Cela ne rembourse ni le repas acheté ni toutes les ressources utilisées : éviter de jeter reste prioritaire.', 'waste'),
    'preferences': ('students', 'Vos envies deviennent une demande', 'Le courtier et le chef voient les deux menus souhaités.', 'Choisir un plat engage des achats, un budget et des ressources. Une envie peut-elle être satisfaite tous les jours ?', 'cattle'),
    'production': ('supplier', 'Le courtier publie ses offres', 'Les prix des deux menus sont mis à jour avec le choix bio ou conventionnel.', 'Le prix seul ne raconte pas tout : origine, pratiques et traçabilité comptent aussi. Que faudrait-il demander au fournisseur ?', 'farm'),
    'plans': ('manager', 'Deux menus deviennent deux commandes', 'Le courtier reçoit les quantités nécessaires ; les élèves peuvent valider les repas.', 'Comparez le coût et la variété. Deux repas au bœuf utilisent davantage de budget et ont une empreinte climatique élevée par rapport au poulet, à poids égal.', 'cattle'),
    'menu': ('manager', 'Le deuxième menu est adapté', 'La nouvelle commande tient compte de la sécheresse et du stock utilisable.', 'Utiliser les réserves et modifier la recette aide à continuer le service. Les déchets de plateaux ne sont pas réutilisés.', 'drought'),
    'service': ('students', 'Le service change les restes', 'Les restes simulés et leur valeur sont maintenant visibles au chef.', 'Une petite portion avec complément peut éviter de jeter. Le temps de passage compte aussi : il faut garder du temps pour manger.', 'waste'),
    'review_waste': ('manager', 'La mesure A.B.C. guide la suite', 'Le chef a pris en compte la nourriture achetée mais non mangée.', 'Jeter gaspille aussi les ressources utilisées avant le plateau. Un repas jeté ne provoque pas à lui seul une sécheresse.', 'waste'),
    'strategy': ('supplier', 'Une récolte insuffisante oblige à remplacer', 'Le courtier organise le complément ; le surcoût est inclus dans le menu.', 'La sécheresse fragilise les récoltes. Réserves, partenaires et recettes adaptables donnent plusieurs moyens de réagir.', 'drought'),
    'approve': (None, 'Une équipe confirme le repas', 'Son accord apparaît sur tous les écrans.', 'Le même repas doit pouvoir être fourni, payé et mangé. Pourquoi l’accord de chaque équipe est-il utile ?', 'farm'),
}

def apply(s, role, action, **values):
    if action == 'reset_game' and role == 'master':
        s.clear()
        s.update(initial())
        return
    if action == 'start_game' and role == 'master':
        if s.get('game_started', True):
            raise ValueError('La partie a déjà commencé.')
        s.update(game_started=True, session_since=time.time(), active_since=time.time())
        return
    if action == 'resume_reflection' and role == 'master':
        if not s.get('reflection'):
            raise ValueError('Aucune pause de lecture en cours.')
        s.update(reflection=None, active_since=time.time())
        return
    if not s.get('game_started', True):
        raise ValueError('Le maître du jeu lancera la partie après la lecture des fiches.')
    if s.get('crisis_pause') and not (role == 'master' and action == 'crisis_resume'):
        raise ValueError('Discussion climatique : seul le maître du jeu peut reprendre le jeu.')
    if s.get('reflection'):
        raise ValueError('Pause de lecture : le maître du jeu reprend ensuite le jeu.')
    if action == 'crisis_offer' and role == 'supplier' and s['phase'] == 3 and s['event'] == 'secheresse':
        if values.get('value') not in CRISIS_OFFERS or s.get('crisis_recipe') or not s['climate_ack']:
            raise ValueError('Choisissez une offre avant la recette du chef.')
        s['crisis_offer'] = values['value']
        s['reviewed'] = False
        reset_supply(s)
        return
    if action == 'crisis_recipe' and role == 'manager' and s['phase'] == 3 and s['event'] == 'secheresse':
        recipe = values.get('value')
        if recipe not in CRISIS_RECIPES or not s.get('crisis_offer') or not s['climate_ack']:
            raise ValueError('Attendez le choix des achats et la reprise du maître du jeu.')
        # Toute tomate achetée reste payée même si elle n’entre pas dans cette recette.
        price = crisis_cost(recipe, s['crisis_offer'])
        if s['first']['cost'] + price > 3000:
            raise ValueError('Cette recette dépasse le budget. Essayez une autre préparation.')
        s['crisis_recipe'] = recipe
        name = CRISIS_RECIPES[recipe][0]
        if recipe == 'chou_puree' and s['crisis_offer'] == 'argentine':
            name = name.replace('Poulet', 'Bœuf argentin')
        s['second'] = {'id': recipe, 'display_name': name, 'cost': price, 'reuse': False, 'adaptation': name + ' · Stock cru non servi transformé. Effet sur les rejets à tester.'}
        s['reviewed'] = True
        reset_supply(s)
        s.update(harvest_done=True, supply_done=True, supply_strategy='direct')
        s['approvals']['supplier'] = True
        return
    if s['phase'] == 3 and s['event'] == 'secheresse' and action == 'menu':
        raise ValueError('Choisissez la mission chou-fleur sans tomate.')
    if action == 'valorisation' and role == 'supplier' and s['phase'] in (2, 4):
        if values.get('value') not in ('compostage', 'methanisation'):
            raise ValueError('Choisissez une filière proposée.')
        s.setdefault('waste_policy', {})[str(s['phase'])] = values['value']
    elif action == 'preferences' and role == 'students' and s['phase'] == 1:
        choices = [values.get('first'), values.get('second')]
        if any(k not in MENUS or k == 'secours' for k in choices):
            raise ValueError('Choisissez deux menus du catalogue.')
        s['preferences'] = choices
    else:
        apply_core(s, role, action, **values)
    if s['phase'] == 5 and s.get('active_since'):
        s['active_elapsed'] = elapsed(s)
        s['active_since'] = None
    if s['phase'] == 1 and action in REFLECTIONS:
        _, title, effect, question, photo = REFLECTIONS[action]
        s.setdefault('notices', []).append({'action': action, 'role': role, 'title': title, 'effect': effect, 'question': question, 'photo': photo, 'number': len(s.get('notices', [])) + 1})
        s['notices'] = s['notices'][-30:]
        ready = bool(s.get('preferences') and s['production'] and s['first'] and s['second'] and all(s['approvals'].values()))
        if ready and not s.get('first_effect_shown'):
            s['first_effect_shown'] = True
            note = {'action': 'plans', 'role': 'master', 'title': 'Effets n°1 · Les trois équipes ont choisi', 'effect': 'Les menus, les achats et l’avis des élèves sont validés. Regardons ensemble leurs conséquences.', 'question': 'Que mobilise notre repas avant d’arriver dans l’assiette ? Que perd-on lorsqu’il est jeté ?', 'photo': 'waste', 'number': 1}
            s['active_elapsed'] = elapsed(s)
            s.update(active_since=None, reflection=note)
    elif action in REFLECTIONS:
        _, title, effect, question, photo = REFLECTIONS[action]
        note = {'action': action, 'role': role, 'title': title, 'effect': effect, 'question': question, 'photo': photo, 'number': len(s.get('notices', [])) + 1}
        s.setdefault('notices', []).append(note)
        s['notices'] = s['notices'][-30:]
        s['active_elapsed'] = elapsed(s)
        s.update(active_since=None, reflection=note)
    elif action == 'next' and s['phase'] == 3:
        s['active_elapsed'] = elapsed(s)
        s['active_since'] = None
    elif action == 'climate_resume':
        s['active_since'] = time.time()

class Store:
    def __init__(self):
        self.lock = threading.RLock()
        self.sessions = {}

    def create(self):
        with self.lock:
            now = time.time()
            self.sessions = {c: s for c, s in self.sessions.items() if now - s['state']['started'] < 28800}
            if len(self.sessions) >= 100:
                raise ValueError('Nombre maximal de parties atteint.')
            code = secrets.token_hex(3).upper()
            while code in self.sessions:
                code = secrets.token_hex(3).upper()
            token = secrets.token_urlsafe(32)
            self.sessions[code] = {'state': initial(), 'tokens': {'master': token}}
            return {'code': code, 'role': 'master', 'token': token}

    def join(self, code, role):
        with self.lock:
            if role not in ('students', 'manager', 'supplier'):
                raise ValueError('Équipe inconnue.')
            if code not in self.sessions:
                raise ValueError('Partie introuvable.')
            tokens = self.sessions[code]['tokens']
            tokens.setdefault(role, secrets.token_urlsafe(32))
            return {'code': code, 'role': role, 'token': tokens[role]}

    def _session(self, auth):
        session = self.sessions.get(auth['code'])
        if not session or session['tokens'].get(auth['role']) != auth['token']:
            raise ValueError('Partie expirée ou accès refusé. Rejoignez une nouvelle partie.')
        return session

    def read(self, auth):
        with self.lock:
            return copy.deepcopy(self._session(auth)['state'])

    def action(self, auth, action, **values):
        with self.lock:
            session = self._session(auth)
            next_state = copy.deepcopy(session['state'])
            apply(next_state, auth['role'], action, **values)
            session['state'] = next_state
