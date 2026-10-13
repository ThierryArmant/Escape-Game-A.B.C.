import time
import streamlit as st
import importlib

@st.cache_resource
def load_engine(revision):
    # Streamlit peut relancer app.py sans recharger les modules importés.
    import abc_game
    return importlib.reload(abc_game)

engine = load_engine('cantine-v2')
Store, MENUS, SERVICES, ROLES = engine.Store, engine.MENUS, engine.SERVICES, engine.ROLES
PRODUCTION, SERVICE_LABELS, SELF_SERVICE = engine.PRODUCTION, engine.SERVICE_LABELS, engine.SELF_SERVICE
cost, harvest, waste, stock_saving = engine.cost, engine.harvest, engine.waste, engine.stock_saving

st.set_page_config(page_title='Escape Game A.B.C.', page_icon='🌱', layout='wide')

@st.cache_resource
def shared_store(revision):
    return Store()

store = shared_store('cantine-v2')
st.title('🌱 Escape Game A.B.C.')
st.caption('600 repas · Trois équipes · Une réussite collective')

if 'auth' not in st.session_state:
    a, b = st.columns(2)
    with a:
        st.subheader('Écran maître')
        st.write('Créez une partie, puis communiquez son code aux trois équipes.')
        if st.button('Créer une partie', type='primary'):
            try:
                st.session_state.auth = store.create()
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    with b:
        with st.form('join'):
            st.subheader('Rejoindre une équipe')
            code = st.text_input('Code de la partie', max_chars=6).strip().upper()
            role = st.selectbox('Équipe', ['students', 'manager', 'supplier'], format_func=ROLES.get)
            if st.form_submit_button('Rejoindre'):
                try:
                    st.session_state.auth = store.join(code, role)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
    st.caption('Données fictives. Aucun nom d’élève demandé.')
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
        st.rerun()

def mission(role, s):
    phase = s['phase']
    menu = s['first' if phase == 1 else 'second'] if phase in (1, 3) else None
    if phase == 4:
        return 'Votre bilan', 'Expliquez un choix de votre équipe et proposez un geste pour votre vraie cantine.'
    if role == 'master':
        if phase in (1, 3):
            if not s['production']:
                return 'Les producteurs commencent', 'Ils choisissent bio ou conventionnel. Le chef cuisinier pourra ensuite proposer le menu.'
            if not menu:
                return 'Attendre la commande', 'Le chef cuisinier choisit le menu. Les autres équipes reçoivent leur mission dès qu’il est proposé.'
            pending = [ROLES[r] for r in ('supplier', 'students') if not s['approvals'][r]]
            return ('Missions encore en cours', 'Attendez : ' + ', '.join(pending) + '.') if pending else ('Prêts pour la suite', 'Les trois équipes ont terminé. Cliquez sur « Passer à la manche suivante ».')
        return ('Mesure terminée', 'Cliquez sur « Passer à la manche suivante ».') if s['measure'] else ('Les élèves choisissent, le chef cuisinier mesure', 'Attendez le service choisi et les deux calculs. Les aides sont disponibles sur les écrans des équipes.')
    if phase in (1, 3):
        if role == 'supplier':
            if not s['production']:
                return 'Choisir comment vous produisez', 'Comparez les prix et les coûts fictifs, puis choisissez bio ou conventionnel. Ce choix fixera les prix pour la cantine.'
            if not menu:
                return 'Votre offre est prête', 'Le chef cuisinier choisit un menu à partir de vos prix. Attendez leur commande.'
            if s['approvals']['supplier']:
                return 'Livraison confirmée', 'Votre vérification est terminée. Attendez la validation des élèves et la suite donnée par le maître.'
            if not s['harvest_done']:
                return 'Combien pouvez-vous fournir ?', 'Calculez les kilogrammes disponibles : nombre de parcelles ou caisses × kilogrammes de chacune. Une question à la fois, avec aide et calculatrice.'
            if not s['supply_done']:
                return 'Comparer avec la commande', 'Votre récolte est calculée. Comparez-la à la quantité demandée : en avez-vous assez ?'
            if not s['supply_strategy']:
                return 'Compléter la quantité manquante', 'Votre récolte est insuffisante. Choisissez le complément disponible pour livrer le repas entier. Son surcoût est inclus dans le prix du menu.'
            return 'Votre commande est réalisable', 'Cliquez sur « Confirmer la livraison ». Le chef cuisinier et les élèves verront votre accord.'
        if role == 'manager':
            if not s['production']:
                return 'Attendre les prix du producteur', 'Le producteur choisit d’abord son mode de production. Votre liste de menus apparaîtra ensuite.'
            if not menu:
                return 'Choisir le menu', 'Comparez les prix et le budget restant. Choisissez un menu pour 600 convives puis cliquez sur « Proposer ce menu ».'
            pending = [ROLES[r] for r in ('supplier', 'students') if not s['approvals'][r]]
            return ('Menu enregistré', 'Votre budget est calculé. Attendez : ' + ', '.join(pending) + '.') if pending else ('Commande validée', 'Tous ont donné leur accord. Le maître peut passer à la suite.')
        if not menu:
            return 'Attendre le menu', 'Le chef cuisinier va proposer un repas. Il apparaîtra ici ; vous pourrez alors donner votre avis.'
        return ('Votre avis est enregistré', 'Attendez la fin de la mission du producteur et la suite donnée par le maître.') if s['approvals']['students'] else ('Donner l’avis des convives', 'Lisez le menu, imaginez votre plateau et échangez dans votre équipe. Validez le repas proposé, ou demandez un changement au chef cuisinier avant de valider.')
    if role == 'students':
        return ('Vos choix de cantine sont enregistrés', 'Les restes simulés sont affichés. Le chef cuisinier va compter ce qui est jeté et son coût. Attendez ses calculs.') if s['service'] else ('Comme à la cantine', 'Choisissez comment demander votre plat selon votre faim, puis comment prendre entrée et dessert en libre-service. Lisez les explications avant de choisir.')
    if role == 'manager':
        if not s['service']:
            return 'Attendre les choix des convives', 'Les élèves choisissent leurs portions et le libre-service. Vous mesurerez ensuite les restes.'
        if s['measure']:
            return 'Vos mesures sont terminées', 'Regardez ce que représente la nourriture jetée en euros. Cette dépense ne revient pas dans le budget. Préparez une amélioration pour le prochain repas.'
        return ('Question 2 : la part jetée', 'Vous avez trouvé les grammes par élève. Calculez maintenant le pourcentage du repas jeté. La calculatrice et l’aide restent disponibles.') if s['grams_done'] else ('Question 1 : les restes par élève', 'Convertissez les kilogrammes en grammes, puis partagez entre 600 élèves. La question suivante apparaîtra après votre réussite.')
    return 'Préparer le prochain repas', 'Votre récolte a été vérifiée. Regardez les choix des convives et la mesure du gaspillage ; vous recalculerez votre offre à la manche suivante.'

@st.dialog('Votre prochaine action')
def show_mission(role, s):
    title, text = mission(role, s)
    st.caption(ROLES[role])
    st.subheader(title)
    st.write(text)
    st.caption('Les outils et les boutons utiles vous attendent sur votre page.')
    if st.button('J’ai compris', type='primary'):
        st.rerun()

def calculator(key):
    with st.expander('🧮 Ouvrir la calculatrice', expanded=False):
        st.caption('Saisissez les deux nombres de votre opération. Vous pouvez recopier le résultat pour faire la suivante.')
        x = st.number_input('Premier nombre', value=0.0, key=key + '_x')
        op = st.selectbox('Opération', ['×', '÷', '+', '−'], key=key + '_op')
        y = st.number_input('Deuxième nombre', value=0.0, key=key + '_y')
        if op == '÷' and y == 0:
            st.caption('Le diviseur doit être différent de zéro.')
        else:
            r = x * y if op == '×' else x / y if op == '÷' else x + y if op == '+' else x - y
            st.success(f'{x:g} {op} {y:g} = {r:g}')

def math_question(key, title, data, answer, unit, action, hints):
    # Chaque question a son propre niveau d’aide. Aucune réponse n’est révélée au départ.
    key = auth['code'] + '_' + key
    st.subheader(title)
    st.write(data)
    level_key = key + '_help'
    level = st.session_state.get(level_key, 0)
    if st.button('J’ai besoin d’aide' if level == 0 else 'Un peu plus d’aide', key=key + '_help_button', disabled=level >= 3):
        st.session_state[level_key] = min(3, level + 1)
        st.rerun()
    if level:
        st.info(hints[min(level, 2) - 1])
    if level >= 3:
        st.success(f'Nous le faisons ensemble : {answer:g} {unit}. Recopiez ce résultat puis vérifiez pour continuer.')
    calculator(key + '_calc')
    with st.form(key + '_form'):
        value = st.number_input('Votre réponse (' + unit + ')', min_value=0.0, step=1.0, key=key + '_answer')
        if st.form_submit_button('Vérifier et continuer', type='primary'):
            act(action, answer=value)
    st.caption('Vous pouvez réessayer autant de fois que nécessaire, sans pénalité.')

def supplier_panel(s):
    phase = s['phase']
    if phase == 2:
        st.write('Votre mission de livraison est terminée. Préparez votre offre pour le prochain repas en observant les restes. Aucun calcul supplémentaire à cette manche.')
        return
    if phase not in (1, 3):
        return
    if not s['production']:
        st.subheader('1 · Votre mode de production')
        st.write('Dans ce scénario, le bio coûte davantage à produire et se vend plus cher. Les rendements de départ sont identiques : cela ne signifie pas que tous les rendements réels sont identiques.')
        st.table([{'Mode': v['name'], 'Coût pommes de terre €/kg': v['potato_cost'], 'Vente pommes de terre €/kg': v['potato_price'], 'Coût carottes €/kg': v['carrot_cost'], 'Vente carottes €/kg': v['carrot_price']} for v in PRODUCTION.values()])
        with st.form('production'):
            mode = st.radio('Votre choix', list(PRODUCTION), format_func=lambda k: PRODUCTION[k]['name'])
            if st.form_submit_button('Publier mes prix', type='primary'):
                act('production', value=mode)
        return
    st.caption('Production choisie : ' + PRODUCTION[s['production']]['name'])
    menu = s['first' if phase == 1 else 'second']
    if not menu:
        st.info('Votre offre est envoyée. Le calcul de récolte apparaîtra dès que le chef cuisinier auront commandé.')
        return
    h = harvest(s)
    if s['event'] == 'inondation' and phase == 3:
        st.warning('Vos 120 kg de pommes de terre et 90 kg de carottes sont perdus dans les parcelles touchées. Les frais de culture étaient déjà engagés. Pour cette livraison, vous mobilisez un stock de réserve non touché.')
    if not s['harvest_done']:
        math_question(f'harvest_{phase}_{menu["id"]}_{s["event"]}', '2 · Calculer la quantité disponible', f'{h["name"]} : vous avez {h["plots"]} {h["unit"]}. Chacune fournit {h["yield"]} kg. Combien de kilogrammes sont disponibles en tout ?', h['quantity'], 'kg', 'harvest', [f'Multipliez les {h["plots"]} {h["unit"]} par les {h["yield"]} kg de chacune.', f'L’opération est : {h["plots"]} × {h["yield"]}. Utilisez la calculatrice si besoin.'])
        return
    st.success('Votre calcul est validé !')
    st.subheader('Correction de votre calcul')
    st.write(f'**{h["plots"]} {h["unit"]} × {h["yield"]} kg = {h["quantity"]} kg** de {h["name"].lower()}.')
    st.caption('On additionne la même quantité pour chaque parcelle ou caisse : la multiplication donne le total disponible.')
    if not s['supply_done']:
        st.subheader('3 · Avez-vous assez pour la cantine ?')
        st.write(f'Votre stock : **{h["quantity"]} kg**. Commande : **{h["need"]} kg**.')
        with st.form('supply'):
            choice = st.radio('Pouvez-vous fournir toute la quantité avec ce stock ?', ['oui', 'non'], format_func=lambda k: 'Oui, j’ai assez' if k == 'oui' else 'Non, il manque une quantité')
            if st.form_submit_button('Vérifier ma comparaison', type='primary'):
                act('supply', value=choice)
        with st.expander('Besoin d’aide pour comparer ?'):
            st.write('Si le stock est égal ou supérieur à la commande, vous avez assez. Sinon, la quantité manquante est : commande − stock.')
        return
    st.subheader('Correction de la comparaison')
    if h['quantity'] >= h['need']:
        surplus = h['quantity'] - h['need']
        st.write(f'**{h["quantity"]} kg disponibles ≥ {h["need"]} kg commandés** : vous avez assez pour livrer.')
        st.caption(f'Après livraison : {h["quantity"]} − {h["need"]} = {surplus} kg encore en stock.')
    else:
        st.write(f'**{h["quantity"]} kg disponibles < {h["need"]} kg commandés** : votre récolte seule ne suffit pas.')
        st.caption(f'Quantité à compléter : {h["need"]} − {h["quantity"]} = {h["need"] - h["quantity"]} kg.')
    if not s['supply_strategy']:
        missing = h['need'] - h['quantity']
        st.warning(f'Il manque {missing} kg. Votre calcul a permis de repérer le problème !')
        st.write('Un complément est disponible : légumes surgelés pour les carottes, fournisseur partenaire pour les pommes de terre. Le menu affiché comprend déjà ce remplacement et sa hausse de prix.')
        if st.button(f'Organiser le complément de {missing} kg', type='primary'):
            act('strategy', value='complement')
        return
    st.success('La commande peut être livrée avec le stock vérifié et, si nécessaire, le complément prévu.')
    if not s['approvals']['supplier']:
        if st.button('Confirmer la livraison', type='primary'):
            act('approve')

def manager_panel(s):
    phase = s['phase']
    if phase in (1, 3):
        if not s['production']:
            st.info('Attendez les prix du producteur.')
            return
        menu = s['first' if phase == 1 else 'second']
        if menu:
            st.success(f'Menu proposé : {MENUS[menu["id"]][0]} · {menu["cost"]} €.')
            if phase == 3 and menu.get('reuse'):
                st.write(f'Le stock utilisable réduit les nouveaux achats de {stock_saving(menu["id"], s["event"], s["production"]):g} €.')
            if menu.get('adaptation'):
                st.write('Votre amélioration pour demain : ' + menu['adaptation'])
            with st.expander('Modifier ma proposition'):
                menu_picker(s)
        else:
            menu_picker(s)
        return
    if phase != 2 or not s['service']:
        return
    w = waste(s)
    if not s['grams_done']:
        math_question(f'grams_{s["service"]}_{s["self_service"]}', '1 · Combien est jeté par élève ?', f'Il reste **{w} kg** de nourriture comestible pour **600 convives**. Combien cela fait-il de **grammes par convive** ?', w * 1000 / 600, 'g par convive', 'grams', ['D’abord, convertissez les kilogrammes en grammes : 1 kg = 1 000 g. Ensuite, partagez entre 600 convives.', f'Première opération : {w} × 1 000. Deuxième opération : le résultat ÷ 600.'])
    elif not s['measure']:
        st.success(f'Première mesure réussie : {w * 1000 / 600:g} g par convive.')
        math_question(f'percent_{s["service"]}_{s["self_service"]}', '2 · Quelle part du repas a été jetée ?', f'**{w} kg** jetés sur **300 kg** servis. Quel est le **pourcentage jeté** ?', w / 3, '%', 'percent', ['Pour obtenir un pourcentage, divisez la quantité jetée par la quantité servie, puis multipliez par 100.', f'Les opérations sont : {w} ÷ 300, puis le résultat × 100.'])
    else:
        st.success(f'Bravo : {w * 1000 / 600:g} g par convive et {w / 3:g} % du repas jeté.')
        value = round(s['first']['cost'] * w / 300)
        st.metric('Valeur estimée de la nourriture jetée', f'{value} €')
        st.write('Cette nourriture a été achetée mais personne ne l’a mangée. Cette dépense ne revient pas dans votre budget. Vous pourrez améliorer le prochain service avec les élèves et les producteurs.')

def menu_picker(s):
    phase = s['phase']
    event = s['event'] if phase == 3 else None
    options = list(MENUS) if phase == 3 else [m for m in MENUS if m != 'secours']
    if event == 'inondation':
        options = ['secours']
    spent = s['first']['cost'] if phase == 3 else 0
    if phase == 3:
        st.subheader('Le chef adapte le repas du lendemain')
        st.write(f'Hier : {waste(s)} kg de restes comestibles, soit {waste(s) * 1000 / 600:g} g par élève. Utilisez cette observation pour adapter le service, présenter le plat et éviter de trop acheter.')
        st.info('Stock fictif utilisable de la veille : 12 kg de pommes de terre crues et 9 kg de carottes crues, non servies et conservées dans des conditions adaptées. Ce stock était déjà acheté avant les deux repas du jeu. Il est distinct des déchets des plateaux, qui ne sont pas remis en cuisine.')
    st.subheader('Comparer les repas pour 600 convives')
    st.caption('Base fixe de 540 € incluse. Les prix tiennent compte du choix du producteur et des aléas.')
    st.table([{'Menu': MENUS[m][0], 'Prix (€)': cost(m, event, s['production']), 'Budget restant sur deux repas (€)': 3000 - spent - cost(m, event, s['production'])} for m in options])
    calculator('budget_' + str(phase))
    with st.form('menu_' + str(phase)):
        choice = st.selectbox('Menu', options, format_func=lambda k: MENUS[k][0])
        reuse = st.checkbox('Utiliser le stock de légumes crus de la veille dans ce menu') if phase == 3 and event != 'inondation' else False
        if phase == 3:
            st.caption('Menu régional : 12 kg de pommes de terre déjà en stock, donc 108 kg à commander. Autres menus avec carottes : 9 kg déjà en stock, donc 81 kg à commander. La réduction de dépense sera affichée après votre proposition. Le menu de réserve utilise ses propres stocks.')
            adaptation = st.radio('Pour mieux satisfaire les convives demain', ['Présenter le plat et proposer de goûter', 'Prévoir des portions selon la faim et un complément', 'Conserver le service prévu'])
        if st.form_submit_button('Proposer ce menu', type='primary'):
            act('menu', value=choice, reuse=reuse, adaptation=adaptation if phase == 3 else None)
    st.caption('Après votre proposition : le producteur vérifie sa récolte ; les élèves donnent leur avis ; le maître lance la suite.')

def students_panel(s):
    phase = s['phase']
    if phase in (1, 3):
        menu = s['first' if phase == 1 else 'second']
        if menu:
            st.subheader('Votre prochain repas')
            st.write(MENUS[menu['id']][0])
            if menu.get('adaptation'):
                st.info('Le chef propose pour demain : ' + menu['adaptation'])
            if menu.get('reuse'):
                st.caption('Le chef utilise aussi des légumes crus encore disponibles dans son stock de la veille.')
            st.write('Voici le plat proposé : connaissez-vous ce plat ? Est-il acceptable pour les convives ? Validez ce repas ou demandez un changement au chef avant de valider.')
            st.info('Vous validez ici le choix du plat. Les portions et les entrées/desserts en libre-service se choisissent à la manche 2, après le passage à la suite par le maître.')
            if not s['approvals']['students'] and st.button('Valider ce repas pour les convives', type='primary'):
                act('approve')
        return
    if phase != 2:
        return
    if s['service']:
        st.success('Votre organisation est enregistrée. Le chef cuisinier calcule maintenant les restes.')
        st.write('Plat : ' + SERVICE_LABELS[s['service']])
        st.write('Libre-service : ' + SELF_SERVICE[s['self_service']][0])
        with st.expander('Changer notre organisation'):
            service_picker()
    else:
        service_picker()

def service_picker():
    st.subheader('À la cantine : chacun n’a pas la même faim')
    st.write('Aujourd’hui, certains élèves ont une petite faim, d’autres une grande faim. Le plat est servi à l’assiette par un agent ; les entrées et desserts sont en libre-service.')
    st.table([
        {'Service du plat': SERVICE_LABELS['unique'], 'Ce qui se passe': 'L’agent met la même quantité dans chaque assiette.', 'Pourquoi le choisir ?': 'Simple à organiser, mais la portion peut être trop grande ou trop petite.'},
        {'Service du plat': SERVICE_LABELS['adapte'], 'Ce qui se passe': 'Vous annoncez petite ou grande faim. Un complément est possible.', 'Pourquoi le choisir ?': 'Adapter la portion à sa faim ; organiser le complément pour ceux qui en ont besoin.'},
        {'Service du plat': SERVICE_LABELS['explique'], 'Ce qui se passe': 'L’agent présente le plat, propose de goûter, puis sert selon votre faim.', 'Pourquoi le choisir ?': 'Découvrir un plat sans remplir son assiette d’emblée ; cela demande du temps et un accompagnement.'},
    ])
    st.write('**Entrées et desserts :** prendre systématiquement les deux est simple, mais vous pouvez avoir trop sur le plateau. Choisir selon votre faim permet de prendre ce que vous pensez manger. Goûter une petite quantité aide lorsque le plat est inconnu, si cette possibilité est organisée par la cantine.')
    with st.form('service'):
        choice = st.radio('Comment servir le plat à l’assiette ?', list(SERVICE_LABELS), format_func=SERVICE_LABELS.get)
        free = st.radio('Que faites-vous aux entrées et desserts en libre-service ?', list(SELF_SERVICE), format_func=lambda k: SELF_SERVICE[k][0])
        st.caption('Petite faim : vous pouvez demander moins. Grande faim : une quantité suffisante et un complément doivent rester possibles.')
        if st.form_submit_button('Enregistrer nos choix de cantine', type='primary'):
            act('service', value=choice, self_service=free)

@st.fragment(run_every='2s')
def game():
    try:
        s = store.read(auth)
    except ValueError as exc:
        st.error(str(exc))
        return
    # Une aide automatique à chaque véritable étape, jamais à chaque frappe dans la calculatrice.
    role, phase = auth['role'], s['phase']
    title, instruction = mission(role, s)
    context = (auth['code'], role, phase, s['event'], title, str(s['first']), str(s['second']), s['service'], s['self_service'])
    if st.session_state.get('mission_context') != context:
        st.session_state.mission_context = context
        st.session_state.mission_pending = True
        st.rerun()
    if st.button('❓ Que doit faire mon équipe ?'):
        st.session_state.mission_pending = True
        st.rerun()
    st.info(f'**{title}** — {instruction}')
    st.subheader(['', '1 · Commander et vérifier la récolte', '2 · Choisir son service et mesurer les restes', '3 · Adapter le prochain repas', 'Bilan collectif'][phase])
    seconds = max(0, 1800 - int(time.time() - s['started']))
    st.caption(f'Temps indicatif : {seconds // 60} min {seconds % 60:02d} s')
    spent = sum(s[k]['cost'] for k in ('first', 'second') if s[k])
    x, y, z = st.columns(3)
    x.metric('Budget disponible sur deux repas', f'{3000 - spent} €')
    y.metric('Restes comestibles simulés', '—' if waste(s) is None else f'{waste(s)} kg')
    z.metric('Mesure A.B.C.', 'Terminée' if s['measure'] else 'À faire')
    if s['event']:
        text = 'INONDATION : les récoltes du fournisseur touché sont détruites. Ses frais étaient engagés et ses revenus attendus sont perdus. Les réserves de remplacement sont plus demandées : le menu de secours passe de 900 € à 1 080 €.' if s['event'] == 'inondation' else 'SÉCHERESSE : les rendements du prochain repas diminuent. Les producteurs recalculent leur récolte ; les compléments font monter les prix.'
        st.warning(text + ' Les repas déjà servis ne changent pas. Hypothèses fictives du jeu.')
    if st.session_state.get('abc_error'):
        st.warning(st.session_state.abc_error)
    if role == 'master' and phase < 4:
        ready = (bool(s['first' if phase == 1 else 'second']) and all(s['approvals'].values())) if phase in (1, 3) else s['measure']
        if st.button('Passer à la manche suivante', disabled=not ready, type='primary'):
            act('next')
        if not ready:
            st.caption('Le bouton se déverrouille quand les missions nécessaires sont terminées.')
        if st.button('Afficher un indice commun'):
            act('hint')
        if not s['event']:
            a, b = st.columns(2)
            if a.button('Déclencher une sécheresse'):
                act('event', value='secheresse')
            if b.button('Déclencher une inondation'):
                act('event', value='inondation')
    elif role == 'manager':
        manager_panel(s)
    elif role == 'supplier':
        supplier_panel(s)
    elif role == 'students':
        students_panel(s)
    if phase == 4:
        st.success('Les deux repas sont possibles dans le budget collectif. Chaque équipe a contribué !')
        st.write('Quel choix a réduit les restes ? Quelle difficulté a rencontré le producteur ? Que changeriez-vous à votre vraie cantine ?')
    with st.expander('Voir les décisions des trois équipes', expanded=role == 'master'):
        st.write('Production : ' + (PRODUCTION[s['production']]['name'] if s['production'] else 'À choisir'))
        for k, label in [('first', 'Premier repas'), ('second', 'Prochain repas')]:
            m = s[k]
            st.write(label + ' : ' + (f'{MENUS[m["id"]][0]} · {m["cost"]} €' if m else 'À proposer'))
            if m and m.get('adaptation'):
                st.write('Amélioration proposée par le chef : ' + m['adaptation'])
        if phase in (1, 3):
            st.write('Producteur : ' + ('✓ livraison confirmée' if s['approvals']['supplier'] else 'mission en cours') + ' · Élèves : ' + ('✓ avis validé' if s['approvals']['students'] else 'avis attendu'))
        if s['service']:
            st.write('Plat : ' + SERVICE_LABELS[s['service']])
            st.write('Entrées et desserts : ' + SELF_SERVICE[s['self_service']][0])
    if s['hint']:
        st.info('Les aides individuelles sont disponibles à chaque calcul. Identifiez ce qui est demandé : une quantité totale, une quantité par élève ou un pourcentage.')
    st.caption('Prix, rendements et restes fictifs. Aucun mode de production ne garantit à lui seul un meilleur rendement. A.B.C. est simulé. Le gaspillage ne provoque pas directement l’aléa de cette partie.')

game()
if st.session_state.pop('mission_pending', False):
    try:
        show_mission(auth['role'], store.read(auth))
    except ValueError as exc:
        st.error(str(exc))
