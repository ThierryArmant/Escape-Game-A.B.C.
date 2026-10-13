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
ROLES = {'master': 'Maître du jeu', 'students': 'Familles et élèves', 'manager': 'Gestionnaires', 'supplier': 'Producteurs et fournisseurs'}

def cost(menu, event=None):
    if menu not in MENUS:
        raise ValueError('Menu inconnu')
    if event == 'inondation' and menu != 'secours':
        raise ValueError('Récoltes détruites : choisissez les produits de réserve.')
    return MENUS[menu][1] + (180 if event == 'inondation' else 0) + (9 + (36 if menu == 'regional' else 0) if event == 'secheresse' and menu != 'secours' else 0)

def initial():
    return dict(phase=1, event=None, started=time.time(), hint=False, first=None, second=None, service=None, measure=False, approvals={'supplier': False, 'students': False})

def apply(s, role, action, **values):
    if role == 'master':
        if action == 'event':
            event = values.get('value')
            if event not in ('secheresse', 'inondation') or s['event'] or s['phase'] == 4:
                raise ValueError('Un seul aléa par partie.')
            s.update(event=event, second=None, approvals={'supplier': False, 'students': False})
        elif action == 'hint':
            s['hint'] = True
        elif action == 'next':
            p = s['phase']
            if p in (1, 3) and (not s['first' if p == 1 else 'second'] or not all(s['approvals'].values())):
                raise ValueError('Le menu doit être validé par les trois équipes.')
            if p == 2 and not s['measure']:
                raise ValueError('Résolvez la mesure A.B.C. avant de continuer.')
            s['phase'] = min(4, p + 1)
            s['hint'] = False
            if s['phase'] == 3:
                s['approvals'] = {'supplier': False, 'students': False}
        else:
            raise ValueError('Action inconnue.')
    elif action == 'menu' and role == 'manager' and s['phase'] in (1, 3):
        menu = values.get('value')
        price = cost(menu, s['event'] if s['phase'] == 3 else None)
        if s['phase'] == 1 and (menu == 'secours' or price > 1500):
            raise ValueError('Choisissez un menu ordinaire dans le budget.')
        if s['phase'] == 3 and price + s['first']['cost'] > 3000:
            raise ValueError('Budget collectif dépassé.')
        s['first' if s['phase'] == 1 else 'second'] = {'id': menu, 'cost': price}
        s['approvals'] = {'supplier': False, 'students': False}
    elif action == 'approve' and role in ('supplier', 'students') and s['phase'] in (1, 3):
        if not s['first' if s['phase'] == 1 else 'second']:
            raise ValueError('Attendez la proposition du gestionnaire.')
        s['approvals'][role] = True
    elif action == 'service' and role == 'students' and s['phase'] == 2:
        if values.get('value') not in SERVICES:
            raise ValueError('Service inconnu.')
        s.update(service=values['value'], measure=False)
    elif action == 'measure' and role == 'manager' and s['phase'] == 2:
        if not s['service']:
            raise ValueError('Attendez le choix du service.')
        waste = SERVICES[s['service']][1]
        if values.get('grams') != waste * 1000 / 600 or values.get('percent') != waste / 3:
            raise ValueError('Vérifiez les unités et les deux calculs.')
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
