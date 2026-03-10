"""
Illustrations SVG pour les 8 categories de badges.
Chaque illustration est un dessin simple en line-art,
stocke comme constante Python.
Les dessins sont dans un espace 100x100.
La couleur est appliquee par le moteur SVG.

SVG illustrations for the 8 badge categories.
Each is a simple line-art drawing stored as a Python constant.
Drawings use a 100x100 coordinate space.
Color is applied by the SVG engine.
"""


# ============================================================================
# Competence (Cp) — Ampoule / Lightbulb
# Represente la connaissance et la reflexion.
# Represents knowledge and thinking.
# ============================================================================

ILLUSTRATION_COMPETENCE = (
    '<path d="M50 8 C32 8 18 22 18 40 C18 54 28 62 34 70 L34 76 L66 76 '
    'L66 70 C72 62 82 54 82 40 C82 22 68 8 50 8 Z" '
    'fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<line x1="37" y1="82" x2="63" y2="82" '
    'fill="none" stroke-width="4" stroke-linecap="round"/>'
    '<line x1="40" y1="88" x2="60" y2="88" '
    'fill="none" stroke-width="4" stroke-linecap="round"/>'
    '<line x1="50" y1="44" x2="50" y2="64" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
    '<line x1="40" y1="54" x2="50" y2="64" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
    '<line x1="60" y1="54" x2="50" y2="64" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
)


# ============================================================================
# Savoir-faire (Sf) — Cle a molette / Wrench
# Represente le savoir-faire technique et manuel.
# Represents technical and manual know-how.
# ============================================================================

ILLUSTRATION_SAVOIR_FAIRE = (
    '<path d="M28 12 C20 12 14 18 14 26 C14 32 18 37 24 39 '
    'L42 57 L36 63 L24 63 L24 76 L36 76 L36 64 L44 56 '
    'L62 74 C64 76 68 76 70 74 L76 68 C78 66 78 62 76 60 '
    'L58 42 C64 40 68 35 68 28 C68 20 62 14 54 12 '
    'L48 22 L52 30 L44 34 L36 30 L40 22 Z" '
    'fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="54" cy="26" r="6" fill="none" stroke-width="3"/>'
)


# ============================================================================
# Savoir-etre (Se) — Personne avec coeur / Person with heart
# Represente les qualites humaines et relationnelles.
# Represents human and relational qualities.
# ============================================================================

ILLUSTRATION_SAVOIR_ETRE = (
    '<circle cx="50" cy="22" r="14" '
    'fill="none" stroke-width="4"/>'
    '<path d="M24 90 L24 62 C24 50 36 42 50 42 C64 42 76 50 76 62 L76 90" '
    'fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M50 58 L44 52 C40 48 44 42 50 48 C56 42 60 48 56 52 Z" '
    'fill="none" stroke-width="2.5" stroke-linejoin="round" opacity="0.6"/>'
)


# ============================================================================
# Savoir-vivre (Sv) — Poignee de main / Handshake
# Represente le vivre-ensemble et le respect mutuel.
# Represents living together and mutual respect.
# ============================================================================

ILLUSTRATION_SAVOIR_VIVRE = (
    '<path d="M10 45 L28 35 L40 45 L52 38 L62 45 L72 40 L90 50" '
    'fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M10 55 L28 50 L42 58 L28 65 Z" '
    'fill="none" stroke-width="3.5" stroke-linejoin="round"/>'
    '<path d="M90 55 L72 50 L58 58 L72 65 Z" '
    'fill="none" stroke-width="3.5" stroke-linejoin="round"/>'
    '<path d="M40 58 L50 52 L60 58 L50 64 Z" '
    'fill="none" stroke-width="2.5" stroke-linejoin="round" opacity="0.5"/>'
)


# ============================================================================
# Projet (Pj) — Fusee / Rocket
# Represente l'initiative et le lancement de projets.
# Represents initiative and project launching.
# ============================================================================

ILLUSTRATION_PROJET = (
    '<path d="M50 6 C50 6 36 24 36 52 L28 64 L36 64 L36 78 '
    'L44 78 L44 64 L56 64 L56 78 L64 78 L64 64 L72 64 '
    'L64 52 C64 24 50 6 50 6 Z" '
    'fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="50" cy="38" r="7" fill="none" stroke-width="3"/>'
    '<line x1="44" y1="86" x2="44" y2="94" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.4"/>'
    '<line x1="50" y1="88" x2="50" y2="94" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.5"/>'
    '<line x1="56" y1="86" x2="56" y2="94" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.4"/>'
)


# ============================================================================
# Participation (Pc) — Mains levees / Raised hands
# Represente la participation active et le volontariat.
# Represents active participation and volunteering.
# ============================================================================

ILLUSTRATION_PARTICIPATION = (
    '<path d="M30 90 L30 55 C30 48 22 48 22 55 L22 38 '
    'C22 31 14 31 14 38 L14 60 L14 45 C14 38 8 38 8 45 L8 68 '
    'C8 80 18 90 30 90 Z" '
    'fill="none" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M70 90 L70 55 C70 48 78 48 78 55 L78 38 '
    'C78 31 86 31 86 38 L86 60 L86 45 C86 38 92 38 92 45 L92 68 '
    'C92 80 82 90 70 90 Z" '
    'fill="none" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M38 30 L50 10 L62 30" '
    'fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.4"/>'
)


# ============================================================================
# Groupe (Gp) — Cercle de personnes / Circle of people
# Represente le travail en equipe et la communaute.
# Represents teamwork and community.
# ============================================================================

ILLUSTRATION_GROUPE = (
    '<circle cx="50" cy="18" r="10" fill="none" stroke-width="3.5"/>'
    '<path d="M34 58 L34 44 C34 36 42 30 50 30 C58 30 66 36 66 44 L66 58" '
    'fill="none" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="20" cy="42" r="8" fill="none" stroke-width="3" opacity="0.65"/>'
    '<path d="M8 72 L8 62 C8 55 14 50 20 50 C26 50 30 53 32 58" '
    'fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.65"/>'
    '<circle cx="80" cy="42" r="8" fill="none" stroke-width="3" opacity="0.65"/>'
    '<path d="M92 72 L92 62 C92 55 86 50 80 50 C74 50 70 53 68 58" '
    'fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" opacity="0.65"/>'
    '<path d="M30 80 C30 70 38 64 50 64 C62 64 70 70 70 80" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.4"/>'
)


# ============================================================================
# Experience (Xp) — Sommet avec drapeau / Mountain peak with flag
# Represente l'experience acquise et les defis releves.
# Represents acquired experience and challenges overcome.
# ============================================================================

ILLUSTRATION_EXPERIENCE = (
    '<path d="M50 10 L82 82 L68 82 L56 58 L50 68 L44 58 L32 82 L18 82 Z" '
    'fill="none" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    '<line x1="50" y1="10" x2="50" y2="4" '
    'fill="none" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M50 4 L66 12 L50 18" '
    'fill="none" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    '<line x1="10" y1="90" x2="90" y2="90" '
    'fill="none" stroke-width="3" stroke-linecap="round" opacity="0.3"/>'
)


# ============================================================================
# Dictionnaire d'acces rapide par abbreviation de categorie.
# Quick-access dictionary by category abbreviation.
# ============================================================================

ILLUSTRATIONS_BY_ABBREVIATION = {
    "Cp": ILLUSTRATION_COMPETENCE,
    "Sf": ILLUSTRATION_SAVOIR_FAIRE,
    "Se": ILLUSTRATION_SAVOIR_ETRE,
    "Sv": ILLUSTRATION_SAVOIR_VIVRE,
    "Pj": ILLUSTRATION_PROJET,
    "Pc": ILLUSTRATION_PARTICIPATION,
    "Gp": ILLUSTRATION_GROUPE,
    "Xp": ILLUSTRATION_EXPERIENCE,
}
