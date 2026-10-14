"""Cartes A.B.C. originales : photographies sous licence et données sourcées."""
from pathlib import Path
from functools import lru_cache
import base64
import html
import json
import streamlit as st
import abc_game as GAME_ENGINE

NUTRITION_URL = 'https://www.mangerbouger.fr/manger-mieux/a-tout-age-et-a-chaque-etape-de-la-vie/enfants-et-adolescents-de-4-a-17-ans/les-recommandations-alimentaires-pour-les-4-17-ans'
PHOTO_ROOT = Path(__file__).parent / 'assets' / 'photos'
UNEP_URL = 'https://www.unep.org/news-and-stories/press-release/world-squanders-over-1-billion-meals-day-un-report'
BEEF_URL = 'https://impactco2.fr/outils/alimentation/boeuf'
PORK_URL = 'https://impactco2.fr/outils/alimentation/porc'
CHICKEN_URL = 'https://impactco2.fr/outils/alimentation/poulet'
IPCC_URL = 'https://report.ipcc.ch/ar6syr/headline.html'
WATER_URL = 'https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-4/'

@lru_cache(maxsize=6)
def photo_data(key):
    return 'data:image/jpeg;base64,' + base64.b64encode((PHOTO_ROOT / (key + '.jpg')).read_bytes()).decode('ascii')

STYLE = '''<style>
.abc-photo-card{border-radius:14px;overflow:hidden;background:#fff;border:1px solid #dce5d9;box-shadow:0 12px 32px rgba(20,57,43,.09);margin:0 0 12px;color:#183d34}
.abc-photo-card .visual{height:225px;position:relative;overflow:hidden;background:#d9e6d8}
.abc-photo-card img{width:100%;height:100%;object-fit:cover;display:block}
.abc-photo-card .visual:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,transparent 35%,rgba(14,35,26,.6))}
.abc-photo-card .tag{position:absolute;top:16px;left:16px;background:#fff3dc;color:#674923;border-radius:30px;font:700 12px system-ui;padding:8px 12px;z-index:1}
.abc-photo-card .body{padding:20px 24px}
.abc-photo-card .figure{font:800 clamp(30px,3.4vw,42px) system-ui;color:#245b48;line-height:1.05;margin:0 0 9px}
.abc-photo-card .unit{font:600 14px system-ui;color:#547466;margin:0 0 9px;line-height:1.5}
.abc-photo-card h3{font:700 22px system-ui;line-height:1.2;margin:0 0 12px}
.abc-photo-card p{font:16px/1.5 system-ui;margin:0 0 9px}
.abc-photo-card .action{background:#edf5e9;border-left:4px solid #568f58;padding:8px 10px;border-radius:8px;font:600 14px/1.35 system-ui}
.abc-photo-card .source{font:12px/1.6 system-ui;color:#607268;margin-top:8px}
.abc-photo-card a{color:#356a57;text-decoration:underline}
.abc-carbon{background:#173e34;color:#fff;border-radius:20px;padding:14px;margin:0 0 12px}
.abc-carbon h3{color:#fff;margin:0 0 12px;font:700 22px system-ui}
.abc-carbon .values{display:flex;gap:14px;flex-wrap:wrap}
.abc-carbon .value{flex:1;min-width:125px;background:#ffffff12;border-radius:12px;padding:10px}
.abc-carbon strong{font:800 25px system-ui;display:block;color:#f2d392}
.abc-carbon small{display:block;margin-top:6px;line-height:1.5}
</style>'''

def render_photo_card(index, key, number, unit, title, text, action, source_label, source_url=None, note=''):
    credits = json.loads((PHOTO_ROOT / 'credits.json').read_text())[key]
    e = html.escape
    source = f'<a href="{e(source_url,quote=True)}" target="_blank">{e(source_label)}</a>' if source_url else e(source_label)
    attribution = f'Photo : {credits["author"]} · {credits["license"]} · recadrée.'
    st.markdown(f'''<article class="abc-photo-card">
<div class="visual"><img src="{photo_data(key)}" alt="{e(title,quote=True)}"><span class="tag">CARTE {index:02d} · A.B.C.</span></div>
<div class="body"><div class="figure">{e(number)}</div><div class="unit">{e(unit)}</div>
<h3>{e(title)}</h3><p>{e(text)}</p><div class="action">{e(action)}</div>
<details class="source"><summary>Sources et précisions</summary>{source}<br>{e(note)}<br><a href="{e(credits['source'],quote=True)}" target="_blank">{e(attribution)}</a></details></div></article>''', unsafe_allow_html=True)


def carbon_comparison():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('''<section class="abc-carbon"><h3>Pour 1 kg de viande : combien de gaz à effet de serre ?</h3><div class="values">
<div class="value">Bœuf<strong>28</strong><small>kg CO₂e par kg d’aliment</small></div>
<div class="value">Porc<strong>6,67</strong><small>kg CO₂e par kg d’aliment</small></div>
<div class="value">Poulet<strong>4,56</strong><small>kg CO₂e par kg d’aliment</small></div>
</div></section>''', unsafe_allow_html=True)
    st.caption('CO₂e veut dire « équivalent CO₂ » : cette unité permet de comparer l’effet sur le climat de plusieurs gaz. Les chiffres ci-dessus concernent 1 kg de viande, sur son cycle de vie.')
    st.caption('Valeurs moyennes : ADEME / Impact CO₂, Agribalyse 3.2, mise à jour du 15 janvier 2025. Pour comprendre : 1 kg de bœuf ≈ 28 kg CO₂e ; 1 kg de poulet ≈ 4,56 kg CO₂e.')
    st.markdown('[Bœuf](' + BEEF_URL + ') · [Porc](' + PORK_URL + ') · [Poulet](' + CHICKEN_URL + ')')
    st.info('À poids égal : une portion de bœuf ≈ les émissions de six portions de poulet. On compare ici leur impact climatique, pas les portions à manger.')
    st.caption('Ces références ne mesurent pas précisément le bœuf du Brésil ou d’Argentine, le porc du Ventoux ou votre fournisseur. Le poisson varie beaucoup selon l’espèce, la pêche ou l’élevage : aucun chiffre unique n’est attribué au poisson générique du jeu.')


def climate_pause(day1, is_master, resume, menus=None):
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader('Du plateau au climat · Six cartes pour comprendre')
    st.write('Votre premier repas est terminé. Lisez les cartes pour comprendre ce que vos choix changent pour le climat. Le maître lancera ensuite la suite.')
    definitions = [
        ('farm', '600', 'repas à préparer chaque jour dans votre collège fictif', 'Avant l’assiette, il y a toute une chaîne', 'Cultiver, élever, transporter, conserver et cuisiner demande des ressources. Quand on adapte les commandes aux besoins, on évite de mobiliser des ressources pour des aliments qui finiront jetés.', 'Votre levier : commander selon les besoins réels.', 'Données du scénario A.B.C.', None, 'La photo illustre une récolte ; ce n’est pas votre fournisseur réel.'),
        ('waste', '8 à 10 %', 'des émissions mondiales de gaz à effet de serre', 'Le gaspillage dépasse la poubelle', 'Cette estimation concerne les pertes et le gaspillage alimentaires dans le monde. Produire de la nourriture qui n’est pas mangée mobilise inutilement des ressources et contribue aux émissions.', 'Votre levier : prendre selon sa faim et ajuster les achats.', 'PNUE · Food Waste Index 2024', UNEP_URL, 'Estimation mondiale, pas le pourcentage d’émissions de votre collège. Photo de biodéchets contenant aussi des parties non comestibles.'),
        ('cattle', '14 200 km contre 2 300 km', 'en voiture diesel : l’équivalent climatique de la viande pour vos 600 élèves', 'Bœuf ou poulet : combien de kilomètres en voiture ?', 'Pour 600 portions de viande de 120 g, le bœuf représente environ les émissions de 14 200 km en voiture diesel. Le poulet représente environ 2 300 km en voiture diesel. Les élèves mangent la même quantité de viande, mais l’impact sur le climat change beaucoup.', 'Votre levier : varier les protéines et comparer les fournisseurs.', 'ADEME · Impact CO₂ · Agribalyse 3.2', BEEF_URL, 'Ordre de grandeur : portions de 120 g, viande seule ; bœuf 2 016 kg CO₂e, poulet 328 kg CO₂e. Un trajet = un aller simple d’environ 800 km. Voiture moyenne diesel : 142 g CO₂e/km (Impact CO₂, modèle 2025). Valeurs arrondies, issues de moyennes.'),
        ('industry', '+1,1 °C', 'température mondiale moyenne en 2011–2020 par rapport à 1850–1900', 'Une hausse moyenne qui change les conditions', 'Les activités humaines ont renforcé l’effet de serre et réchauffé le climat. Les émissions de l’alimentation s’ajoutent à celles des autres activités. Ce chiffre du GIEC porte sur une période précise.', 'Votre levier : réduire les émissions évitables, notamment le gaspillage.', 'GIEC · Rapport de synthèse 2023', IPCC_URL, 'Ce n’est pas la température actuelle d’une journée. Photo d’une centrale à Rostock ; un panache visible ne mesure pas le CO₂.'),
        ('water', 'L’eau circule', 'évaporation → nuages → précipitations → sols et cours d’eau', 'Le réchauffement modifie le cycle de l’eau', 'Un climat plus chaud modifie l’évaporation et les précipitations. Les changements dépendent des régions : certains lieux risquent davantage de manquer d’eau, d’autres de subir des pluies intenses.', 'Votre levier : anticiper les risques et garder des alternatives.', 'GIEC · Eau, impacts et adaptation', WATER_URL, 'Photo illustrative du Mékong, au Laos ; elle ne représente pas la sécheresse fictive du jeu.'),
        ('drought', '−50 %', 'de carottes disponibles au jour 2 dans la simulation', 'La sécheresse atteint votre prochain menu', 'Dans le jeu, l’offre de carottes passe de 90 à 45 kg. Le responsable des achats doit trouver un complément et le chef peut changer sa recette. Les quantités et les surcoûts du jeu sont fictifs.', 'Votre levier : revoir ensemble menu, portions et approvisionnement.', 'Scénario A.B.C. · hypothèse pédagogique', None, 'Photo réelle de sol sec à Chowilla, en Australie ; ce n’est pas la ferme fictive du jeu.'),
    ]
    for offset in range(0, len(definitions), 3):
        for index, (column, args) in enumerate(zip(st.columns(3), definitions[offset:offset + 3]), offset + 1):
            with column:
                render_photo_card(index, *args)
    st.info(f'Votre jour 1 : {day1["waste"]} kg de restes comestibles simulés. Le chiffre du jeu et les chiffres mondiaux ci-dessus ne décrivent pas la même échelle.')
    if menus and sum(m in ('boeuf', 'boeuf_bresil', 'boeuf_argentine') for m in menus) == 2:
        st.warning('Votre prévision contenait du bœuf aux deux repas. Une offre moins chère peut résoudre le budget sans supprimer les émissions liées à l’élevage. Vous pouvez varier le jour 2.')
    carbon_comparison()
    with st.expander('Comprendre la comparaison avec la voiture'):
        st.write('On divise les émissions de la viande par 0,142 kg CO₂e par kilomètre de voiture diesel. On compare des émissions sur le cycle de vie ; les kilomètres ne représentent pas le transport réel de la viande.')
        st.markdown('[Impact CO₂ — voiture moyenne diesel](https://impactco2.fr/outils/transport/voiturethermique) · [Itinéraire Marseille–Paris, environ 800 km](https://fr.mappy.com/itineraire/75000-paris/13000-marseille)')
    st.warning('La sécheresse est une mise en situation. Les déchets du premier repas ne l’ont pas causée à eux seuls : les émissions et les risques climatiques s’accumulent à grande échelle et sur une longue durée.')
    st.caption('Textes, chiffres mis en contexte et présentation propres à A.B.C. Aucun texte ni visuel repris des cartes officielles de La Fresque du Climat.')
    if is_master:
        if st.button('Suivant : adapter le jour 2', type='primary'):
            resume()
    else:
        st.info('Le maître reprendra la mission après ce temps commun.')


def menu_consequences(s):
    if not s['first'] or not s['second']:
        return
    total = s['first']['cost'] + s['second']['cost']
    beef_count = sum(m['id'] in ('boeuf', 'boeuf_bresil', 'boeuf_argentine') for m in (s['first'], s['second']))
    if total <= 3000 and beef_count < 2:
        return
    st.markdown(STYLE, unsafe_allow_html=True)
    render_photo_card(1, 'cattle', f'{total:g} €', 'pour les deux menus de 600 repas', 'Votre choix a des conséquences', 'Le budget des deux journées est de 3 000 €. Alterner les plats peut faire varier le coût, les apports alimentaires et les impacts environnementaux.', 'Essayez une autre composition, puis regardez ce qui change.', 'Scénario A.B.C. · prix fictifs', None)
    if total > 3000:
        st.error(f'Budget : il manque {total - 3000:g} €. Les commandes restent en attente : changez un menu ou comparez une autre offre.')
    if beef_count == 2:
        st.warning('Deux repas au bœuf : peu de variété dans votre prévision. L’équilibre se construit sur plusieurs repas et sur la semaine ; ce n’est pas un diagnostic de santé.')
        st.write('Les légumes secs apportent des protéines végétales et des fibres. Gardez aussi légumes, féculents et fruits ; la viande n’est pas nécessaire à chaque repas.')
        st.markdown('[Repères pour les 4–17 ans — Manger Bouger](' + NUTRITION_URL + ')')
        carbon_comparison()


def sourcing_card():
    carbon_comparison()
    with st.expander('Lire les différences entre les offres'):
        st.table([
            {'Offre': 'Bœuf brésilien ou argentin', 'À regarder': 'Élevage, méthane, alimentation, terres et transport.', 'Point clé': 'Le pays seul ne suffit pas à déterminer l’empreinte.'},
            {'Offre': 'Bœuf régional', 'À regarder': 'Élevage et transport.', 'Point clé': 'Local ne garantit pas une faible empreinte.'},
            {'Offre': 'Porc du Ventoux', 'À regarder': 'Ferme, alimentation animale, effluents, énergie.', 'Point clé': 'Le repère porc est une moyenne, pas une mesure de cette ferme.'},
            {'Offre': 'Poisson', 'À regarder': 'Espèce, pêche ou élevage, carburant, conservation.', 'Point clé': 'Empreinte variable : pas de valeur unique pour tous les poissons.'},
        ])
        st.caption('Cours et prix fictifs. Les chiffres ADEME sont des références documentaires indépendantes des prix du scénario.')

def final_debate(s, role, send):
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader('Dernière carte · Prix, provenance et climat : que choisit-on vraiment ?')
    st.write('Vous préparez le prochain repas pour les mêmes 600 élèves. Le prix le plus bas suffit-il pour choisir ? Comparez les trois offres, leur provenance et leurs repères carbone, puis défendez votre choix.')
    a, b, c = st.columns(3)
    with c:
        render_photo_card(3, 'cattle', '396 €', 'pour 72 kg de bœuf dans le scénario : 600 portions de 120 g', 'Offre C · Bœuf brésilien', 'Le prix est le plus bas de ces trois offres fictives. Mais le repère moyen du bœuf est de 28 kg CO₂e par kg : pour ces 600 portions, environ les émissions de 14 200 km en voiture diesel.', 'Prix, élevage, alimentation, terres et transport : quelles informations demander au courtier ?', 'ADEME · Agribalyse 3.2 · Impact CO₂', BEEF_URL, 'Prix et origine fictifs. Le carbone est une moyenne pour le bœuf, pas une mesure de cet élevage brésilien. Photo illustrative.')
    with a:
        render_photo_card(1, 'chicken', '432 €', 'pour 72 kg de poulet dans le scénario : 600 portions de 120 g', 'Offre A · Poulet brésilien', 'Repère carbone moyen du poulet : 4,56 kg CO₂e par kg. Pour 600 portions : environ 328 kg CO₂e, soit l’équivalent de 2 300 km en voiture diesel.', 'À vérifier : élevage, alimentation des animaux, traçabilité et transport.', 'ADEME · Agribalyse 3.2 · Impact CO₂', CHICKEN_URL, 'Le prix et l’origine de cette offre sont fictifs. Le carbone est une moyenne de référence pour le poulet, pas une mesure de cet élevage brésilien. Photo illustrative.')
    with b:
        render_photo_card(2, 'pig', '504 €', 'pour 72 kg de porc dans le scénario : 600 portions de 120 g', 'Offre B · Porc du Ventoux', 'Repère carbone moyen du porc : 6,67 kg CO₂e par kg. Pour 600 portions : environ 480 kg CO₂e, soit l’équivalent de 3 400 km en voiture diesel.', 'À vérifier : ferme, pratiques d’élevage, alimentation, prix versé au producteur.', 'ADEME · Agribalyse 3.2 · Impact CO₂', PORK_URL, 'Le prix et l’origine de cette offre sont fictifs. Le carbone est une moyenne de référence pour le porc, pas une mesure de la ferme du Ventoux. Photo illustrative.')
    st.info('Dans le scénario : bœuf brésilien 396 €, poulet brésilien 432 €, porc du Ventoux 504 €. Le moins cher à acheter a ici le repère carbone moyen le plus élevé. Ces prix fictifs et les références carbone ne mesurent pas les mêmes choses.')
    st.write('**La provenance mérite une enquête :** comment sont élevés les animaux ? Avec quelle alimentation ? Y a-t-il un changement d’usage des terres ? Quel transport et quelle conservation ? Quel prix reçoit le producteur ? Être proche ou loin ne répond pas à toutes ces questions.')
    st.write('**Questions pour débattre :** que gagne-t-on avec chaque offre ? Quelles informations manquent ? Peut-on soutenir une ferme proche tout en variant les sources de protéines au fil des menus ?')
    labels = {'E': 'Bœuf brésilien : priorité au prix, malgré le repère carbone moyen élevé', 'A': 'Poulet brésilien : priorité au prix et au repère carbone moyen', 'B': 'Porc du Ventoux : priorité à la proximité, avec des pratiques à vérifier', 'C': 'Alterner les offres et des repas avec légumes secs', 'D': 'Demander les données des fournisseurs avant de décider'}
    if role != 'master':
        st.caption('Il n’y a pas de bonne réponse imposée. Après échange, retenez un choix et un argument.')
        with st.form('debate_vote'):
            choice = st.radio('La proposition de notre équipe', list(labels), format_func=labels.get)
            reason = st.selectbox('Notre argument principal', ['Budget de la cantine', 'Émissions de gaz à effet de serre', 'Lien avec les producteurs proches', 'Variété des repas', 'Informations et traçabilité'])
            if st.form_submit_button('Partager notre choix pour le débat', type='primary'):
                send('debate', value=choice, reason=reason)
    votes = s.get('debate_votes', {})
    if votes:
        from abc_game import ROLES
        st.table([{'Équipe': ROLES[r], 'Choix': labels[v['choice']], 'Argument': v['reason']} for r, v in votes.items()])
    if role == 'master':
        st.info('Donnez la parole aux trois équipes. Aidez-les à distinguer les chiffres documentés, les hypothèses de prix et les informations à vérifier.')
        if len(votes) == 3 and not s.get('debate_decision'):
            with st.form('debate_decision'):
                decision = st.selectbox('Notre décision collective après le débat', list(labels), format_func=labels.get)
                if st.form_submit_button('Afficher notre décision collective', type='primary'):
                    send('debate_close', value=decision)
    if s.get('debate_decision'):
        st.success('Décision collective : ' + labels[s['debate_decision']])
        st.write('Pour votre vraie cantine : quelle information demander et quel geste changer dès le prochain repas ?')
    with st.expander('Sources et hypothèses de la comparaison'):
        st.markdown('[Poulet — ADEME / Agribalyse](' + CHICKEN_URL + ') · [Porc — ADEME / Agribalyse](' + PORK_URL + ') · [Voiture moyenne diesel — ADEME](https://impactco2.fr/outils/transport/voiturethermique)')
        st.write('Calculs automatiques : bœuf 72 × 28 = 2 016 kg CO₂e ; poulet 72 × 4,56 = 328,32 kg CO₂e ; 72 × 6,67 = 480,24 kg CO₂e. Un trajet illustratif est un aller simple d’environ 800 km, avec le facteur de 142 g CO₂e/km. Les équivalents sont arrondis et comparent des cycles de vie. Les prix sont fictifs ; la source carbone est Agribalyse 3.2, mise à jour le 15 janvier 2025.')

FAO_URL = 'https://www.fao.org/forest-resources-assessment/remote-sensing/remote-sensing-survey/en'

def welcome_cards():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader('Avant de jouer · La cantine commence bien avant le plateau')
    st.write('Lisez ces quatre fiches pendant que les autres équipes se connectent. Le maître lancera ensuite le jeu. Le chronomètre ne tourne pas encore.')
    a, b, c, d = st.columns(4)
    with a:
        render_photo_card(1, 'farm', 'Cultiver et élever', 'Des activités humaines pour nous nourrir', 'D’où vient notre repas ?', 'Les légumes poussent dans les champs. Les animaux ont besoin de nourriture. Produire demande des sols, de l’eau et de l’énergie ; l’élevage de ruminants émet aussi du méthane, un gaz à effet de serre.', 'À observer : quel plat choisir, et pour combien de convives ?', 'GIEC · Synthèse 2023', IPCC_URL)
    with b:
        render_photo_card(2, 'water', 'Un puits de carbone', 'Les forêts captent du CO₂ et stockent du carbone', 'Les arbres, des alliés pour le climat', 'Avec la lumière, les feuilles absorbent du CO₂ et libèrent de l’oxygène : c’est la photosynthèse. Le carbone sert à fabriquer le bois, les feuilles et les racines ; une partie se retrouve dans le sol. Une forêt est un puits de carbone lorsqu’elle absorbe plus de carbone qu’elle n’en libère.', 'Pour la cantine : demander des produits dont la production ne détruit pas les forêts.', 'ONF · Photosynthèse et puits de carbone', 'https://www.onf.fr/onf/+/1ba8::la-foret-un-indispensable-pour-une-planete-decarbonee.html', 'Photo illustrative : végétation sur les rives du Mékong, au Laos.')
        st.info('Imaginez 10 parts de CO₂ émises par les activités humaines : les plantes et les sols des continents en absorbent environ 3. Les forêts font partie de ce grand puits de carbone terrestre.')
        st.caption('Repère : 29 % des émissions humaines de CO₂ absorbées par les écosystèmes terrestres en moyenne en 2014–2023, selon le Global Carbon Budget 2024. Ce chiffre concerne l’ensemble des plantes et sols, pas uniquement les forêts.')
        st.markdown('[Source du repère — Global Carbon Budget 2024](https://globalcarbonbudget.org/gcb-2024/faqs/)')
        st.write('**Quand une forêt est détruite :** du carbone stocké peut être libéré, et des arbres qui auraient capté du CO₂ disparaissent. Créer des cultures ou des pâturages à sa place peut donc peser sur le climat. La forêt abrite aussi des êtres vivants et participe au cycle de l’eau.')
        st.caption('« Poumon vert » est une image : les arbres respirent aussi. Le carbone n’est pas éliminé pour toujours ; incendies et décomposition peuvent le remettre dans l’atmosphère. Protéger les forêts accompagne la réduction de nos émissions.')

    with c:
        render_photo_card(3, 'waste', 'Du champ au plateau', 'Transporter · conserver · cuisiner · manger', 'Jeter, c’est gaspiller toute cette chaîne', 'Avant la cantine, les aliments ont déjà demandé du travail et des ressources. Le transport et la conservation comptent, mais la distance seule ne suffit pas à classer les aliments selon leur impact climatique.', 'À observer : peut-on prendre à sa faim et éviter les achats inutiles ?', 'ADEME · Impact CO₂ / PNUE', BEEF_URL, 'Les photos sont illustratives ; fiches A.B.C. originales.')
    with d:
        render_photo_card(4, 'industry', 'Sur 10 parts de CO₂', '≈ 3 vers les terres · ≈ 2 à 3 vers les océans · ≈ 4 à 5 restent dans l’air', 'Où va le CO₂ que nous émettons ?', 'L’atmosphère est l’enveloppe d’air autour de la Terre. Son effet de serre naturel garde une température permettant la vie. Nos émissions supplémentaires renforcent cet effet de serre. Les plantes et les océans absorbent une partie du CO₂ ; le reste s’accumule dans l’air et contribue au réchauffement.', 'Réduire nos émissions et protéger les puits de carbone sont deux actions complémentaires.', 'Global Carbon Budget 2024 · moyenne 2014–2023', 'https://globalcarbonbudget.org/gcb-2024/faqs/', '29 % vers le puits terrestre, 26 % vers le puits océanique, environ 45 % restant dans l’atmosphère. Parts du CO₂ émis, pas de tous les gaz à effet de serre. Photo illustrative d’une centrale ; le panache visible n’est pas une mesure du CO₂.')
        st.write('**Photosynthèse :** avec la lumière, les plantes absorbent du CO₂ pour fabriquer leur matière et libèrent de l’oxygène. Les arbres ne sont pas seuls : les autres plantes et le phytoplancton des océans font aussi de la photosynthèse.')
        st.write('**Océans :** le CO₂ se dissout dans l’eau. Les échanges et la circulation océanique participent à son stockage ; les organismes marins interviennent aussi dans le cycle du carbone. L’absorption de CO₂ contribue à l’acidification des océans : cette aide au climat a des conséquences sur la vie marine.')
        st.caption('Un puits de carbone absorbe davantage de carbone qu’il n’en libère. Ces parts sont des moyennes sur une période précise : elles changent d’une année à l’autre. Elles ne signifient pas que chaque repas est automatiquement compensé.')
        st.markdown('[Océans et acidification — NOAA](https://www.noaa.gov/education/resource-collections/ocean-coasts/ocean-acidification)')
        st.subheader('30 juillet 2026 · Le Jour du dépassement mondial')
        st.write('Imaginez un budget nature prévu pour douze mois. Dès la fin juillet, notre demande a atteint ce que la Terre peut renouveler en une année. Nous continuons ensuite à consommer en entamant les réserves naturelles et en accumulant notamment du CO₂.')
        st.info('Les forêts et les océans absorbent du carbone, mais notre demande dépasse la capacité de renouvellement de la planète. À la cantine, éviter le gaspillage et comparer les menus aide à réduire cette demande.')
        st.caption('Indicateur calculé par Global Footprint Network : ressources biologiques et services écologiques, dont l’absorption du CO₂. Ce n’est pas la date où toutes les ressources sont épuisées, ni un budget de CO₂ uniquement. Date mondiale pour 2026, pas une date propre au collège.')
        st.markdown('[Date et méthode — Global Footprint Network](https://overshoot.footprintnetwork.org/newsroom/press-release-june-2026-english/)')

    st.info('Chef : préparer deux menus. Élèves : exprimer vos envies. Responsable des achats : consulter vos offres, puis répondre aux demandes. Les choix sont proposés par le jeu : aucun calcul à saisir.')

def reflection_card(note, s, is_master, resume):
    st.markdown(STYLE, unsafe_allow_html=True)
    st.warning('⏸ Pause commune · Le chronomètre est arrêté sur tous les écrans.')
    st.caption('Décision transmise par : ' + {'manager': 'le chef cuisinier', 'students': 'les élèves', 'supplier': 'le responsable des achats'}.get(note['role'], 'le maître'))
    render_photo_card(note['number'], note['photo'], 'Une décision → des effets', 'Lire · comprendre · en discuter', note['title'], note['effect'], note['question'], 'A.B.C. · Conséquences du scénario et repères sourcés', None, 'Prix, stocks et restes : simulation. Repères climatiques : sources ci-dessous.')
    if note.get('action') == 'plans':
        menu_climate_cards()
        with st.expander('Analyse des menus et observations de notre cantine'):
            chef_nutrition(s)
            abc_observations()
    elif note['role'] in ('students', 'manager'):
        abc_observations()
    if note['role'] == 'supplier' and note['photo'] == 'farm':
        purchase_reveal(s)
    if s.get('first') and s.get('second'):
        st.write('**Jour 1 :** ' + GAME_ENGINE.MENUS[s['first']['id']][0])
        st.write('**Jour 2 :** ' + GAME_ENGINE.MENUS[s['second']['id']][0])
        st.metric('Budget restant sur les deux repas', f"{3000 - s['first']['cost'] - s['second']['cost']:g} €")
    st.markdown('[Agriculture et climat — GIEC](' + IPCC_URL + ') · [Empreinte des aliments — ADEME](' + BEEF_URL + ') · [Déforestation — FAO](' + FAO_URL + ')')
    if is_master:
        if st.button('Reprendre le jeu pour toutes les équipes', type='primary'):
            resume()
    else:
        st.info('Lisez la fiche et échangez dans votre équipe. Le maître reprend le jeu lorsque vous êtes prêts.')

MEAT_FACTORS = {'boeuf': 28, 'boeuf_bresil': 28, 'boeuf_argentine': 28, 'regional': 4.56, 'importe': 4.56, 'porc_ventoux': 6.67}

def choice_footprint(s):
    engine = GAME_ENGINE
    menus = [s[k] for k in ('first', 'second') if s.get(k)]
    if not menus and s.get('preferences'):
        menus = [{'id': k, 'cost': engine.cost(k)} for k in s['preferences']]
    if not menus:
        return
    st.subheader('Ce que vos choix engagent · Prix et empreinte climatique')
    rows = []
    for index, menu in enumerate(menus, 1):
        factor = MEAT_FACTORS.get(menu['id'])
        footprint = 72 * factor if factor is not None else None
        rows.append({'Journée': index, 'Menu choisi': engine.MENUS[menu['id']][0], 'Coût fictif (€)': menu['cost'], 'Viande seule : kg CO₂e pour 600 portions': round(footprint) if footprint is not None else 'Non chiffré pour cet aliment', 'Autant d’émissions qu’un parcours en voiture diesel': f'≈ {round(footprint / .142 / 100) * 100:,} km'.replace(',', ' ') if footprint is not None else '—'})
    for column, menu in zip(st.columns(len(menus)), menus):
        factor = MEAT_FACTORS.get(menu['id'])
        with column:
            if factor is not None:
                km = round(72 * factor / .142 / 100) * 100
                key = 'cattle' if menu['id'] in ('boeuf', 'boeuf_bresil', 'boeuf_argentine') else 'pig' if menu['id'] == 'porc_ventoux' else 'chicken'
                render_photo_card(1, key, f'≈ {km:,} km'.replace(',', ' '), 'en voiture diesel : autant d’émissions que la viande pour 600 élèves', engine.MENUS[menu['id']][0], 'Ce chiffre compare les émissions de la viande à celles d’une voiture. Les aliments n’ont pas parcouru cette distance !', 'Le type de viande change beaucoup l’empreinte. Comparez les kilomètres.', 'ADEME · Impact CO₂ / Agribalyse 3.2', BEEF_URL if key == 'cattle' else PORK_URL if key == 'pig' else CHICKEN_URL, '600 portions de 120 g ; viande seule. Valeur moyenne, pas mesure du fournisseur. Voiture diesel moyenne à 142 g CO₂e/km. Kilomètres arrondis à la centaine.')
            else:
                st.info(engine.MENUS[menu['id']][0] + ' : recette complète nécessaire pour donner un équivalent kilométrique fiable.')
    with st.expander('Chiffres et méthode de comparaison'):
        st.table(rows)
        st.caption('600 portions de 120 g = 72 kg de viande. Facteurs moyens ADEME : bœuf 28 ; porc 6,67 ; poulet 4,56 kg CO₂e/kg. Trajet illustratif de 800 km, voiture diesel moyenne à 142 g CO₂e/km. Viande seule : ce n’est pas l’empreinte complète du repas. Ces valeurs de cycle de vie incluent déjà le transport moyen : il ne faut pas l’ajouter une deuxième fois.')
    st.markdown('[Bœuf](' + BEEF_URL + ') · [Porc](' + PORK_URL + ') · [Poulet](' + CHICKEN_URL + ') · [Voiture](https://impactco2.fr/outils/transport/voiturethermique)')
    st.info('Proche ou lointain ? Un poulet importé garde ici le repère moyen du poulet, et un bœuf local le repère moyen du bœuf. Nous ne connaissons pas l’empreinte précise de ces fournisseurs. Pour les départager, il faudrait leurs pratiques, l’alimentation des animaux, le mode de transport et les garanties contre la déforestation.')
    st.write('**Les émissions s’additionnent :** cultures et alimentation des animaux, élevage, changements d’usage des terres, énergie, transport, conservation et cuisine. Ce sont plusieurs gaz : CO₂, méthane et protoxyde d’azote notamment. Le CO₂e permet de comparer leurs effets. Les activités qui émettent renforcent l’effet de serre naturel ; l’accumulation du CO₂ contribue au réchauffement durable.')
    st.markdown('[Repères scientifiques — GIEC](' + IPCC_URL + ')')
    if len(menus) == 2:
        long_term_choices(menus)

def long_term_choices(menus):
    engine = GAME_ENGINE
    total = sum(m['cost'] for m in menus)
    reference = 2 * engine.cost('regional')
    saving = reference - total
    with st.expander('Si ces choix se répètent : 1 à 4 ans, puis au-delà', expanded=False):
        st.write('**Court terme : les dépenses.** Imaginons 180 jours de cantine par an, soit 90 répétitions de vos deux repas, toujours pour 600 convives. Comparaison : deux menus au poulet régional conventionnel à 2 880 € au total. Cette référence sert à comparer les prix ; ce n’est pas un modèle de variété alimentaire.')
        st.table([{'Horizon': f'{years} an(s)', 'Dépenses simulées (€)': round(total * 90 * years), 'Économie face à la référence (€), négatif = surcoût': round(saving * 90 * years)} for years in (1, 2, 4)])
        st.caption('Projection pédagogique à prix constants : aucune inflation, aucun changement de fréquentation. Les prix sont fictifs. Le menu ne devrait pas rester identique toute l’année. La valeur des restes reste comprise dans les achats : on ne la retranche pas une seconde fois.')
        known = [72 * MEAT_FACTORS[m['id']] for m in menus if m['id'] in MEAT_FACTORS]
        if known:
            st.write('**Moyen et long terme : les émissions se répètent aussi.** Voici uniquement la composante viande chiffrée de vos deux repas, répétée dans la même hypothèse. Les autres aliments et étapes non couverts ne sont pas comptés ici.')
            st.table([{'Durée de répétition': f'{years} an(s)', 'Viande chiffrée : émissions cumulées (tonnes CO₂e)': round(sum(known) * 90 * years / 1000, 1)} for years in (1, 4, 10)])
        st.write('**Pourquoi regarder plus loin ?** Les émissions de CO₂ s’accumulent et contribuent au réchauffement. Avec le réchauffement, les risques de fortes chaleurs et, selon les régions, de sécheresses et de pluies intenses augmentent. Des récoltes peuvent devenir plus fragiles ; disponibilité et prix peuvent être affectés. Ces risques dépendent aussi des autres émissions, des territoires et des mesures d’adaptation.')
        st.caption('Les horizons 1, 4 et 10 ans sont des fenêtres de comparaison du jeu, pas les dates annoncées d’une catastrophe. On ne convertit pas les émissions de cette cantine en degrés de réchauffement ni en sécheresse locale. Les tonnes CO₂e cumulées ne décrivent pas exactement l’évolution physique de chaque gaz.')
        st.success('Question à débattre : ce qui coûte moins cher aujourd’hui est-il forcément le meilleur choix si l’on considère aussi la variété, le gaspillage, les producteurs et le climat ?')
        st.markdown('[GIEC · Réchauffement, risques et adaptation](' + IPCC_URL + ') · [GIEC · Eau](' + WATER_URL + ')')

def abc_observations():
    st.subheader('Dans notre vraie cantine · Ce que révèle A.B.C.')
    st.caption('Extraits du collège J. Giono, service du 1er octobre 2026, consultés le 14 octobre. Ces observations sont distinctes des 600 repas fictifs du jeu.')
    a, b = st.columns(2)
    with a:
        st.markdown('### Paupiette · Environ un tiers non mangé')
        st.image(str(Path(__file__).parent / 'assets' / 'abc' / 'paupiette.jpg'), width='stretch')
        st.write('**30 portions observées · 67 % mangé.** Le détail mentionne du bœuf et une sauce italienne. Sept élèves disent « pas aimé » ; six disent « pas le temps ».')
        st.info('A.B.C. estime 4,39 kg de restes évitables attribués à cet aliment. Le 5,27 kg CO₂e de la capture utilise un facteur de travail par défaut : la recette doit être renseignée pour une estimation adaptée.')
    with b:
        st.markdown('### Chou-fleur · Environ trois quarts non mangés')
        st.image(str(Path(__file__).parent / 'assets' / 'abc' / 'chou-fleur.jpg'), width='stretch')
        st.write('**14 portions observées · 26 % mangé.** Il s’agit d’un gratin avec béchamel. Sept élèves disent « pas aimé » ; quatre disent « pas le temps ».')
        st.info('A.B.C. estime 2,16 kg de restes évitables attribués à cet aliment. Le 3,09 kg CO₂e de la capture repose sur le chou-fleur cuit à 1,43 kg CO₂e/kg ; il ne décompose pas la béchamel du gratin.')
    st.write('**Chaque aliment a déjà mobilisé des ressources avant d’être jeté.** Pour chiffrer toute l’assiette, il faut compter la viande, les légumes, les sauces, les accompagnements, puis les quantités effectivement servies et jetées. La recette compte autant que le nom du plat.')
    st.success('Que changer au prochain service ? Une quantité selon la faim, la possibilité de goûter, une autre préparation ou davantage de temps pour manger : les observations aident à choisir.')
    with st.expander('Lire ces captures correctement'):
        st.write('Les pourcentages décrivent les portions scannées, pas l’ensemble des convives. Les kilos affichés sont les estimations attribuées aux aliments par A.B.C. ; ils ne sont pas chacun une pesée indépendante. Les petits effectifs et la couverture des scans limitent la représentativité. Les restes inévitables ne doivent pas être confondus avec les restes comestibles évitables.')
        st.markdown('[Ouvrir A.B.C. — Assiette Bas Carbone](https://thierryarmant.github.io/E3D-cantine/)')


def abc_chef(s):
    st.subheader('Le chef s’appuie sur les rejets A.B.C.')
    st.table([
        {'Aliment observé': 'Tomates', 'Rejet moyen dans les scans': '35 %', 'Motifs à examiner': '30 portions observées'},
        {'Aliment observé': 'Paupiette', 'Rejet moyen dans les scans': '33 %', 'Motifs à examiner': '7 « pas aimé » ; 6 « pas le temps » sur 30 portions'},
        {'Aliment observé': 'Chou-fleur en gratin', 'Rejet moyen dans les scans': '74 %', 'Motifs à examiner': '7 « pas aimé » ; 4 « pas le temps » sur 14 portions'},
        {'Aliment observé': 'Pommes noisettes', 'Rejet moyen dans les scans': '13 %', 'Motifs à examiner': '16 portions observées'},
        {'Aliment observé': 'Tiramisu', 'Rejet moyen dans les scans': '23 %', 'Motifs à examiner': '20 portions observées'},
        {'Aliment observé': 'Pain', 'Rejet moyen dans les scans': '40 %', 'Motifs à examiner': '35 portions observées sur deux jours'},
    ])
    st.write('Le chou-fleur a été moins mangé que les pommes noisettes dans cet échantillon. Pour demain, comparez les possibilités : changer la préparation, proposer de goûter, adapter les portions et garder du temps à table. Ne supprimez pas les légumes uniquement parce qu’ils sont moins appréciés.')
    st.caption('Ces chiffres viennent des scans A.B.C. du 1er octobre 2026 au collège J. Giono. Ils ne prouvent pas à eux seuls pourquoi un aliment a été laissé ; plusieurs causes peuvent se combiner.')
    if any(s.get(k) and s[k]['id'] == 'abc_cantine' for k in ('first', 'second')):
        st.info('Menu A.B.C. du jeu : prix fictif de 1 380 € pour 600 repas. Quantités hypothétiques : 72 kg de paupiettes préparées, 90 kg de gratin et 120 kg de pommes noisettes. Avec les taux de rejet observés, le scénario de portion unique prévoit environ 106 kg de restes. Les autres organisations simulent une réduction ; cette efficacité n’a pas été mesurée au collège.')

def purchase_posters():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader('Votre vitrine d’achat · Comparez prix et provenance')
    st.caption('Offres fictives pour 72 kg de viande, soit 600 portions de 120 g. Les accompagnements ne sont pas inclus dans ces prix. La commande totale est calculée avec les menus du chef.')
    offers = [
        ('cattle', '396 €', 'Brésil · Bœuf · 5,50 €/kg', 'Le prix le plus bas de ces trois offres', 'Une offre importée pour votre catalogue. Elle semble intéressante pour préserver le budget. Quelles autres informations vous manquent ?', 'Avant de retenir une offre : comparer coût, disponibilité et besoins.', 'Photo de bovins dans un pâturage britannique, illustrative ; elle ne montre pas ce fournisseur.'),
        ('chicken', '432 €', 'Poulet importé · 6 €/kg', 'Une autre viande dans le catalogue', 'Une offre importée de poulet, livrable à J+2 dans le scénario. Le prix est plus bas que celui du poulet régional à 576 €.', 'Comparer aussi les délais et la variété des deux repas.', 'Photo illustrative de poulets britanniques ; le pays fournisseur n’est pas précisé pour cette offre.'),
        ('pig', '504 €', 'Ventoux · Porc · 7 €/kg', 'Une offre proche', 'Une offre présentée comme locale dans le scénario. Elle coûte davantage que les deux offres précédentes. La proximité peut favoriser les liens avec les producteurs.', 'Un prix supérieur doit-il faire éliminer une offre ?', 'Photo illustrative d’un élevage britannique ; elle ne montre pas un élevage du Ventoux.'),
    ]
    for index, (column, args) in enumerate(zip(st.columns(3), offers), 1):
        key, price, origin, title, text, question, note = args
        with column:
            render_photo_card(index, key, price, origin, title, text, question, 'Catalogue A.B.C. · prix et provenances fictifs', None, note)
    st.caption('Autres propositions fermées : poulet régional, bœuf régional ou argentin, poisson et menu de lentilles. Les prix complets et les disponibilités figurent dans les choix. La provenance seule ne permet pas de conclure à une empreinte carbone supérieure ou inférieure.')

def purchase_reveal(s):
    st.subheader('Après l’achat · Le prix ne raconte pas toute l’histoire')
    actual = [s[k]['id'] for k in ('first', 'second') if s.get(k)]
    if actual:
        choice_footprint(s)
    else:
        st.caption('L’offre est publiée, mais les menus ne sont pas encore commandés. L’empreinte des aliments effectivement retenus apparaîtra lors de la confirmation de la livraison.')
    animal = next((m for m in actual if m in ('boeuf', 'boeuf_bresil', 'boeuf_argentine')), None)
    if animal in ('boeuf', 'boeuf_bresil', 'boeuf_argentine'):
        render_photo_card(1, 'cattle', '≈ 14 200 km', 'en voiture diesel : autant d’émissions que le bœuf pour 600 élèves', 'Un bœuf moins cher reste du bœuf', 'Le prix importé peut laisser davantage de budget dans notre scénario. Mais le repère climatique moyen du bœuf reste bien supérieur à celui du poulet : environ 14 200 km contre 2 300 km pour la même quantité de viande.', 'Votre marge de décision : varier les plats et demander des garanties au fournisseur.', 'ADEME · Agribalyse 3.2 / Impact CO₂', BEEF_URL, '72 kg de viande : bœuf 2 016 kg CO₂e ; poulet 328 kg. Trajet illustratif de 800 km à 142 g CO₂e/km. Moyennes génériques, pas des mesures du fournisseur ni une comparaison précise Brésil/France.')
    elif actual:
        carbon_comparison()
    st.write('**Un achat a plusieurs effets :** dépense immédiate, variété des repas, conditions de production, traçabilité, transport et émissions. Une offre proche n’est pas automatiquement moins carbonée qu’une autre viande importée.')

SCHOOL_NUTRITION_URL = 'https://www.legifrance.gouv.fr/loda/id/JORFTEXT000024614763'

def chef_nutrition(s):
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader('Chef · Nourrir, varier, respecter le cadre')
    st.markdown('''<section class="abc-carbon"><h3>Comprendre les proportions, sans calculer des grammes</h3>
<p>Exemple illustratif : sur 100 parts d’énergie dans une journée</p>
<div style="display:flex;border-radius:12px;overflow:hidden;min-height:50px;font:700 16px system-ui">
<div style="width:50%;background:#f4c45c;color:#183d34;padding:10px">50 % glucides</div>
<div style="width:35%;background:#85cbb4;color:#183d34;padding:10px">35 % lipides</div>
<div style="width:15%;background:#c8b0e5;color:#183d34;padding:10px">15 % protéines</div></div>
<div class="values" style="margin-top:12px"><div class="value">Glucides<br><small>Énergie pour bouger et réfléchir : riz, pommes de terre, pain…</small></div><div class="value">Lipides<br><small>Énergie, cellules : huiles, beurre, matières grasses des aliments…</small></div><div class="value">Protéines<br><small>Grandir et renouveler les tissus : lentilles, viande, poisson, produits laitiers…</small></div></div></section>''', unsafe_allow_html=True)
    st.caption('50/35/15 est une illustration de lecture des pourcentages, pas une obligation réglementaire par repas ni le calcul de vos menus. Ce sont des parts d’énergie, pas des parts du poids ou de la surface de l’assiette. Les besoins varient avec l’âge et l’activité ; les aliments apportent souvent plusieurs nutriments.')
    with st.expander('Les contraintes réelles du chef, expliquées simplement'):
        st.write('À la cantine, un déjeuner comprend un plat principal, une garniture, un produit laitier et une entrée et/ou un dessert. La variété est contrôlée sur 20 repas successifs : deux menus seuls ne permettent pas de déclarer un plan conforme.')
        st.write('Exemple sur 20 repas : 10 accompagnements avec des légumes cuits autres que les légumes secs, et 10 avec légumes secs, féculents ou céréales. Il existe aussi des fréquences pour les crudités, fruits et produits laitiers, ainsi que des limites concernant certaines préparations grasses ou sucrées.')
        st.caption('Les pourcentages de glucides, lipides et protéines ne remplacent pas ces règles. Pour connaître la répartition réelle d’un menu, il faut toutes ses recettes, ingrédients et portions ; ils ne sont pas tous renseignés dans le jeu.')
        st.markdown('[Règles de restauration scolaire — arrêté du 30 septembre 2011](' + SCHOOL_NUTRITION_URL + ') · [Repères 4–17 ans — Manger Bouger](' + NUTRITION_URL + ')')
    if not s.get('first') or not s.get('second'):
        return
    st.subheader('Votre analyse rapide des deux menus')
    first, second = s['first']['id'], s['second']['id']
    st.success('✓ Les plats proposés associent une source de protéines, des légumes et un accompagnement énergétique. Le scénario comprend aussi un produit laitier, une entrée et/ou un dessert, du pain et de l’eau dans la base fixe.')
    if first == second:
        st.warning('À améliorer : les deux plats sont identiques. Essayez une autre recette au deuxième repas pour varier goûts et aliments.')
    else:
        st.success('✓ Vous proposez deux plats différents.')
    if first in ('boeuf', 'boeuf_bresil', 'boeuf_argentine', 'abc_cantine') and second in ('boeuf', 'boeuf_bresil', 'boeuf_argentine', 'abc_cantine'):
        st.warning('À revoir : du bœuf aux deux repas. Varier les sources de protéines est utile ; le menu de lentilles est une autre possibilité. Ce signal n’est pas, à lui seul, une infraction à la réglementation.')
    if 'abc_cantine' in (first, second):
        st.warning('À vérifier dans la recette A.B.C. : béchamel, farce et préparation des pommes noisettes influencent les lipides. Leur nom seul ne permet pas de calculer une proportion fiable. Le chou-fleur très rejeté appelle aussi une adaptation de préparation ou de portion.')
    if 'vegetal' in (first, second) or 'secours' in (first, second):
        st.success('✓ Les lentilles apportent des protéines et des fibres. Le riz complète le plat ; ce choix permet de varier les sources de protéines.')
    total = s['first']['cost'] + s['second']['cost']
    if total > 3000:
        st.error(f'Budget dépassé de {total-3000:g} € : modifiez l’un des deux menus avant la commande.')
    else:
        st.success(f'✓ Budget respecté : {3000-total:g} € restent disponibles sur les deux repas.')
    st.caption('Analyse pédagogique du catalogue, pas un bilan nutritionnel calculé ni une certification de conformité. Les repas doivent être mangés pour que leurs apports profitent aux élèves.')

def menu_climate_cards():
    st.markdown(STYLE, unsafe_allow_html=True)
    st.subheader('Pause commune · Nos gestes dépassent le plateau')
    definitions = [
        ('waste', '8 à 10 %', 'des émissions mondiales de gaz à effet de serre sont liées aux pertes et au gaspillage alimentaires', 'Jeter un repas, c’est gaspiller sa fabrication', 'Cultiver, élever, transporter, conserver et cuisiner mobilise de l’énergie et émet des gaz à effet de serre. Si le repas est jeté, ces ressources n’ont pas servi à nourrir quelqu’un. Le CO₂ contribue au réchauffement ; le méthane de l’élevage et de certains déchets compte aussi.', 'Notre levier : prendre à sa faim et ajuster les achats.', 'PNUE · Food Waste Index 2024', UNEP_URL, 'Repère mondial, toutes pertes et gaspillage compris ; pas le pourcentage d’émissions du collège. Photo de biodéchets contenant aussi des parties non comestibles.'),
        ('water', '≈ 7 parts sur 10', 'des prélèvements mondiaux d’eau douce servent à l’agriculture', 'L’eau a travaillé avant notre repas', 'L’eau permet de produire les aliments. Jeter une nourriture comestible rend inutile une partie des ressources mobilisées pour elle. L’agriculture représente environ 72 % des prélèvements mondiaux d’eau douce, principalement pour irriguer.', 'Notre levier : éviter de produire et acheter des quantités qui seront jetées.', 'FAO · AQUASTAT et gestion de l’eau agricole', 'https://www.fao.org/land-water/water/agricultural-water-management/water-accounting/en', 'Prélèvements, pas consommation nette ni eau gaspillée. Ce repère ne dit pas combien de litres contient l’empreinte d’une assiette. Photo illustrative du Mékong.'),
        ('farm', '40 % du pain laissé', 'dans les portions scannées A.B.C. sur deux jours au collège J. Giono', 'Un morceau de pain a une histoire', 'Avant le pain : cultiver des céréales, récolter, moudre, transporter et cuire. Dans les 35 portions de pain observées par A.B.C., environ 60 % étaient mangés en moyenne. Chaque morceau évité dans la poubelle limite le gaspillage de cette chaîne.', 'Notre levier : prendre un morceau, puis se resservir si on a encore faim.', 'A.B.C. · observations du collège consultées le 14 octobre 2026', 'https://thierryarmant.github.io/E3D-cantine/', 'Échantillon de 35 portions sur deux jours, pas tous les convives. Photo illustrative d’une récolte de pommes de terre, pas de céréales. Les kilos et émissions attribués au pain par l’application sont des estimations.'),
    ]
    for index, (column, args) in enumerate(zip(st.columns(3), definitions), 1):
        with column:
            render_photo_card(index, *args)
    st.info('Produire inutilement ajoute des émissions et une pression sur les ressources. Cela contribue au problème climatique à grande échelle ; les restes de ce repas ne provoquent pas directement la sécheresse du jeu.')
    st.caption('Cartes A.B.C. originales : aucune reproduction des textes ou visuels de La Fresque du Climat.')
