"""Cartes A.B.C. originales : photographies sous licence et données sourcées."""
from pathlib import Path
from functools import lru_cache
import base64
import html
import json
import streamlit as st

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
.abc-photo-card{border-radius:22px;overflow:hidden;background:#fff;border:1px solid #dce5d9;box-shadow:0 12px 32px rgba(20,57,43,.09);margin:0 0 24px;color:#183d34}
.abc-photo-card .visual{height:225px;position:relative;overflow:hidden;background:#d9e6d8}
.abc-photo-card img{width:100%;height:100%;object-fit:cover;display:block}
.abc-photo-card .visual:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,transparent 35%,rgba(14,35,26,.6))}
.abc-photo-card .tag{position:absolute;top:16px;left:16px;background:#fff3dc;color:#674923;border-radius:30px;font:700 12px system-ui;padding:8px 12px;z-index:1}
.abc-photo-card .body{padding:24px 25px 22px}
.abc-photo-card .figure{font:800 clamp(32px,4vw,46px) system-ui;color:#245b48;line-height:1.05;margin:0 0 9px}
.abc-photo-card .unit{font:600 14px system-ui;color:#547466;margin:0 0 19px;line-height:1.5}
.abc-photo-card h3{font:700 23px system-ui;line-height:1.2;margin:0 0 12px}
.abc-photo-card p{font:16px/1.6 system-ui;margin:0 0 15px}
.abc-photo-card .action{background:#edf5e9;border-left:4px solid #568f58;padding:12px 14px;border-radius:8px;font:600 14px/1.5 system-ui}
.abc-photo-card .source{font:12px/1.6 system-ui;color:#607268;margin-top:16px}
.abc-photo-card a{color:#356a57;text-decoration:underline}
.abc-carbon{background:#173e34;color:#fff;border-radius:20px;padding:24px;margin:0 0 20px}
.abc-carbon h3{color:#fff;margin:0 0 12px;font:700 22px system-ui}
.abc-carbon .values{display:flex;gap:14px;flex-wrap:wrap}
.abc-carbon .value{flex:1;min-width:125px;background:#ffffff12;border-radius:12px;padding:16px}
.abc-carbon strong{font:800 32px system-ui;display:block;color:#f2d392}
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
<div class="source">{source}<br>{e(note)}<br><a href="{e(credits['source'],quote=True)}" target="_blank">{e(attribution)}</a></div></div></article>''', unsafe_allow_html=True)


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
        ('cattle', '2 tonnes contre 330 kg', 'de CO₂e pour 600 portions de 120 g : bœuf contre poulet', 'Les mêmes 600 élèves, un impact très différent', 'Pour la viande seule, 600 portions de bœuf représentent environ 2 tonnes CO₂e ; les mêmes portions de poulet environ 330 kg CO₂e. À poids égal, une portion de bœuf correspond donc à peu près aux émissions de six portions de poulet.', 'Votre levier : varier les protéines et comparer les fournisseurs.', 'ADEME · Impact CO₂ · Agribalyse 3.2', BEEF_URL, 'Calcul : 600 × 0,120 kg × 28 = 2 016 kg CO₂e ; avec le poulet, × 4,56 = 328 kg CO₂e. Valeurs arrondies, viande seule. Estimation à partir de moyennes ; aucune mesure du fournisseur fictif.'),
        ('industry', '+1,1 °C', 'température mondiale moyenne en 2011–2020 par rapport à 1850–1900', 'Une hausse moyenne qui change les conditions', 'Les activités humaines ont renforcé l’effet de serre et réchauffé le climat. Les émissions de l’alimentation s’ajoutent à celles des autres activités. Ce chiffre du GIEC porte sur une période précise.', 'Votre levier : réduire les émissions évitables, notamment le gaspillage.', 'GIEC · Rapport de synthèse 2023', IPCC_URL, 'Ce n’est pas la température actuelle d’une journée. Photo d’une centrale à Rostock ; un panache visible ne mesure pas le CO₂.'),
        ('water', 'L’eau circule', 'évaporation → nuages → précipitations → sols et cours d’eau', 'Le réchauffement modifie le cycle de l’eau', 'Un climat plus chaud modifie l’évaporation et les précipitations. Les changements dépendent des régions : certains lieux risquent davantage de manquer d’eau, d’autres de subir des pluies intenses.', 'Votre levier : anticiper les risques et garder des alternatives.', 'GIEC · Eau, impacts et adaptation', WATER_URL, 'Photo illustrative du Mékong, au Laos ; elle ne représente pas la sécheresse fictive du jeu.'),
        ('drought', '−50 %', 'de carottes disponibles au jour 2 dans la simulation', 'La sécheresse atteint votre prochain menu', 'Dans le jeu, l’offre de carottes passe de 90 à 45 kg. Le courtier doit trouver un complément et le chef peut changer sa recette. Les quantités et les surcoûts du jeu sont fictifs.', 'Votre levier : revoir ensemble menu, portions et approvisionnement.', 'Scénario A.B.C. · hypothèse pédagogique', None, 'Photo réelle de sol sec à Chowilla, en Australie ; ce n’est pas la ferme fictive du jeu.'),
    ]
    for offset in range(0, len(definitions), 2):
        for column, args in zip(st.columns(2), definitions[offset:offset+2]):
            with column:
                render_photo_card(offset + list(definitions[offset:offset+2]).index(args) + 1, *args)
    st.info(f'Votre jour 1 : {day1["waste"]} kg de restes comestibles simulés. Le chiffre du jeu et les chiffres mondiaux ci-dessus ne décrivent pas la même échelle.')
    if menus and sum(m in ('boeuf', 'boeuf_bresil', 'boeuf_argentine') for m in menus) == 2:
        st.warning('Votre prévision contenait du bœuf aux deux repas. Une offre moins chère peut résoudre le budget sans supprimer les émissions liées à l’élevage. Vous pouvez varier le jour 2.')
    carbon_comparison()
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
