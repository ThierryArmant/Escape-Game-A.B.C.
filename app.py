import time
import streamlit as st
from abc_game import Store, MENUS, SERVICES, ROLES, cost

st.set_page_config(page_title='Escape Game A.B.C.', page_icon='🌱', layout='wide')

@st.cache_resource
def shared_store():
    return Store()

store = shared_store()
st.title('🌱 Escape Game A.B.C.')
st.caption('600 repas · Trois équipes · Une réussite collective')

if 'auth' not in st.session_state:
    left, right = st.columns(2)
    with left:
        st.subheader('Écran maître')
        st.write('Créez une partie et communiquez le code aux trois équipes.')
        if st.button('Créer une partie', type='primary'):
            try:
                st.session_state.auth = store.create()
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    with right:
        st.subheader('Rejoindre une équipe')
        with st.form('join'):
            code = st.text_input('Code de la partie', max_chars=6).strip().upper()
            role = st.selectbox('Équipe', ['students', 'manager', 'supplier'], format_func=ROLES.get)
            if st.form_submit_button('Rejoindre'):
                try:
                    st.session_state.auth = store.join(code, role)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    st.caption('Données économiques fictives. Aucun nom d’élève demandé.')
    st.stop()

auth = st.session_state.auth
st.info(f"{ROLES[auth['role']]} · Code : {auth['code']}")
if st.button('Quitter cet écran'):
    del st.session_state.auth
    st.rerun()

def act(action, **values):
    try:
        store.action(auth, action, **values)
        st.session_state.pop('abc_error', None)
        st.rerun()
    except ValueError as exc:
        st.session_state.abc_error = str(exc)


def mission_help(role, s):
    phase = s['phase']
    menu = s['first' if phase == 1 else 'second'] if phase in (1, 3) else None
    pending = [ROLES[r] for r in ('supplier', 'students') if not s['approvals'][r]]
    if phase == 4:
        return ('Préparer le bilan', 'Expliquez un choix, son effet sur le budget ou les restes, puis un geste à appliquer à la cantine.', 'Échangez oralement avec les autres équipes.')
    if role == 'master':
        if phase in (1, 3):
            if not menu:
                return ('Attendre les gestionnaires', 'L’équipe Gestionnaires doit choisir un menu puis cliquer sur « Proposer ce menu ».', 'Les autres équipes recevront automatiquement leur consigne dès que la proposition sera enregistrée.')
            if pending:
                return ('Des accords sont attendus', 'Le menu est proposé. Équipes qui doivent encore agir : ' + ', '.join(pending) + '.', 'Elles reçoivent leur consigne sur leur écran. Attendez leurs validations.')
            return ('Tout le monde a validé', 'Le menu et les deux accords sont enregistrés.', 'Cliquez sur « Passer à la manche suivante ».')
        if not s['service']:
            return ('Attendre le service', 'L’équipe Familles et élèves doit choisir l’organisation des portions.', 'Les gestionnaires seront ensuite invités à calculer le gaspillage.')
        if not s['measure']:
            return ('Attendre les calculs', 'Le service est choisi. Les gestionnaires doivent calculer les grammes par convive et le pourcentage jeté.', 'La calculatrice et les formules sont disponibles sur leur écran.')
        return ('La mesure est réussie', 'Les gestionnaires ont trouvé les deux résultats.', 'Cliquez sur « Passer à la manche suivante ».')
    if phase in (1, 3):
        if role == 'manager':
            if menu:
                remaining = 3000 - sum(s[k]['cost'] for k in ('first', 'second') if s[k])
                detail = f'Votre menu est enregistré : {MENUS[menu["id"]][0]}, {menu["cost"]} €. Le budget restant sur les deux repas est de {remaining} €. Cette somme est réservée aux achats du jeu.'
                return ('Menu proposé : attendez les accords', detail, 'Encore attendus : ' + ', '.join(pending) + '. Vous pouvez discuter avec ces équipes.' if pending else 'Les deux équipes ont validé. Attendez que le maître passe à la manche suivante.')
            detail = 'Comparez les menus et leurs prix. Choisissez dans la liste « Menu », puis cliquez sur « Proposer ce menu ».'
            if phase == 3 and s['event']:
                detail = 'Lisez l’alerte, comparez les produits encore disponibles et les nouveaux prix. Choisissez un remplacement dans « Menu », puis cliquez sur « Proposer ce menu ».'
            return ('Choisir un repas pour 600 convives', detail, 'Utilisez la calculatrice si nécessaire. Premier repas : 1 500 € maximum. Les deux repas ensemble : 3 000 € maximum.')
        if not menu:
            return ('Préparer votre avis', 'Attendez la proposition des gestionnaires, visible dans « Décisions partagées ».', 'Fournisseurs : préparez stocks et alternatives. Familles et élèves : discutez des préférences et adaptations acceptables.')
        label = f'{MENUS[menu["id"]][0]} · {menu["cost"]} €'
        if s['approvals'][role]:
            return ('Votre accord est enregistré', 'Vous avez validé : ' + label + '.', 'Attendez les autres équipes et le maître. Une modification du menu demandera un nouvel accord.')
        if role == 'supplier':
            return ('Un menu vous est proposé', label + '. Vérifiez les stocks, les délais et l’alerte éventuelle avec les gestionnaires.', 'Si le menu est réalisable, cliquez sur « Confirmer le menu et sa disponibilité ». Sinon, demandez oralement un autre menu avant de confirmer.')
        return ('Donner l’avis des convives', label + '. Discutez : ce repas est-il acceptable ? Comment donner envie de le goûter ?', 'Après cet échange, cliquez sur « Valider le menu proposé ». Si vous souhaitez un changement, demandez-le aux gestionnaires avant de valider.')
    if role == 'students':
        if s['service']:
            return ('Service enregistré', SERVICES[s['service']][0] + '. Les restes simulés sont maintenant visibles.', 'Les gestionnaires doivent effectuer les deux calculs. Attendez leur résultat. Changer de service annulera leur mesure précédente.')
        return ('Choisir les portions', 'Comparez les trois organisations : portion unique, petite portion avec complément, ou portion adaptée et recette présentée.', 'Choisissez dans « Organisation du service » puis cliquez sur « Choisir le service ». Les petits appétits doivent pouvoir prendre moins, et les autres se resservir.')
    if role == 'manager':
        if s['measure']:
            return ('Mesure réussie', 'Les deux calculs sont corrects. Expliquez aux autres équipes ce que représente cette quantité jetée.', 'La valeur des restes est une dépense déjà engagée : elle ne revient pas dans le budget. Attendez la manche suivante.')
        if not s['service']:
            return ('Attendre le choix des portions', 'L’équipe Familles et élèves doit d’abord choisir le service.', 'Dès que les kilogrammes de restes apparaissent, vous recevrez la consigne de calcul.')
        waste = SERVICES[s['service']][1]
        return ('Calculer les restes du repas', f'Vous observez {waste} kg de restes pour 600 convives, sur 300 kg servis. Calculez les grammes par convive et le pourcentage jeté.', 'Ouvrez la calculatrice ci-dessous. Formules : kg × 1 000 ÷ 600 ; kg ÷ 300 × 100. Reportez vos résultats dans les deux champs, puis cliquez sur « Vérifier la mesure A.B.C. ».')
    return ('Préparer une alternative', 'Pendant la mesure, discutez d’un produit ou d’une recette de remplacement et des difficultés du producteur.', 'Pas de bouton à valider à cette manche. Votre mission est un échange oral ; vous interviendrez à nouveau au prochain repas.')

def calculator(prefix, role, s):
    if s['phase'] == 4:
        return
    with st.expander('🧮 Calculatrice — budget et quantités', expanded=role == 'manager' and s['phase'] == 2 and bool(s['service']) and not s['measure']):
        if s['phase'] == 2 and s['service']:
            waste = SERVICES[s['service']][1]
            if st.checkbox('M’aider pas à pas avec les nombres du jeu', key=prefix + '_guided'):
                st.write(f'1. Convertir les kilogrammes en grammes : {waste} × 1 000 = {waste * 1000} g.')
                st.write(f'2. Partager entre 600 convives : {waste * 1000} ÷ 600 = {waste * 1000 / 600:g} g par convive.')
                st.write(f'3. Calculer la part jetée : {waste} ÷ 300 × 100 = {waste / 3:g} %.')
                if role == 'manager' and not s['measure']:
                    if st.button('Reporter ces résultats dans mes réponses', key=prefix + '_copy'):
                        st.session_state.answer_grams = waste * 1000 / 600
                        st.session_state.answer_percent = waste / 3
                        st.session_state.mission_pending = False
                        st.rerun()
                st.caption('Expliquez avec vos mots ce que signifie chacun des deux résultats.')
        if s['phase'] == 2:
            st.caption('Grammes par convive : kg de restes × 1 000 ÷ 600. Pourcentage : kg de restes ÷ 300 × 100. Effectuez vos opérations puis reportez les résultats dans les champs de réponse.')
        else:
            st.caption('Budget restant : 3 000 − coût du premier repas − coût du prochain repas. Prix par convive : coût du repas ÷ 600.')
        x = st.number_input('Premier nombre', value=0.0, key=prefix + '_x', format='%.3f')
        op = st.selectbox('Opération', ['+', '−', '×', '÷'], key=prefix + '_op')
        y = st.number_input('Deuxième nombre', value=0.0, key=prefix + '_y', format='%.3f')
        if op == '÷' and y == 0:
            st.caption('Saisissez un diviseur différent de zéro.')
        else:
            result = x + y if op == '+' else x - y if op == '−' else x * y if op == '×' else x / y
            st.success(f'{x:g} {op} {y:g} = {result:g}')
            st.caption('Pour enchaîner un calcul, recopiez le résultat dans « Premier nombre ». La calculatrice ne valide pas vos réponses à votre place.')

@st.dialog('Votre mission')
def show_mission(role, s):
    title, instruction, next_step = mission_help(role, s)
    st.caption(ROLES[role])
    st.subheader(title)
    st.write(instruction)
    st.info(next_step)
    calculator('dialog_calc', role, s)
    if st.button('J’ai compris', type='primary'):
        st.rerun()


@st.fragment(run_every='2s')
def game():
    try:
        s = store.read(auth)
    except ValueError as exc:
        st.error(str(exc))
        return
    role, phase = auth['role'], s['phase']
    current_menu = s['first' if phase == 1 else 'second'] if phase in (1, 3) else None
    menu_signature = (current_menu['id'], current_menu['cost']) if current_menu else None
    approvals_signature = tuple(s['approvals'][r] for r in ('supplier', 'students')) if role in ('master', 'manager') else s['approvals'].get(role)
    help_context = (auth['code'], role, phase, s['event'], menu_signature, s['service'], s['measure'], approvals_signature if phase in (1, 3) else None)
    if st.session_state.get('mission_context') != help_context:
        st.session_state.mission_context = help_context
        st.session_state.mission_pending = True
        st.rerun()
    if st.button('❓ Que doit faire mon équipe ?'):
        st.session_state.mission_pending = True
        st.rerun()
    title, instruction, next_step = mission_help(role, s)
    st.info(f'**À vous : {title}.** {instruction}')
    st.caption(next_step)
    calculator('screen_calc', role, s)
    st.subheader(['', '1 · Acheter et composer', '2 · Servir et mesurer', '3 · Adapter ensemble', 'Bilan collectif'][phase])
    remaining_time = max(0, 1800 - int(time.time() - s['started']))
    st.caption(f'Temps indicatif : {remaining_time // 60} min {remaining_time % 60:02d} s')
    waste = SERVICES[s['service']][1] if s['service'] else None
    spent = sum(s[k]['cost'] for k in ('first', 'second') if s[k])
    a, b, c = st.columns(3)
    a.metric('Budget restant sur deux repas', f'{3000 - spent} €')
    b.metric('Restes comestibles', '—' if waste is None else f'{waste} kg')
    c.metric('Mesure A.B.C.', 'Résolue' if s['measure'] else 'À résoudre')
    if s['event'] == 'inondation':
        st.warning('INONDATION — Les récoltes de carottes et de pommes de terre du fournisseur touché sont détruites. Il perd les revenus attendus malgré les dépenses déjà engagées. Les stocks de remplacement deviennent plus chers : le menu de secours passe de 900 € à 1 080 € (+20 %, hypothèse fictive). Adaptez le prochain repas ensemble.')
    elif s['event'] == 'secheresse':
        st.warning('SÉCHERESSE — Seule la moitié des carottes est disponible. Le remplacement fait passer les légumes à 189 € au lieu de 180 €. Les pommes de terre passent de 144 € à 180 €. Ces hausses sont fictives.')
    if st.session_state.get('abc_error'):
        st.error(st.session_state.abc_error)
    if role == 'master':
        st.write('Les équipes négocient oralement puis valident sur leur tablette. Vous décidez quand déclencher un seul aléa.')
        if phase < 4:
            if st.button('Passer à la manche suivante', type='primary'):
                act('next')
            if st.button('Afficher un indice'):
                act('hint')
            if not s['event']:
                x, y = st.columns(2)
                if x.button('Déclencher une sécheresse'):
                    act('event', value='secheresse')
                if y.button('Déclencher une inondation'):
                    act('event', value='inondation')
    elif phase in (1, 3):
        if role == 'manager':
            st.write('Proposez un menu pour 600 convives. Base fixe de 540 € incluse. Budget : 1 500 € au premier repas, 3 000 € sur les deux.')
            options = list(MENUS) if phase == 3 else [m for m in MENUS if m != 'secours']
            options = [m for m in options if not (phase == 3 and s['event'] == 'inondation' and m != 'secours')]
            first_cost = s['first']['cost'] if s['first'] and phase == 3 else 0
            st.write('Comparez avant de choisir : les calculs du budget sont faits pour vous.')
            st.table([{'Menu': MENUS[m][0], 'Coût du repas (€)': cost(m, s['event'] if phase == 3 else None), 'Budget restant pour les deux repas (€)': 3000 - first_cost - cost(m, s['event'] if phase == 3 else None)} for m in options])
            st.caption('Après votre proposition, les fournisseurs vérifient les disponibilités et les familles et élèves donnent leur accord. Vous n’avez pas à passer vous-mêmes à la manche suivante.')
            with st.form(f'menu_{phase}_{s["event"]}'):
                choice = st.selectbox('Menu', options, format_func=lambda m: f'{MENUS[m][0]} · {cost(m, s["event"] if phase == 3 else None)} €')
                if st.form_submit_button('Proposer ce menu'):
                    act('menu', value=choice)
        elif role == 'supplier':
            st.write('Mission : confirmez les quantités et les délais avant de promettre une livraison. Un lot de carottes et de poulet régional par service. Deux lots de légumes surgelés en réserve. Commande ordinaire à J−2 : produits régionaux à J+1, importés à J+2.')
            st.write('Après un aléa, riz de réserve, lentilles et légumes surgelés non touchés permettent le menu de secours. Expliquez les conséquences sur votre travail et vos revenus.')
            if st.button('Confirmer le menu et sa disponibilité'):
                act('approve')
        else:
            st.write('180 convives préfèrent une petite portion avec un complément possible. Discutez de l’acceptabilité du menu et proposez une présentation qui donne envie de goûter.')
            if st.button('Valider le menu proposé'):
                act('approve')
    elif phase == 2:
        if role == 'students':
            with st.form('service'):
                choice = st.radio('Organisation du service', list(SERVICES), format_func=lambda k: SERVICES[k][0])
                if st.form_submit_button('Choisir le service'):
                    act('service', value=choice)
        elif role == 'manager':
            st.write('300 kg comestibles servis à 600 convives. Calculez les grammes de restes par convive et le pourcentage jeté.')
            with st.form('measure'):
                grams = st.number_input('Grammes par convive', min_value=0.0, step=1.0, key='answer_grams')
                percent = st.number_input('Pourcentage jeté', min_value=0.0, max_value=100.0, step=1.0, key='answer_percent')
                if st.form_submit_button('Vérifier la mesure A.B.C.'):
                    act('measure', grams=grams, percent=percent)
        else:
            st.write('Préparez une alternative aux produits exposés à un aléa. Comment utiliser les mesures pour ajuster les achats sans priver les convives de nourriture ?')
    if phase == 4:
        st.success('Mission accomplie : deux services de 600 repas prévus dans le budget collectif.')
        st.write('Quel geste appliquerez-vous à la cantine ? Qu’avez-vous appris d’une autre équipe ? Quel choix a rendu votre menu adaptable ?')
    st.divider()
    st.subheader('Décisions partagées')
    for field, label in [('first', 'Premier repas'), ('second', 'Prochain repas')]:
        menu = s[field]
        st.write(f'{label} : ' + (f'{MENUS[menu["id"]][0]} · {menu["cost"]} €' if menu else 'En discussion'))
    st.write('Service : ' + (SERVICES[s['service']][0] if s['service'] else 'À choisir'))
    if phase in (1, 3):
        st.write('Fournisseurs : ' + ('✓ confirmé' if s['approvals']['supplier'] else 'en attente') + ' · Élèves : ' + ('✓ validé' if s['approvals']['students'] else 'en attente'))
    if s['measure']:
        st.write(f'Valeur estimée des restes : {round(s["first"]["cost"] * waste / 300)} €. Dépense déjà engagée, pas d’argent récupéré.')
    if s['hint']:
        st.info('Grammes par convive = kg de restes × 1 000 ÷ 600. Pourcentage = kg de restes ÷ 300 × 100. Budget collectif = coût des deux menus.')
    st.caption('Données fictives · Mesures A.B.C. simulées · Une catastrophe n’est pas une conséquence directe des plateaux jetés.')

game()
if st.session_state.pop('mission_pending', False):
    try:
        show_mission(auth['role'], store.read(auth))
    except ValueError as exc:
        st.error(str(exc))
