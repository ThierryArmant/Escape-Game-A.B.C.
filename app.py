import time
import streamlit as st
from climate_cards import climate_pause, menu_consequences, sourcing_card, NUTRITION_URL
import importlib

@st.cache_resource
def load_engine(revision):
    # Streamlit peut relancer app.py sans recharger les modules importés.
    import abc_game
    return importlib.reload(abc_game)

engine = load_engine('cantine-v3-courtier-actions')
Store, MENUS, SERVICES, ROLES = engine.Store, engine.MENUS, engine.SERVICES, engine.ROLES
PRODUCTION, SERVICE_LABELS, SELF_SERVICE = engine.PRODUCTION, engine.SERVICE_LABELS, engine.SELF_SERVICE
cost, harvest, waste, stock_saving = engine.cost, engine.harvest, engine.waste, engine.stock_saving
requirements = engine.requirements
BEEF = engine.BEEF
POTATO = engine.POTATO

st.set_page_config(page_title='Escape Game A.B.C.', page_icon='🌱', layout='wide')

@st.cache_resource
def shared_store(revision):
    return Store()

store = shared_store('cantine-v3-courtier-actions')
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
    menu = (s['first'] if phase == 1 and s['second'] else s['second'] if phase == 3 and s['reviewed'] else None) if phase in (1, 3) else None
    if phase == 3 and not s['climate_ack']:
        return 'Pause commune : comprendre le climat', 'Lisez les quatre cartes après le premier repas. Le maître reprendra ensuite la mission du jour 2.'
    if phase == 1 and s['first'] and s['second'] and s['first']['cost'] + s['second']['cost'] > 3000:
        return ('Revoir votre prévision', 'Ces deux menus dépassent le budget : ouvrez la modification et essayez une autre combinaison.') if role == 'manager' else ('Budget insuffisant', 'Le chef doit modifier les menus avant la commande. Le total et le déficit sont affichés sur les écrans.')
    if phase == 5:
        return 'Votre bilan', 'Expliquez un choix de votre équipe et proposez un geste pour votre vraie cantine.'
    if role == 'master':
        if phase in (1, 3):
            if not s['production']:
                return 'Le courtier prépare ses offres', 'Il choisit son fournisseur de légumes et l’origine de la viande. Le chef préparera ensuite les deux menus ensemble.'
            if not menu:
                return 'Attendre les deux menus' if phase == 1 else 'Attendre la révision du jour 2', 'Le chef prépare les deux repas à l’avance, puis réexamine le deuxième après les restes du premier service.'
            pending = [ROLES[r] for r in ('supplier', 'students') if not s['approvals'][r]]
            return ('Missions encore en cours', 'Attendez : ' + ', '.join(pending) + '.') if pending else ('Prêts pour la suite', 'Les trois équipes ont terminé. La suite se lance automatiquement.')
        return ('Bilan pris en compte', 'La suite se lance automatiquement.') if s['waste_reviewed'] else ('Les élèves choisissent, le chef consulte les pertes', 'Les résultats se calculent automatiquement. Le chef doit lire le bilan puis confirmer qu’il l’a pris en compte.')
    if phase in (1, 3):
        if role == 'supplier':
            if not s['production']:
                return 'Choisir vos fournisseurs', 'Vous êtes courtier : vous choisissez des fournisseurs. Publiez vos prix ; les quantités et les disponibilités des deux repas seront ensuite calculées automatiquement.'
            if not menu:
                return 'Préparer les deux livraisons', 'Attendez les deux menus du chef ; entre les deux jours, attendez sa confirmation ou sa modification du menu du lendemain.'
            if s['approvals']['supplier']:
                return 'Livraison confirmée', 'Votre vérification est terminée. Attendez la validation des élèves et la suite donnée par le maître.'
            if not s['harvest_done']:
                return 'Combien pouvez-vous fournir ?', 'Calculez les kilogrammes disponibles : nombre de parcelles ou caisses × kilogrammes de chacune. Une question à la fois, avec aide et calculatrice.'
            if not s['supply_done']:
                return 'Comparer avec la commande', 'Les disponibilités sont calculées. Regardez si un complément est nécessaire.'
            if not s['supply_strategy']:
                return 'Compléter la quantité manquante', 'Le stock proposé est insuffisant. Choisissez le complément disponible pour livrer le repas entier. Son surcoût est inclus dans le prix du menu.'
            return 'Votre commande est réalisable', 'Cliquez sur « Confirmer la livraison ». Le chef cuisinier et les élèves verront votre accord.'
        if role == 'manager':
            if not s['production']:
                return 'Attendre les offres du courtier', 'Le courtier choisit les fournisseurs ; vous pourrez ensuite préparer les deux menus.'
            if not menu:
                return ('Préparer les deux repas', 'Choisissez le menu du jour 1 et celui du jour 2 : variez les plats et vérifiez le budget total, puis envoyez les deux commandes.') if phase == 1 else ('Revoir le menu du jour 2', 'Comparez le menu prévu avec les restes du jour 1, le stock utilisable et l’alerte. Confirmez ou modifiez ce menu pour lancer la nouvelle vérification du courtier.')
            pending = [ROLES[r] for r in ('supplier', 'students') if not s['approvals'][r]]
            return ('Menu enregistré', 'Votre budget est calculé. Attendez : ' + ', '.join(pending) + '.') if pending else ('Commande validée', 'Tous ont donné leur accord. La suite se lance automatiquement.')
        if not menu:
            return 'Attendre le menu', 'Le chef cuisinier va préparer les deux repas. Il apparaîtra ici ; vous pourrez alors donner votre avis.'
        return ('Votre avis est enregistré', 'Attendez la fin de la mission du courtier et la suite donnée par le maître.') if s['approvals']['students'] else ('Donner l’avis des convives', 'Lisez le menu, imaginez votre plateau et échangez dans votre équipe. Validez le repas proposé, ou demandez un changement au chef cuisinier avant de valider.')
    if role == 'students':
        return ('Vos choix de cantine sont enregistrés', 'Les restes simulés et leur coût sont calculés. Le chef lit le bilan avant la suite.') if s['service'] else ('Comme à la cantine', 'Choisissez comment demander votre plat selon votre faim, puis comment prendre entrée et dessert en libre-service. Lisez les explications avant de choisir.')
    if role == 'manager':
        if not s['service']:
            return 'Attendre les choix des convives', 'Les élèves choisissent les portions et le libre-service. Le bilan des restes s’affichera automatiquement.'
        if s['waste_reviewed']:
            return 'Pertes prises en compte', 'La suite se lance automatiquement. Vous réexaminerez le menu du jour 2 après le premier service.'
        return 'Lire les résultats du service', 'Les kilogrammes, grammes par élève, pourcentage et pertes en euros sont calculés. Lisez-les, puis cliquez sur « J’ai pris en compte les pertes ».'
    return 'Préparer le prochain repas', 'Votre commande a été vérifiée. Regardez les choix des convives et la mesure du gaspillage ; vous recalculerez votre offre à la manche suivante.'

@st.dialog('Votre prochaine action')
def show_mission(role, s):
    title, text = mission(role, s)
    st.caption(ROLES[role])
    st.subheader(title)
    st.write(text)
    menu_consequences(s)
    st.caption('Les outils et les boutons utiles vous attendent sur votre page.')
    if st.button('J’ai compris', type='primary'):
        st.rerun()

def supplier_panel(s):
    phase = s['phase']
    if phase in (2, 4):
        st.write('Votre mission de livraison est terminée. Préparez votre offre pour le prochain repas en observant les restes. Aucun calcul supplémentaire à cette manche.')
        return
    if phase not in (1, 3):
        return
    if not s['production']:
        st.subheader('1 · Vos offres de fournisseur')
        st.write('Vous êtes courtier, pas agriculteur : vous choisissez des fournisseurs. Dans ce scénario fictif, l’offre bio est plus chère. Les frais de culture du tableau expliquent le prix du producteur ; ce ne sont pas vos frais de courtier.')
        st.table([{'Mode': v['name'], 'Coût pommes de terre €/kg': v['potato_cost'], 'Vente pommes de terre €/kg': v['potato_price'], 'Coût carottes €/kg': v['carrot_cost'], 'Vente carottes €/kg': v['carrot_price']} for v in PRODUCTION.values()])
        sourcing_card()
        with st.form('production'):
            mode = st.radio('Votre choix', list(PRODUCTION), format_func=lambda k: PRODUCTION[k]['name'])
            source = st.radio('Fournisseur de poulet pour 600 portions (72 kg)', ['regional', 'importe'], format_func=lambda k: 'Régional : 576 €, livraison J+1' if k == 'regional' else 'Importé : 432 €, livraison J+2')
            animal_offer = st.radio('Votre offre supplémentaire : comparer les cours fictifs', ['boeuf', 'boeuf_bresil', 'boeuf_argentine', 'porc_ventoux', 'poisson'], format_func=lambda k: MENUS[k][0] + ' · menu complet ' + str(cost(k, mode=mode)) + ' €')
            st.caption('Les commandes sont préparées deux jours à l’avance : les deux délais sont possibles. Le prix importé inférieur est une hypothèse du jeu, pas une garantie sur tous les produits.')
            if st.form_submit_button('Publier mes prix', type='primary'):
                act('production', value=mode, source=source, animal_offer=animal_offer)
        return
    st.caption('Offre légumes choisie : ' + PRODUCTION[s['production']]['name'])
    menu = s['first' if phase == 1 else 'second']
    if not menu or not s['second'] or phase == 3 and not s['reviewed']:
        st.info('Votre offre est envoyée. Le calcul de récolte apparaîtra dès que le chef cuisinier auront commandé.')
        return
    st.subheader('Commande des deux jours' if phase == 1 else 'Commande révisée du jour 2')
    st.table([{'Produit': k, 'Quantité à livrer (kg)': v} for k, v in requirements(s).items()])
    sourcing_card()
    st.caption('Stocks partenaires réservables : poulet 144 kg, pommes de terre 240 kg, carottes 180 kg, riz sec 72 kg, lentilles sèches 72 kg, bœuf 144 kg. Les deux repas doivent rester variés. Les légumes constituent votre calcul de vérification ; les autres lignes sont vérifiées avec les stocks du catalogue.')
    h = harvest(s)
    if s['event'] == 'inondation' and phase == 3:
        st.warning('Vos 120 kg de pommes de terre et 90 kg de carottes sont perdus dans les parcelles touchées. Les frais de culture étaient déjà engagés. Pour cette livraison, vous mobilisez un stock de réserve non touché.')
    st.success('Les quantités sont prêtes : vous n’avez aucun calcul à saisir.')
    st.subheader('Votre disponibilité, calculée automatiquement')
    st.write(f'**{h["plots"]} {h["unit"]} × {h["yield"]} kg = {h["quantity"]} kg** de {h["name"].lower()}.')
    st.caption('On additionne la même quantité pour chaque parcelle ou caisse : la multiplication donne le total disponible.')
    st.subheader('Peut-on livrer la commande ?')
    if h['quantity'] >= h['need']:
        surplus = h['quantity'] - h['need']
        st.write(f'**{h["quantity"]} kg disponibles ≥ {h["need"]} kg commandés** : vous avez assez pour livrer.')
        st.caption(f'Après livraison : {h["quantity"]} − {h["need"]} = {surplus} kg encore en stock.')
    else:
        st.write(f'**{h["quantity"]} kg disponibles < {h["need"]} kg commandés** : votre récolte seule ne suffit pas.')
        st.caption(f'Quantité à compléter : {h["need"]} − {h["quantity"]} = {h["need"] - h["quantity"]} kg.')
    if not s['supply_strategy']:
        missing = h['need'] - h['quantity']
        st.warning(f'Il manque {missing} kg. Le bilan automatique a repéré le manque.')
        st.write('Un complément est disponible : légumes surgelés pour les carottes, fournisseur partenaire pour les pommes de terre. Le menu affiché comprend déjà ce remplacement et sa hausse de prix.')
        if st.button(f'Organiser le complément de {missing} kg', type='primary'):
            act('strategy', value='complement')
        return
    st.success('La commande peut être livrée avec le stock vérifié et, si nécessaire, le complément prévu.')
    if not s['approvals']['supplier']:
        if st.button('Confirmer la livraison', type='primary', disabled=s['first']['cost'] + s['second']['cost'] > 3000):
            act('approve')

def manager_panel(s):
    phase = s['phase']
    if phase in (1, 3):
        if not s['production']:
            st.info('Attendez les prix du courtier.')
            return
        menu = s['first' if phase == 1 else 'second']
        if menu and s['second'] and (phase != 3 or s['reviewed']):
            if phase == 1:
                st.write('Menu du jour 2 déjà prévu : ' + MENUS[s['second']['id']][0])
            st.success(f'Menu proposé : {MENUS[menu["id"]][0]} · {menu["cost"]} €.')
            if phase == 3 and menu.get('reuse'):
                st.write(f'Le stock utilisable réduit les nouveaux achats de {stock_saving(menu["id"], s["event"], s["production"]):g} €.')
            if menu.get('adaptation'):
                st.write('Votre amélioration pour demain : ' + menu['adaptation'])
            if phase == 1:
                menu_consequences(s)
                if s['first']['id'] in BEEF and s['second']['id'] in BEEF:
                    if st.button('Essayer des lentilles au jour 2', type='primary'):
                        act('plans', first=s['first']['id'], second='vegetal')
            with st.expander('Modifier ma proposition', expanded=phase == 1 and s['first']['cost'] + s['second']['cost'] > 3000):
                menu_picker(s)
        else:
            menu_picker(s)
        return
    if phase not in (2, 4) or not s['service']:
        return
    w = waste(s)
    st.subheader('Bilan automatique du service')
    value = round(s['first' if phase == 2 else 'second']['cost'] * w / 300)
    st.table([
        {'Résultat': 'Restes comestibles', 'Valeur': f'{w} kg'},
        {'Résultat': 'Restes par élève', 'Valeur': f'{w * 1000 / 600:g} g'},
        {'Résultat': 'Part du repas jetée', 'Valeur': f'{w / 3:g} %'},
        {'Résultat': 'Valeur estimée des restes', 'Valeur': f'{value} €'},
    ])
    st.write('Cette nourriture a été achetée mais personne ne l’a mangée. La valeur des restes ne revient pas dans le budget. Pour le prochain repas, vous pouvez adapter le menu, présenter le plat et proposer des portions selon la faim.')
    if not s['waste_reviewed'] and st.button('J’ai pris en compte les pertes', type='primary'):
        act('review_waste')

def plan_two_days(s):
    st.subheader('Préparer les deux repas à l’avance')
    st.write('Un repas doit nourrir, donner envie de manger et respecter le budget. Le courtier doit connaître vos deux commandes pour réserver les bons produits.')
    st.table([
        {'Repère': 'Légumes et fruits', 'Pourquoi ?': 'Varier les goûts et apporter notamment des fibres et vitamines.', 'Dans le jeu': 'Légumes dans les plats ; fruits et entrées dans la base fixe.'},
        {'Repère': 'Féculents', 'Pourquoi ?': 'Apporter de l’énergie ; privilégier aussi les versions complètes ou semi-complètes.', 'Dans le jeu': 'Pommes de terre ou riz.'},
        {'Repère': 'Sources de protéines variées', 'Pourquoi ?': 'Alterner les aliments : la viande n’est pas nécessaire tous les jours.', 'Dans le jeu': 'Un jour avec volaille, un autre avec lentilles.'},
        {'Repère': 'Eau et accompagnements', 'Pourquoi ?': 'Prévoir aussi l’eau et les autres composantes du repas.', 'Dans le jeu': 'Entrée, fruit ou produit laitier et pain sont inclus dans la base fixe.'},
    ])
    st.caption('Ces repères expliquent les choix du jeu ; deux menus ne suffisent pas à valider un plan alimentaire scolaire réel. L’équilibre s’apprécie sur plusieurs repas.')
    st.markdown('[Repères pour les 4–17 ans — Manger Bouger](' + NUTRITION_URL + ')')
    options = [s['meat_source'], 'vegetal', s['animal_offer']]
    st.table([{'Plat proposé': MENUS[m][0], 'Prix pour 600 repas (€)': cost(m, mode=s['production'], beef_source=s['beef_source'])} for m in options])
    st.caption('Les prix et le budget des deux jours sont calculés pour vous.')
    with st.form('two_days'):
        first = st.selectbox('Jour 1 · Menu', options, format_func=lambda k: MENUS[k][0])
        second = st.selectbox('Jour 2 · Menu prévu', ['vegetal', s['meat_source'], s['animal_offer']], format_func=lambda k: MENUS[k][0])
        st.caption('Variez les deux journées. Après le jour 1, vous pourrez revoir le second menu grâce aux mesures de restes et aux nouvelles disponibilités.')
        if st.form_submit_button('Envoyer les deux menus au courtier', type='primary'):
            act('plans', first=first, second=second)

def menu_picker(s):
    phase = s['phase']
    if phase == 1:
        plan_two_days(s)
        return
    event = s['event'] if phase == 3 else None
    options = [s['meat_source'], s['animal_offer'], 'vegetal', 'secours'] if phase == 3 else [s['meat_source'], s['animal_offer'], 'vegetal']
    if event == 'inondation':
        options = ['secours']
    spent = s['first']['cost'] if phase == 3 else 0
    if phase == 3:
        st.subheader('Le chef adapte le repas du lendemain')
        st.write(f'Hier : {s["day1"]["waste"]} kg de restes comestibles, soit {s["day1"]["waste"] * 1000 / 600:g} g par élève. Utilisez cette observation pour adapter le service, présenter le plat et éviter de trop acheter.')
        st.info('Stock fictif utilisable de la veille : 12 kg de pommes de terre crues et 9 kg de carottes crues, non servies et conservées dans des conditions adaptées. Ce stock était déjà acheté avant les deux repas du jeu. Il est distinct des déchets des plateaux, qui ne sont pas remis en cuisine.')
    st.subheader('Comparer les repas pour 600 convives')
    st.caption('Base fixe de 540 € incluse. Les prix tiennent compte du choix du courtier et des aléas.')
    st.table([{'Menu': MENUS[m][0], 'Prix (€)': cost(m, event, s['production'], beef_source=s['beef_source']), 'Budget restant sur deux repas (€)': 3000 - spent - cost(m, event, s['production'], beef_source=s['beef_source'])} for m in options])
    st.caption('Aucun calcul à saisir : le budget s’actualise avec votre proposition.')
    with st.form('menu_' + str(phase)):
        choice = st.selectbox('Menu', options, format_func=lambda k: MENUS[k][0])
        reuse = st.checkbox('Utiliser le stock de légumes crus de la veille dans ce menu') if phase == 3 and event != 'inondation' else False
        if phase == 3:
            st.caption('Menu régional : 12 kg de pommes de terre déjà en stock, donc 108 kg à commander. Autres menus avec carottes : 9 kg déjà en stock, donc 81 kg à commander. La réduction de dépense sera affichée après votre proposition. Le menu de réserve utilise ses propres stocks.')
            adaptation = st.radio('Pour mieux satisfaire les convives demain', ['Présenter le plat et proposer de goûter', 'Prévoir des portions selon la faim et un complément', 'Conserver le service prévu'])
        if st.form_submit_button('Proposer ce menu', type='primary'):
            act('menu', value=choice, reuse=reuse, adaptation=adaptation if phase == 3 else None)
    st.caption('Après votre proposition : le courtier vérifie sa récolte ; les élèves donnent leur avis ; le maître lance la suite.')

def students_panel(s):
    phase = s['phase']
    if phase in (1, 3):
        menu = s['first' if phase == 1 else 'second']
        if menu and s['second'] and (phase != 3 or s['reviewed']):
            st.subheader('Vos deux repas prévus' if phase == 1 else 'Le repas révisé du jour 2')
            if phase == 1:
                st.write('Jour 1 : ' + MENUS[s['first']['id']][0])
                st.write('Jour 2 : ' + MENUS[s['second']['id']][0])
            st.write(MENUS[menu['id']][0])
            if menu.get('adaptation'):
                st.info('Le chef propose pour demain : ' + menu['adaptation'])
            if menu.get('reuse'):
                st.caption('Le chef utilise aussi des légumes crus encore disponibles dans son stock de la veille.')
            st.write('Voici le plat proposé : connaissez-vous ce plat ? Est-il acceptable pour les convives ? Validez ce repas ou demandez un changement au chef avant de valider.')
            st.info('Vous validez les menus ici. Les portions et le libre-service seront choisis au moment du service : jour 1 puis jour 2.')
            if not s['approvals']['students'] and st.button('Valider ce repas pour les convives', type='primary', disabled=s['first']['cost'] + s['second']['cost'] > 3000):
                act('approve')
        return
    if phase not in (2, 4):
        return
    if s['service']:
        st.success('Votre organisation est enregistrée. Le chef cuisinier calcule maintenant les restes.')
        st.write('Plat : ' + SERVICE_LABELS[s['service']])
        st.write('Libre-service : ' + SELF_SERVICE[s['self_service']][0])
        service_time(s)
        with st.expander('Changer notre organisation'):
            service_picker()
    else:
        service_picker()

# Temps fictifs par convive, non mesurés sur la cantine réelle.
PLAT_MINUTES = {'unique': 6, 'adapte': 8, 'explique': 10}
LIBRE_MINUTES = {'tout': 3, 'faim': 2, 'gouter': 4}

def service_time(s):
    if not s['service']:
        return
    duration = PLAT_MINUTES[s['service']] + LIBRE_MINUTES[s['self_service']]
    st.info(f'Votre pause : 30 minutes. Passage au self estimé : {duration} minutes. Temps restant à table : {30 - duration} minutes.')
    st.caption('Durées fictives par convive, attente et choix compris. Elles ne représentent pas la durée du service des 600 élèves.')

def service_picker():
    st.subheader('À la cantine : 30 minutes pour passer au self et manger')
    st.write('Certains élèves ont une petite faim, d’autres une grande faim. Le plat est servi à l’assiette par un agent ; les entrées et desserts sont en libre-service. Vous devez aussi garder du temps pour manger tranquillement.')
    st.table([
        {'Service du plat': SERVICE_LABELS['unique'], 'Ce qui se passe': 'L’agent sert la même quantité à chacun.', 'Avantage et contrainte': 'Passage simple, mais quantité parfois trop grande ou trop petite.', 'Temps estimé': '6 min'},
        {'Service du plat': SERVICE_LABELS['adapte'], 'Ce qui se passe': 'Vous annoncez petite ou grande faim ; un complément reste possible.', 'Avantage et contrainte': 'Quantité adaptée, mais échange et complément à organiser.', 'Temps estimé': '8 min'},
        {'Service du plat': SERVICE_LABELS['explique'], 'Ce qui se passe': 'Le plat est présenté ; vous pouvez goûter puis demander une portion adaptée.', 'Avantage et contrainte': 'Découvrir le plat, mais présentation et dégustation prennent du temps.', 'Temps estimé': '10 min'},
    ])
    st.write('**Entrées et desserts en libre-service :** choisir selon votre faim aide à prendre ce que vous pensez manger. Goûter demande une organisation prévue par la cantine.')
    st.table([
        {'Choix au libre-service': SELF_SERVICE['tout'][0], 'Temps estimé': '3 min'},
        {'Choix au libre-service': SELF_SERVICE['faim'][0], 'Temps estimé': '2 min'},
        {'Choix au libre-service': SELF_SERVICE['gouter'][0], 'Temps estimé': '4 min'},
    ])
    st.caption('Ces durées sont des hypothèses fictives par convive, attente et choix compris. Elles servent à comparer les organisations du jeu.')
    choice = st.radio('Comment servir le plat à l’assiette ?', list(SERVICE_LABELS), format_func=SERVICE_LABELS.get, key='pick_plat')
    free = st.radio('Que faites-vous aux entrées et desserts en libre-service ?', list(SELF_SERVICE), format_func=lambda k: SELF_SERVICE[k][0], key='pick_libre')
    duration = PLAT_MINUTES[choice] + LIBRE_MINUTES[free]
    st.subheader('Le temps pour votre choix')
    st.write(f'**{PLAT_MINUTES[choice]} min** pour le plat + **{LIBRE_MINUTES[free]} min** au libre-service = **{duration} min** de passage estimé.')
    st.success(f'Sur vos 30 minutes, il reste **{30 - duration} minutes pour manger à table**.')
    st.caption('Le temps restant ne détermine pas automatiquement le gaspillage. Les portions et les choix alimentaires ont leurs propres effets fictifs dans le jeu.')
    st.write('Choisissez un service qui permet de manger à sa faim, de limiter les restes et de garder du temps à table.')
    if st.button('Enregistrer nos choix de cantine', type='primary'):
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
    context = (auth['code'], role, phase, s['event'], title, instruction, str(s['first']), str(s['second']), s['service'], s['self_service'], s['climate_ack'], s['waste_reviewed'])
    if st.session_state.get('mission_context') != context:
        st.session_state.mission_context = context
        st.session_state.mission_pending = True
        st.rerun()
    if st.button('❓ Que doit faire mon équipe ?'):
        st.session_state.mission_pending = True
        st.rerun()
    st.info(f'**{title}** — {instruction}')
    st.progress((phase - 1) / 4, text='Préparation → Jour 1 → Pause et adaptation → Jour 2 → Bilan')
    st.subheader(['', 'Préparer les deux journées', 'Jour 1 · Servir et mesurer', 'Entre les deux jours · Adapter le menu', 'Jour 2 · Servir et comparer', 'Bilan des deux journées'][phase])
    seconds = max(0, 1800 - int(time.time() - s['started']))
    st.caption(f'Temps indicatif : {seconds // 60} min {seconds % 60:02d} s')
    spent = sum(s[k]['cost'] for k in ('first', 'second') if s[k])
    x, y, z = st.columns(3)
    x.metric('Budget disponible sur deux repas', f'{3000 - spent:g} €')
    if spent > 3000:
        st.warning(f'Votre prévision dépasse le budget de {spent - 3000:g} €. Le chef doit changer les menus : les commandes ne peuvent pas encore être confirmées.')
    if s['first'] and s['second']:
        beef_count = sum(m['id'] in BEEF for m in [s['first'], s['second']])
        if beef_count:
            st.info(f'Bœuf prévu sur {beef_count} journée(s) : les ruminants émettent du méthane. Alterner avec des légumes secs est une possibilité pour réduire la pression climatique du menu.')
        if s['first']['id'] == s['second']['id']:
            st.caption('Les deux plats sont identiques. Vous pouvez varier pour découvrir d’autres aliments et mieux équilibrer la succession des repas.')
    y.metric('Restes comestibles simulés', '—' if waste(s) is None else f'{waste(s)} kg')
    z.metric('Mesure A.B.C.', 'Calculée automatiquement' if s['measure'] else 'Selon vos choix')
    if s['event']:
        text = 'INONDATION : les récoltes du fournisseur agricole touché sont détruites. Ses frais étaient engagés et ses revenus attendus sont perdus. Les réserves de remplacement sont plus demandées : le menu de secours passe de 900 € à 1 080 €.' if s['event'] == 'inondation' else 'SÉCHERESSE : les rendements du prochain repas diminuent. Les producteurs recalculent leur récolte ; les compléments font monter les prix.'
        st.warning(text + ' Les repas déjà servis ne changent pas. Hypothèses fictives du jeu.')
    if st.session_state.get('abc_error'):
        st.warning(st.session_state.abc_error)
    if phase == 3 and not s['climate_ack']:
        climate_pause(s['day1'], role == 'master', lambda: act('climate_resume'), menus=[s['first']['id'], s['original_second']['id']])
        return
    if role == 'master' and phase < 5:
        ready = (bool(s['first']) and bool(s['second']) and all(s['approvals'].values()) and (phase == 1 or s['reviewed'])) if phase in (1, 3) else s['waste_reviewed']
        st.info('Les manches s’enchaînent automatiquement après les choix des équipes. Vous reprenez la main pour terminer la pause climatique.')
        if st.button('Afficher un indice commun'):
            act('hint')
        st.caption('La sécheresse se déclenche automatiquement entre les deux journées, après la pause illustrée.')
    elif role == 'manager':
        manager_panel(s)
    elif role == 'supplier':
        supplier_panel(s)
    elif role == 'students':
        students_panel(s)
    if phase == 5:
        st.success('Les deux journées sont terminées. Chaque équipe a contribué !')
        st.table([{'Journée': day, 'Restes (kg)': s[key]['waste'], 'Par convive (g)': s[key]['waste'] * 1000 / 600, 'Valeur estimée des restes (€)': round(s[key]['cost'] * s[key]['waste'] / 300)} for day, key in [('Jour 1', 'day1'), ('Jour 2', 'day2')]])
        change = s['day1']['waste'] - s['day2']['waste']
        st.write(f'Évolution : {change:g} kg de restes en moins.' if change >= 0 else f'Évolution : {-change:g} kg de restes en plus. Qu’est-ce qui pourrait être amélioré ?')
        st.write('Quel choix a réduit les restes ? Quelle difficulté a rencontré le courtier ? Que changeriez-vous à votre vraie cantine ?')
    with st.expander('Voir les décisions des trois équipes', expanded=role == 'master'):
        st.write('Offre légumes : ' + (PRODUCTION[s['production']]['name'] if s['production'] else 'À choisir'))
        for k, label in [('first', 'Premier repas'), ('second', 'Prochain repas')]:
            m = s[k]
            st.write(label + ' : ' + (f'{MENUS[m["id"]][0]} · {m["cost"]} €' if m else 'À proposer'))
            if m and m.get('adaptation'):
                st.write('Amélioration proposée par le chef : ' + m['adaptation'])
        if phase in (1, 3):
            st.write('Courtier : ' + ('✓ livraison confirmée' if s['approvals']['supplier'] else 'mission en cours') + ' · Élèves : ' + ('✓ avis validé' if s['approvals']['students'] else 'avis attendu'))
        if s['service']:
            st.write('Plat : ' + SERVICE_LABELS[s['service']])
            st.write('Entrées et desserts : ' + SELF_SERVICE[s['self_service']][0])
            service_time(s)
    if s['hint']:
        st.info('Les aides individuelles sont disponibles à chaque calcul. Identifiez ce qui est demandé : une quantité totale, une quantité par élève ou un pourcentage.')
    st.caption('Prix, rendements et restes fictifs. Aucun mode de production ne garantit à lui seul un meilleur rendement. A.B.C. est simulé. Le gaspillage ne provoque pas directement l’aléa de cette partie.')

game()
if st.session_state.pop('mission_pending', False):
    try:
        show_mission(auth['role'], store.read(auth))
    except ValueError as exc:
        st.error(str(exc))
