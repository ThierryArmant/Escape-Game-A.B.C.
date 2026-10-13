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

@st.fragment(run_every='2s')
def game():
    try:
        s = store.read(auth)
    except ValueError as exc:
        st.error(str(exc))
        return
    role, phase = auth['role'], s['phase']
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
