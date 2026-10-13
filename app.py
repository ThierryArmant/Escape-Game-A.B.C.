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
        st.rerun(scope='fragment')
    except ValueError as exc:
        st.session_state.abc_error = str(exc)


def mission_help(role, s):
    phase = s['phase']
    if phase == 4:
        return ('Préparer le bilan', 'Expliquez un choix, son effet sur le budget ou les restes, puis un geste à appliquer à la cantine.', 'Échangez oralement avec les autres équipes.')
    if role == 'master':
        if phase in (1, 3):
            return ('Faire avancer les équipes', 'Les gestionnaires proposent le menu. Les fournisseurs confirment sa disponibilité et les élèves le valident.', 'Lorsque les deux accords sont affichés, cliquez sur « Passer à la manche suivante ». Vous pouvez déclencher un seul aléa quand vous le souhaitez.')
        return ('Accompagner la mesure', 'Les élèves choisissent le service, puis les gestionnaires calculent les grammes par convive et le pourcentage jeté.', 'Attendez que la mesure A.B.C. affiche « Résolue », puis cliquez sur « Passer à la manche suivante ».')
    if phase in (1, 3):
        field = 'first' if phase == 1 else 'second'
        if role == 'manager':
            detail = 'Choisissez un menu pour 600 repas dans la liste « Menu », puis cliquez sur « Proposer ce menu ».'
            if phase == 3 and s['event']:
                detail = 'Lisez l’alerte : les disponibilités et les prix ont changé. Choisissez un menu de remplacement, puis cliquez sur « Proposer ce menu ».'
            return ('Proposer le repas', detail, 'Discutez avec les deux autres équipes. Une nouvelle proposition annule les accords précédents.')
        if not s[field]:
            return ('Préparer votre avis', 'Attendez la proposition des gestionnaires, visible dans « Décisions partagées ».', 'Fournisseurs : préparez les stocks et alternatives. Élèves : préparez vos préférences et les adaptations acceptables.')
        if s['approvals'][role]:
            return ('Votre accord est enregistré', 'Votre équipe a validé la proposition actuelle.', 'Attendez les autres équipes et le maître. Si le menu change, vous devrez le valider à nouveau.')
        if role == 'supplier':
            return ('Confirmer la disponibilité', 'Lisez le menu dans « Décisions partagées ». Vérifiez les stocks, les délais et l’éventuelle alerte avec les gestionnaires.', 'Cliquez sur « Confirmer le menu et sa disponibilité ».')
        return ('Valider le choix des convives', 'Lisez le menu dans « Décisions partagées ». Discutez des préférences des élèves et des adaptations possibles.', 'Cliquez sur « Valider le menu proposé ».')
    if role == 'students':
        return ('Choisir les portions', 'Dans « Organisation du service », choisissez une manière de servir, puis cliquez sur « Choisir le service ».', 'Les gestionnaires calculeront ensuite le gaspillage. Un changement de service annule le calcul précédent.')
    if role == 'manager':
        if s['measure']:
            return ('Mesure réussie', 'Les deux calculs sont corrects.', 'Expliquez ce que les restes représentent et attendez la manche suivante.')
        if not s['service']:
            return ('Attendre le choix du service', 'Les élèves doivent d’abord choisir les portions.', 'Dès que les restes apparaissent, remplissez les deux champs et cliquez sur « Vérifier la mesure A.B.C. ».')
        return ('Calculer le gaspillage', 'Avec les kilogrammes de restes affichés, calculez les grammes par convive pour 600 élèves et le pourcentage des 300 kg servis.', 'Remplissez les deux champs, puis cliquez sur « Vérifier la mesure A.B.C. ». Vous pouvez demander un indice au maître.')
    return ('Préparer une alternative', 'Quels produits et quelles recettes permettraient d’adapter le prochain repas ?', 'Vous n’avez pas de bouton de validation à cette manche. Discutez avec les autres équipes et expliquez les contraintes du producteur.')

@st.dialog('Votre mission')
def show_mission(role, s):
    title, instruction, next_step = mission_help(role, s)
    st.caption(ROLES[role])
    st.subheader(title)
    st.write(instruction)
    st.info(next_step)
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
    help_context = (auth['code'], role, phase, s['event'], bool(s['first'] if phase == 1 else s['second']) if phase in (1, 3) else bool(s['service']), s['measure'])
    if st.session_state.get('mission_context') != help_context:
        st.session_state.mission_context = help_context
        st.session_state.mission_pending = True
        st.rerun()
    if st.button('❓ Que doit faire mon équipe ?'):
        st.session_state.mission_pending = True
        st.rerun()
    title, instruction, _ = mission_help(role, s)
    st.info(f'**À vous : {title}.** {instruction}')
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
                grams = st.number_input('Grammes par convive', min_value=0.0, step=1.0)
                percent = st.number_input('Pourcentage jeté', min_value=0.0, max_value=100.0, step=1.0)
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
