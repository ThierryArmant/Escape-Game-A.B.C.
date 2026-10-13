"""Cartes illustrées pour la pause commune après le premier service."""
import streamlit as st

NUTRITION_URL = 'https://www.mangerbouger.fr/manger-mieux/a-tout-age-et-a-chaque-etape-de-la-vie/enfants-et-adolescents-de-4-a-17-ans/les-recommandations-alimentaires-pour-les-4-17-ans'

def svg(content, background='#ecf3e7'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="240" viewBox="0 0 480 240"><rect width="480" height="240" rx="24" fill="{background}"/>{content}</svg>'

CARDS = [
    ('1 · Un repas a une histoire', svg('<path d="M0 185 Q120 135 240 185 T480 185 V240 H0Z" fill="#729b52"/><path d="M45 175V95M110 175V80M175 175V95" stroke="#3d703c" stroke-width="9"/><path d="M45 135q-35-40-30-40q45 5 30 40M110 120q35-40 40-35q-5 40-40 35M175 145q-30-35-30-40q40 0 30 40" fill="#65a647"/><rect x="265" y="115" width="110" height="60" rx="10" fill="#d9a455"/><rect x="375" y="135" width="55" height="40" rx="8" fill="#bf8741"/><circle cx="295" cy="180" r="20" fill="#29463d"/><circle cx="400" cy="180" r="20" fill="#29463d"/><path d="M255 100q-25-30 0-65q25 35 0 65" fill="#60aabd"/>'), 'Pour remplir un plateau, il a fallu cultiver, élever, transporter, conserver et cuisiner. Cela utilise de l’eau et de l’énergie, et produit des gaz à effet de serre.'),
    ('2 · Jeter, c’est perdre aussi ces ressources', svg('<ellipse cx="160" cy="115" rx="100" ry="70" fill="#fff" stroke="#9fbaaa" stroke-width="8"/><ellipse cx="160" cy="115" rx="65" ry="42" fill="#f1dbb1"/><circle cx="145" cy="110" r="20" fill="#d48e49"/><circle cx="183" cy="125" r="17" fill="#6d9b4a"/><path d="M275 85H410L398 200H286Z" fill="#789084"/><path d="M265 80H420M300 60H385" stroke="#355c4c" stroke-width="12" stroke-linecap="round"/><path d="M225 140l50 25-20 10" fill="none" stroke="#c9754e" stroke-width="8"/>'), 'Si la nourriture finit à la poubelle, les ressources utilisées pour la produire ont été dépensées sans nourrir personne. Certains traitements des déchets peuvent aussi émettre des gaz. Prendre selon sa faim et ajuster les achats évite de produire inutilement.'),
    ('3 · La viande a des impacts différents', svg('<rect x="70" y="105" width="165" height="70" rx="24" fill="#fff" stroke="#456b58" stroke-width="6"/><rect x="205" y="75" width="70" height="65" rx="20" fill="#fff" stroke="#456b58" stroke-width="6"/><path d="M220 80l-10-25M255 80l15-25M95 165v45M195 165v45" stroke="#456b58" stroke-width="8"/><ellipse cx="130" cy="125" rx="24" ry="18" fill="#456b58"/><circle cx="250" cy="98" r="5" fill="#456b58"/><path d="M295 65q0-35 35-30q25-35 50-10q50-5 45 35q30 30-15 40H315q-45-5-20-35" fill="#c3d5d0"/><path d="M325 145h60M335 170h40" stroke="#c2804d" stroke-width="7" stroke-linecap="round"/>'), 'L’élevage mobilise des terres, de l’alimentation animale et de l’énergie. Les ruminants, comme les bovins, émettent aussi du méthane pendant leur digestion. Toutes les viandes n’ont pas le même impact : varier avec des légumes secs et limiter les excès peut réduire la pression sur le climat.'),
    ('4 · Un climat plus chaud fragilise les récoltes', svg('<circle cx="370" cy="65" r="40" fill="#e5b653"/><path d="M315 65H290M425 65H450M370 10V0M330 25L310 5M410 25L430 5" stroke="#e5b653" stroke-width="7"/><path d="M0 170Q140 135 280 170T480 170V240H0Z" fill="#c79562"/><path d="M80 190l20 20-15 25M235 180l-20 20 25 20-10 20M380 185l25 20-15 35" fill="none" stroke="#805f43" stroke-width="6"/><path d="M145 165V95M145 130q-35-15-40-40q35 0 40 40M145 145q35-15 40-40q-35 0-40 40" stroke="#8b9460" stroke-width="8" fill="none"/>', '#fbefda'), 'Les gaz à effet de serre renforcent le réchauffement. Celui-ci modifie le cycle de l’eau et peut augmenter le risque de sécheresse dans certaines régions. Des sols plus secs et un manque d’eau peuvent réduire les récoltes : moins de produits disponibles, des remplacements et des prix qui changent.'),
]

# Cartes originales A.B.C. : une chaîne de mécanismes, avec textes et illustrations propres au jeu.
CARDS = CARDS[:3] + [
    ('4 · Plus de gaz, plus de chaleur retenue', svg('<circle cx="240" cy="130" r="67" fill="#80b2be"/><path d="M210 80l-25 40 35 15 5 40 35-20 5-35 35-10-40-30Z" fill="#76a365"/><ellipse cx="240" cy="130" rx="100" ry="95" fill="none" stroke="#b0c6d4" stroke-width="12"/><circle cx="70" cy="45" r="25" fill="#e5b653"/><path d="M90 60l80 55M180 150l-55 35M295 140l55-30-5 55-35-5" fill="none" stroke="#d38357" stroke-width="9"/>'), 'L’effet de serre naturel garde la Terre habitable. Les gaz ajoutés par les activités humaines retiennent davantage de chaleur : le climat se réchauffe. Nos choix alimentaires font partie des activités qui émettent ces gaz.'),
    ('5 · Le cycle de l’eau se modifie', svg('<path d="M0 180Q100 150 200 185T480 180V240H0Z" fill="#6ba3be"/><path d="M45 175L130 60l90 120Z" fill="#9db3a0"/><path d="M104 95l26-35 28 35Z" fill="#f9fcfa"/><path d="M270 95q-10-45 40-40q25-35 50-10q50-5 45 35q25 25-20 30H290Z" fill="#c4d5dd"/><path d="M250 170V120l-12 15M250 120l12 15" fill="none" stroke="#d69259" stroke-width="8"/><path d="M320 120l-8 25M360 120l-8 25M400 120l-8 25" stroke="#6ba3be" stroke-width="7"/>'), 'L’eau s’évapore, forme des nuages et retombe en précipitations. Avec le réchauffement, l’évaporation et les pluies changent. Selon les régions et les saisons, le risque de sécheresse ou de pluies intenses peut augmenter.'),
    ('6 · Récoltes fragilisées, menus à adapter', CARDS[3][1], 'Moins d’eau disponible peut réduire les récoltes. Le fournisseur a moins de produits ; le courtier cherche des alternatives ; le chef adapte le menu et le budget. Votre mission est de nourrir les élèves tout en limitant les pertes.'),
]

def climate_pause(day1, is_master, resume, menus=None):
    st.subheader('Pause commune · Du plateau au climat')
    st.info(f'Au jour 1, vos choix ont laissé {day1["waste"]} kg de restes comestibles. Prenons un moment pour comprendre pourquoi cela compte aussi pour la planète.')
    if menus and sum(m in ('boeuf', 'boeuf_bresil', 'boeuf_argentine') for m in menus) == 2:
        st.warning('Votre prévision contenait du bœuf aux deux repas. Ce choix sollicite davantage une filière d’élevage de ruminants ; une offre moins chère ne supprime pas cet enjeu. Vous pouvez essayer une autre composition pour le jour 2.')
    st.write('**Reliez les cartes :** repas et ressources → émissions → chaleur retenue → cycle de l’eau modifié → récoltes fragilisées → adaptations à la cantine.')
    for offset in range(0, len(CARDS), 2):
        columns = st.columns(2)
        for column, (title, image, text) in zip(columns, CARDS[offset:offset+2]):
            with column:
                with st.container(border=True):
                    st.image(image, width='stretch')
                    st.subheader(title)
                    st.write(text)
    st.warning('Dans le jeu, une sécheresse frappe les fournisseurs du jour 2. C’est une mise en situation : les déchets de votre premier repas n’ont pas causé à eux seuls cette sécheresse. Les émissions et les risques climatiques s’accumulent à grande échelle et sur une longue durée.')
    st.write('**Votre mission suivante :** nourrir tout le monde, varier les menus, ajuster les portions et adapter les approvisionnements aux récoltes disponibles.')
    st.caption('Cartes originales A.B.C., inspirées de la pédagogie des liens de cause à conséquence. Elles ne sont pas les cartes officielles de La Fresque du Climat.')
    with st.expander('Sources pour approfondir'):
        st.markdown('[La Fresque du Climat — démarche collaborative](https://fresqueduclimat.org/projet/) · [PNUE — pertes, gaspillage et émissions](https://www.unep.org/news-and-stories/press-release/world-squanders-over-1-billion-meals-day-un-report) · [GIEC — alimentation et élevage](https://www.ipcc.ch/srccl/chapter/chapter-5/) · [GIEC — eau et sécheresses](https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-4/)')
    if is_master:
        if st.button('Reprendre la mission : adapter le jour 2', type='primary'):
            resume()
    else:
        st.info('Lisez les cartes avec votre équipe. Le maître reprendra la mission après ce temps commun.')

def menu_consequences(s):
    if not s['first'] or not s['second']:
        return
    total = s['first']['cost'] + s['second']['cost']
    beef_count = sum(m['id'] in ('boeuf', 'boeuf_bresil', 'boeuf_argentine') for m in (s['first'], s['second']))
    if total <= 3000 and beef_count < 2:
        return
    with st.container(border=True):
        st.subheader('Votre menu a des conséquences')
        st.image(svg('<circle cx="240" cy="120" r="100" fill="#fff" stroke="#94b6a4" stroke-width="8"/><path d="M240 35A85 85 0 0 0 240 205Z" fill="#83ae69"/><path d="M240 35A85 85 0 0 1 325 120H240Z" fill="#edcf80"/><path d="M240 120H325A85 85 0 0 1 240 205Z" fill="#cb906a"/><circle cx="208" cy="95" r="15" fill="#508545"/><circle cx="180" cy="130" r="18" fill="#508545"/><circle cx="208" cy="161" r="14" fill="#508545"/>'), width='stretch')
        st.caption('Illustration de variété des aliments ; proportions décoratives, pas une prescription de portions.')
        if total > 3000:
            st.error(f'Budget : {total:g} € prévus pour 3 000 € disponibles. Il manque {total - 3000:g} €. Les commandes restent en attente : changez un menu ou comparez une autre offre.')
        if beef_count == 2:
            st.warning('Deux repas au bœuf : vos menus sont peu variés. Ce n’est pas un diagnostic de santé pour un repas ; l’équilibre se construit sur plusieurs repas et sur la semaine.')
            st.write('**Pour la santé :** varier les aliments aide à diversifier les apports. La viande n’est pas nécessaire à chaque repas. Les légumes secs, comme les lentilles, apportent des protéines végétales et des fibres ; gardez aussi des légumes, des féculents et des fruits dans les repas.')
            st.write('**Pour le climat :** le bœuf provient de ruminants qui émettent du méthane. Une offre importée moins chère peut aider le budget, mais ne supprime pas ces émissions.')
            st.markdown('[Repères pour les enfants et adolescents — Manger Bouger](' + NUTRITION_URL + ')')


def sourcing_card():
    with st.container(border=True):
        st.subheader('Prix bas : et l’empreinte carbone ?')
        st.table([
            {'Offre': 'Bœuf brésilien ou argentin', 'À regarder': 'Élevage de ruminants : méthane, alimentation, usage des terres, puis transport.', 'Point clé': 'Le pays seul ne permet pas de calculer l’empreinte. Les pratiques du fournisseur comptent.'},
            {'Offre': 'Bœuf régional', 'À regarder': 'Le transport peut être plus court, mais l’élevage produit aussi des émissions.', 'Point clé': 'Local ne signifie pas automatiquement faible carbone.'},
            {'Offre': 'Porc du Ventoux', 'À regarder': 'Alimentation animale, effluents, énergie et transport.', 'Point clé': 'En moyenne, le porc a généralement une empreinte plus faible que le bœuf ; la ferme et le produit précis comptent.'},
            {'Offre': 'Poisson', 'À regarder': 'Espèce, pêche ou élevage, carburant, alimentation, conservation.', 'Point clé': 'Empreinte très variable : poisson n’est pas synonyme de faible carbone.'},
            {'Offre': 'Lentilles', 'À regarder': 'Culture, transformation, transport et cuisson.', 'Point clé': 'Une alternative végétale pour varier les protéines et réduire la pression climatique du menu.'},
        ])
        st.write('Le courtier compare **prix, quantité, délai et mode de production**. Une offre moins chère peut aider le budget, mais son prix n’indique pas son impact climatique.')
        st.caption('Prix fictifs du jeu. Aucun chiffre de CO₂ n’est attribué à un pays ou fournisseur sans données sur le produit réel.')
        st.markdown('[GIEC — systèmes alimentaires, élevage et émissions](https://www.ipcc.ch/srccl/chapter/chapter-5/)')
