"""Moteur coopératif sans dépendance ; état partagé protégé par verrou."""
import copy
import secrets
import threading
import time

MENUS = {
    'regional': ('Poulet régional, pommes de terre, carottes', 1440),
    'importe': ('Poulet importé, riz, carottes', 1242),
    'vegetal': ('Lentilles, riz, carottes', 918),
    'secours': ('Lentilles, riz de réserve, légumes surgelés', 900),
}
SERVICES = {'unique': ('Portion unique', 60), 'adapte': ('Petite portion et complément', 36), 'explique': ('Portion adaptée et recette présentée', 24)}
ROLES = {'master': 'Maître du jeu', 'students': 'Familles et élèves', 'manager': 'Chef cuisinier', 'supplier': 'Producteurs et fournisseurs'}

PRODUCTION = {
    'conventionnel': {'name': 'Production conventionnelle', 'potato_price': 1.20, 'carrot_price': 2.00, 'potato_cost': .80, 'carrot_cost': 1.20},
    'bio': {'name': 'Production biologique', 'potato_price': 1.40, 'carrot_price': 2.40, 'potato_cost': 1.00, 'carrot_cost': 1.50},
}
SERVICE_LABELS = {'unique': 'Même portion de plat pour tous', 'adapte': 'Plat selon la faim, avec complément', 'explique': 'Plat selon la faim, possibilité de goûter'}
SELF_SERVICE = {'tout': ('Prendre entrée et dessert systématiquement', 0), 'faim': ('Choisir entrée et dessert selon sa faim', -6), 'gouter': ('Goûter une petite quantité avant de choisir', -12)}

def cost(menu, event=None, mode='conventionnel', reuse=False):
    if menu not in MENUS or mode not in PRODUCTION:
        raise ValueError('Choix inconnu.')
    if event == 'inondation' and menu != 'secours':
        raise ValueError('Récoltes détruites : choisissez les produits de réserve.')
    extra = (60 if menu == 'regional' else 36) if mode == 'bio' and menu != 'secours' else 0
    # En sécheresse : seule une demi-récolte de carottes est achetée au producteur.
    if event == 'secheresse' and mode == 'bio' and menu != 'secours':
        extra = 18 + (24 if menu == 'regional' else 0)
    saving = stock_saving(menu, event, mode) if reuse else 0
    return round(MENUS[menu][1] + extra + (180 if event == 'inondation' else 0) + (9 + (36 if menu == 'regional' else 0) if event == 'secheresse' and menu != 'secours' else 0) - saving, 2)

def stock_saving(menu, event, mode):
    if menu == 'secours':
        return 0
    if menu == 'regional':
        return 12 * (PRODUCTION[mode]['potato_price'] + (.30 if event == 'secheresse' else 0))
    return 9 * PRODUCTION[mode]['carrot_price']

def harvest(s):
    event = s['event'] if s['phase'] == 3 else None
    if event == 'inondation':
        return {'name': 'Légumes surgelés de réserve', 'plots': 6, 'yield': 15, 'quantity': 90, 'unit': 'caisses', 'need': 90}
    potato = s['first' if s['phase'] == 1 else 'second']
    if potato and potato['id'] == 'regional':
        y = 24 if event == 'secheresse' else 30
        return {'name': 'Pommes de terre', 'plots': 4, 'yield': y, 'quantity': 4 * y, 'unit': 'parcelles', 'need': 108 if s['phase'] == 3 and potato.get('reuse') else 120}
    y = 15 if event == 'secheresse' else 30
    return {'name': 'Carottes', 'plots': 3, 'yield': y, 'quantity': 3 * y, 'unit': 'parcelles', 'need': 81 if s['phase'] == 3 and potato and potato.get('reuse') else 90}

def waste(s):
    if not s['service']:
        return None
    return max(0, SERVICES[s['service']][1] + SELF_SERVICE[s.get('self_service', 'tout')][1])

def initial():
    return dict(phase=1, event=None, started=time.time(), hint=False, first=None, second=None, service=None, self_service='tout', measure=False, grams_done=False, production=None, harvest_done=False, supply_done=False, supply_strategy=None, approvals={'supplier': False, 'students': False})

def reset_supply(s):
    s.update(harvest_done=False, supply_done=False, supply_strategy=None)
    s['approvals'] = {'supplier': False, 'students': False}

def apply(s, role, action, **values):
    if role == 'master':
        if action == 'event':
            event = values.get('value')
            if event not in ('secheresse', 'inondation') or s['event'] or s['phase'] == 4:
                raise ValueError('Un seul aléa par partie.')
            s.update(event=event, second=None)
            if s['phase'] == 3:
                reset_supply(s)
        elif action == 'hint':
            s['hint'] = True
        elif action == 'next':
            p = s['phase']
            if p in (1, 3) and (not s['first' if p == 1 else 'second'] or not all(s['approvals'].values())):
                raise ValueError('Les trois équipes ont encore une mission à terminer.')
            if p == 2 and not s['measure']:
                raise ValueError('Le chef cuisinier termine les deux petits calculs avant la suite.')
            s['phase'] = min(4, p + 1)
            s['hint'] = False
            if s['phase'] == 3:
                reset_supply(s)
        else:
            raise ValueError('Action inconnue.')
        return
    if action == 'production' and role == 'supplier' and s['phase'] == 1:
        mode = values.get('value')
        if mode not in PRODUCTION:
            raise ValueError('Choisissez un mode de production.')
        if s['production'] == mode:
            return
        s['production'] = mode
        if s['first']:
            s['first']['cost'] = cost(s['first']['id'], mode=mode)
        reset_supply(s)
    elif action == 'menu' and role == 'manager' and s['phase'] in (1, 3):
        if not s['production']:
            raise ValueError('Le producteur choisit d’abord son mode de production. Les prix seront alors disponibles.')
        menu = values.get('value')
        reuse = bool(values.get('reuse')) and s['phase'] == 3
        price = cost(menu, s['event'] if s['phase'] == 3 else None, s['production'], reuse)
        if s['phase'] == 1 and (menu == 'secours' or price > 1500):
            raise ValueError('Choisissez un menu ordinaire dans le budget.')
        if s['phase'] == 3 and price + s['first']['cost'] > 3000:
            raise ValueError('Ce menu dépasse le budget des deux repas. Essayez une autre recette : aucune pénalité.')
        s['first' if s['phase'] == 1 else 'second'] = {'id': menu, 'cost': price, 'reuse': reuse, 'adaptation': values.get('adaptation') if s['phase'] == 3 else None}
        reset_supply(s)
    elif action == 'harvest' and role == 'supplier' and s['phase'] in (1, 3):
        if not s['first' if s['phase'] == 1 else 'second']:
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
        if not s['first' if s['phase'] == 1 else 'second']:
            raise ValueError('Attendez la proposition du chef cuisinier.')
        if role == 'supplier' and not (s['harvest_done'] and s['supply_done'] and s['supply_strategy']):
            raise ValueError('Terminez votre calcul et la vérification de la commande avant de confirmer.')
        s['approvals'][role] = True
    elif action == 'service' and role == 'students' and s['phase'] == 2:
        if values.get('value') not in SERVICES or values.get('self_service') not in SELF_SERVICE:
            raise ValueError('Choisissez le service du plat et le libre-service.')
        s.update(service=values['value'], self_service=values['self_service'], measure=False, grams_done=False)
    elif action == 'grams' and role == 'manager' and s['phase'] == 2:
        if not s['service']:
            raise ValueError('Attendez le choix du service.')
        if values.get('answer') != waste(s) * 1000 / 600:
            raise ValueError('Pas encore : convertissez les kg en grammes, puis partagez entre les 600 convives. Ouvrez l’aide pour avancer.')
        s['grams_done'] = True
    elif action == 'percent' and role == 'manager' and s['phase'] == 2:
        if not s['grams_done']:
            raise ValueError('Terminez d’abord la question des grammes par élève.')
        if values.get('answer') != waste(s) / 3:
            raise ValueError('Essayez encore : divisez les kg de restes par les 300 kg servis, puis multipliez par 100. L’aide est disponible.')
        s['measure'] = True
    else:
        raise ValueError('Action non disponible pour votre rôle.')

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
