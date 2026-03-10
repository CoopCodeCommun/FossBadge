"""
Moteur de generation SVG pour les badges — qualite Le Dome.
Produit des badges multi-couches avec :
  - Ombre portee subtile (profondeur)
  - Bordure glow epaisse semi-transparente (halo)
  - Fond blanc de base
  - Aplat de couleur dans la partie haute (fond_categorie)
  - Bordure principale nette (contour visible)
  - Filet interieur decoratif
  - Texte courbe (categorie en haut, posture en bas)
  - Illustration au centre
  - Titre blanc sur fond colore
  - Sous-titre sombre en dessous

SVG generation engine for Le Dome quality badges.
Multi-layered badges with drop shadow, glow border, colored inner fill,
crisp outline, decorative inner ring, curved text, centered illustration.

LOCALISATION : badge_generator/svg_engine.py
"""

import math

from badge_generator.shapes import ALL_SHAPES, DEFAULT_SHAPE_KEY


# ============================================================================
# Constantes du badge.
# Badge constants.
# ============================================================================

# Taille du badge en pixels.
# Badge size in pixels.
BADGE_SIZE = 500

# Centre du badge.
# Badge center.
CENTER_X = BADGE_SIZE / 2
CENTER_Y = BADGE_SIZE / 2

# --- Bordures multi-couches ---
# Multi-layer border constants.

# Couche 1 : Ombre portee (drop shadow).
# Layer 1: Drop shadow.
SHADOW_BLUR = 8
SHADOW_OPACITY = 0.10

# Couche 2 : Glow exterieur (halo epais semi-transparent).
# Layer 2: Outer glow (thick semi-transparent halo).
GLOW_STROKE_WIDTH = 22
GLOW_OPACITY = 0.18

# Couche 3 : Filet interieur decoratif (mince, discret).
# Layer 3: Inner decorative ring (thin, subtle).
INNER_RING_STROKE_WIDTH = 1.5
INNER_RING_OPACITY = 0.25

# --- Aplat de couleur (fond_categorie) ---
# Colored inner fill constants.
# La couleur de la categorie remplit la partie haute du badge.
# Le Y de coupure definit ou la couleur s'arrete.
# Category color fills the upper part of the badge.
# The cutoff Y defines where the color stops.
COLOR_FILL_CUTOFF_Y = 310

# --- Texte et couleurs ---
# Text and color constants.

# Couleur par defaut du texte fonce (titre, posture).
# Default dark text color.
DEFAULT_TEXT_COLOR = "#473467"

# Couleur par defaut de la bordure.
# Default border color.
DEFAULT_BORDER_COLOR = "#009eb9"

# Rayon de l'arc pour le texte courbe en haut.
# On utilise un rayon plus petit pour que le texte reste bien a l'interieur
# de toutes les formes, y compris les formes Dome plus petites (CP, SE, XP).
# Arc radius for curved text at top.
# Smaller radius keeps text inside all shapes including smaller Dome ones.
TEXT_ARC_TOP_RADIUS = 130

# Rayon de l'arc pour le texte courbe en bas.
# Encore plus petit pour les formes aplaties comme XP (bas a Y~383).
# Arc radius for curved text at bottom.
# Even smaller to fit flat shapes like XP (bottom at Y~383).
TEXT_ARC_BOTTOM_RADIUS = 115

# Police de caracteres pour les textes.
# Font family for text.
FONT_FAMILY = "Montserrat, Arial, Helvetica, sans-serif"


# ============================================================================
# Construction des arcs pour le texte courbe.
# Build arc paths for curved text.
# ============================================================================

def _build_text_arc_top():
    """
    On fabrique un arc SVG pour le texte courbe en haut du badge.
    Le texte de la categorie suit cet arc.
    On utilise un arc plus resserre (225-315 degres au lieu de 220-320)
    pour que le texte ne depasse pas des formes Dome plus petites.

    Build SVG arc for curved text at the top of the badge.
    Tighter arc (225-315° instead of 220-320°) to keep text inside
    smaller Dome shapes.
    """
    angle_start_degrees = 225
    angle_end_degrees = 315

    angle_start_radians = math.radians(angle_start_degrees)
    angle_end_radians = math.radians(angle_end_degrees)

    start_x = CENTER_X + TEXT_ARC_TOP_RADIUS * math.cos(angle_start_radians)
    start_y = CENTER_Y + TEXT_ARC_TOP_RADIUS * math.sin(angle_start_radians)

    end_x = CENTER_X + TEXT_ARC_TOP_RADIUS * math.cos(angle_end_radians)
    end_y = CENTER_Y + TEXT_ARC_TOP_RADIUS * math.sin(angle_end_radians)

    return (
        f"M{start_x:.1f} {start_y:.1f} "
        f"A{TEXT_ARC_TOP_RADIUS} {TEXT_ARC_TOP_RADIUS} 0 0 1 {end_x:.1f} {end_y:.1f}"
    )


def _build_text_arc_bottom():
    """
    On fabrique un arc SVG pour le texte courbe en bas du badge.
    Le texte de posture ("JE DECOUVRE" etc.) suit cet arc.
    On utilise un rayon plus petit pour rester a l'interieur
    des formes aplaties comme XP.

    Build SVG arc for curved text at the bottom of the badge.
    Smaller radius to stay inside flat shapes like XP.
    """
    angle_start_degrees = 140
    angle_end_degrees = 40

    angle_start_radians = math.radians(angle_start_degrees)
    angle_end_radians = math.radians(angle_end_degrees)

    start_x = CENTER_X + TEXT_ARC_BOTTOM_RADIUS * math.cos(angle_start_radians)
    start_y = CENTER_Y + TEXT_ARC_BOTTOM_RADIUS * math.sin(angle_start_radians)

    end_x = CENTER_X + TEXT_ARC_BOTTOM_RADIUS * math.cos(angle_end_radians)
    end_y = CENTER_Y + TEXT_ARC_BOTTOM_RADIUS * math.sin(angle_end_radians)

    return (
        f"M{start_x:.1f} {start_y:.1f} "
        f"A{TEXT_ARC_BOTTOM_RADIUS} {TEXT_ARC_BOTTOM_RADIUS} 0 0 0 {end_x:.1f} {end_y:.1f}"
    )


# Arcs pre-calcules.
# Pre-computed arcs.
TEXT_ARC_TOP_PATH = _build_text_arc_top()
TEXT_ARC_BOTTOM_PATH = _build_text_arc_bottom()


# ============================================================================
# Fonction utilitaire : eclaircir une couleur.
# On melange la couleur avec du blanc pour obtenir une teinte plus claire.
# Utilisee pour le filet interieur decoratif.
#
# Utility: lighten a color by mixing with white.
# Used for the inner decorative ring.
# ============================================================================

def _lighten_color(hex_color, factor=0.45):
    """
    On eclaircit une couleur hex en la melangeant avec du blanc.
    factor=0 : couleur originale. factor=1 : blanc pur.

    Lighten a hex color by mixing with white.
    factor=0: original. factor=1: pure white.
    """
    hex_color = hex_color.lstrip('#')

    # On extrait les composantes rouge, vert, bleu.
    # Extract red, green, blue components.
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    # On melange chaque composante avec 255 (blanc).
    # Mix each component towards 255 (white).
    red = int(red + (255 - red) * factor)
    green = int(green + (255 - green) * factor)
    blue = int(blue + (255 - blue) * factor)

    return f'#{red:02x}{green:02x}{blue:02x}'


# ============================================================================
# Fonction principale : generer le SVG complet du badge.
# Main function: generate the complete badge SVG.
# ============================================================================

def generate_badge_svg(
    category_name="",
    category_color=DEFAULT_BORDER_COLOR,
    level_stroke_width=3,
    level_posture_text="",
    illustration_svg="",
    title="Badge",
    subtitle="",
    shape_key="",
):
    """
    On fabrique le code SVG complet du badge, qualite Le Dome.
    Le badge utilise des couches superposees pour un rendu riche :
    ombre, halo, fond blanc, aplat de couleur, bordure nette, textes.

    Build complete Le Dome quality badge SVG code.
    Multi-layered: shadow, glow, white fill, colored area, crisp border, text.

    LOCALISATION : badge_generator/svg_engine.py
    """

    # --- Choix de la forme ---
    # Shape selection.
    if not shape_key or shape_key not in ALL_SHAPES:
        shape_key = DEFAULT_SHAPE_KEY

    chosen_shape_path = ALL_SHAPES[shape_key]["path"]

    # --- Couleur eclaircie pour le filet interieur ---
    # Lighter shade for inner decorative ring.
    light_category_color = _lighten_color(category_color, factor=0.45)

    # --- Texte alternatif pour l'accessibilite ---
    # Alt text for accessibility.
    badge_description = _escape_svg_text(title)
    if subtitle:
        badge_description += f" — {_escape_svg_text(subtitle)}"
    if category_name:
        badge_description += f". {_escape_svg_text(category_name)}"

    # ==================================================================
    # COUCHE 1 : Ombre portee.
    # On dessine la forme en gris clair avec un filtre de flou.
    # Ca donne l'impression que le badge flotte au-dessus de la page.
    #
    # LAYER 1: Drop shadow.
    # Shape drawn in light gray with blur filter.
    # Makes the badge appear to float above the page.
    # ==================================================================
    shadow_layer = (
        f'<path d="{chosen_shape_path}" '
        f'fill="#b0b0b0" '
        f'stroke="none" '
        f'filter="url(#drop-shadow)" '
        f'opacity="{SHADOW_OPACITY}"/>'
    )

    # ==================================================================
    # COUCHE 2 : Halo exterieur (glow).
    # Trait epais et semi-transparent autour de la forme.
    # Cree un halo lumineux, comme dans les badges du Dome.
    #
    # LAYER 2: Outer glow.
    # Thick semi-transparent stroke around the shape.
    # Creates a luminous halo like in Dome badges.
    # ==================================================================
    glow_layer = (
        f'<path d="{chosen_shape_path}" '
        f'fill="none" '
        f'stroke="{category_color}" '
        f'stroke-width="{GLOW_STROKE_WIDTH}" '
        f'stroke-linejoin="round" '
        f'opacity="{GLOW_OPACITY}"/>'
    )

    # ==================================================================
    # COUCHE 3 : Fond blanc.
    # On remplit toute la forme en blanc.
    # C'est la base sur laquelle on pose la couleur et les textes.
    #
    # LAYER 3: White base fill.
    # Fill entire shape white. Base for color and text layers.
    # ==================================================================
    white_fill_layer = (
        f'<path d="{chosen_shape_path}" '
        f'fill="#ffffff" '
        f'stroke="none"/>'
    )

    # ==================================================================
    # COUCHE 4 : Aplat de couleur (fond_categorie).
    # C'est LA couche qui donne leur caractere aux badges du Dome.
    # On remplit la partie haute du badge avec la couleur de la categorie.
    # On utilise un clipPath (la forme du badge) pour que la couleur
    # ne deborde pas hors de la forme.
    # Le rectangle de couleur s'arrete a COLOR_FILL_CUTOFF_Y (310px),
    # laissant la partie basse en blanc pour le sous-titre et la posture.
    #
    # LAYER 4: Colored inner fill (fond_categorie).
    # THE layer that gives Dome badges their character.
    # Upper portion filled with category color via clipPath.
    # Rectangle stops at COLOR_FILL_CUTOFF_Y (310px),
    # leaving bottom white for subtitle and posture text.
    # ==================================================================
    colored_fill_layer = (
        f'<g clip-path="url(#badge-clip)">'
        f'<rect x="0" y="0" width="{BADGE_SIZE}" height="{COLOR_FILL_CUTOFF_Y}" '
        f'fill="{category_color}"/>'
        f'</g>'
    )

    # ==================================================================
    # COUCHE 5 : Filet interieur decoratif.
    # Un trait fin et clair a l'interieur de la forme.
    # Ca ajoute de la finesse et de la profondeur visuelle.
    #
    # LAYER 5: Inner decorative ring.
    # Thin light stroke inside the shape.
    # Adds visual finesse and depth.
    # ==================================================================
    inner_ring_layer = (
        f'<path d="{chosen_shape_path}" '
        f'fill="none" '
        f'stroke="{light_category_color}" '
        f'stroke-width="{INNER_RING_STROKE_WIDTH}" '
        f'opacity="{INNER_RING_OPACITY}"/>'
    )

    # ==================================================================
    # COUCHE 6 : Bordure principale (contour net).
    # Le trait visible et net qui definit le bord du badge.
    # Son epaisseur change selon le niveau du badge.
    #
    # LAYER 6: Main crisp border.
    # Clean visible stroke that defines the badge edge.
    # Thickness varies by badge level.
    # ==================================================================
    main_border_layer = (
        f'<path d="{chosen_shape_path}" '
        f'fill="none" '
        f'stroke="{category_color}" '
        f'stroke-width="{level_stroke_width}" '
        f'stroke-linejoin="round"/>'
    )

    # ==================================================================
    # COUCHE 7 : Texte courbe en haut — nom de la categorie.
    # Ecrit en BLANC sur le fond colore, en majuscules.
    # Le texte suit un arc de cercle.
    #
    # LAYER 7: Curved text at top — category name.
    # Written in WHITE over the colored fill, in uppercase.
    # ==================================================================
    category_text_section = ""
    if category_name:
        escaped_category_name = _escape_svg_text(category_name.upper())
        category_text_section = (
            f'<text fill="#ffffff" '
            f'font-family="{FONT_FAMILY}" '
            f'font-size="18" '
            f'font-weight="700" '
            f'letter-spacing="0.15em" '
            f'opacity="0.92">'
            f'<textPath href="#arc-top" startOffset="50%" text-anchor="middle">'
            f'{escaped_category_name}'
            f'</textPath>'
            f'</text>'
        )

    # ==================================================================
    # COUCHE 8 : Illustration au centre.
    # Le dessin de la categorie est en BLANC sur le fond colore.
    # On augmente l'epaisseur du trait pour plus de lisibilite.
    #
    # LAYER 8: Centered illustration.
    # Category drawing in WHITE over colored fill.
    # Thicker strokes for readability.
    # ==================================================================
    illustration_section = ""
    if illustration_svg:
        # Taille reduite (75 au lieu de 90) pour ne pas chevaucher le titre.
        # Reduced size (75 instead of 90) to avoid overlapping the title.
        illustration_display_size = 75
        illustration_offset_x = CENTER_X - illustration_display_size / 2
        # Place plus haut (facteur 0.90) pour laisser de la place au titre en dessous.
        # Placed higher (factor 0.90) to leave room for title below.
        illustration_offset_y = CENTER_Y - illustration_display_size * 0.90
        illustration_scale = illustration_display_size / 100

        illustration_section = (
            f'<g transform="translate({illustration_offset_x:.1f}, {illustration_offset_y:.1f}) '
            f'scale({illustration_scale:.2f})" '
            f'fill="none" stroke="#ffffff" stroke-width="4" '
            f'stroke-linecap="round" stroke-linejoin="round" '
            f'opacity="0.95">'
            f'{illustration_svg}'
            f'</g>'
        )

    # ==================================================================
    # COUCHE 9 : Titre principal.
    # Ecrit en BLANC et gras sur le fond colore.
    # Place dans la partie haute du badge, sous l'illustration.
    #
    # LAYER 9: Main title.
    # Written in WHITE and bold over the colored fill.
    # Positioned in the upper area, below the illustration.
    # ==================================================================
    title_font_size = _compute_title_font_size(title)
    # Place un peu plus bas (facteur 0.10 au lieu de 0.06) pour degager l'illustration.
    # Moved slightly lower (factor 0.10 instead of 0.06) to clear the illustration.
    title_y_position = CENTER_Y + BADGE_SIZE * 0.10

    escaped_title = _escape_svg_text(title)
    title_section = (
        f'<text x="{CENTER_X}" y="{title_y_position:.1f}" '
        f'text-anchor="middle" '
        f'font-family="{FONT_FAMILY}" '
        f'font-weight="700" '
        f'font-size="{title_font_size:.1f}" '
        f'fill="#ffffff">'
        f'{escaped_title}'
        f'</text>'
    )

    # ==================================================================
    # COUCHE 10 : Sous-titre.
    # Ecrit en SOMBRE sous la zone coloree, dans la partie blanche.
    # Plus petit et moins visible que le titre.
    #
    # LAYER 10: Subtitle.
    # Written in DARK below the colored area, in the white zone.
    # Smaller and less prominent than the title.
    # ==================================================================
    subtitle_section = ""
    if subtitle:
        subtitle_font_size = title_font_size * 0.55
        subtitle_y_position = COLOR_FILL_CUTOFF_Y + 22

        escaped_subtitle = _escape_svg_text(subtitle)
        subtitle_section = (
            f'<text x="{CENTER_X}" y="{subtitle_y_position:.1f}" '
            f'text-anchor="middle" '
            f'font-family="{FONT_FAMILY}" '
            f'font-weight="500" '
            f'font-size="{subtitle_font_size:.1f}" '
            f'fill="{DEFAULT_TEXT_COLOR}" '
            f'opacity="0.7">'
            f'{escaped_subtitle}'
            f'</text>'
        )

    # ==================================================================
    # COUCHE 11 : Texte courbe en bas — texte de posture.
    # Ecrit en SOMBRE dans la partie blanche du badge.
    # Par exemple "JE DECOUVRE" ou "JE SAIS CREER".
    #
    # LAYER 11: Curved text at bottom — posture text.
    # Written in DARK in the white area of the badge.
    # ==================================================================
    posture_text_section = ""
    if level_posture_text:
        escaped_posture_text = _escape_svg_text(level_posture_text.upper())
        posture_text_section = (
            f'<text fill="{DEFAULT_TEXT_COLOR}" '
            f'font-family="{FONT_FAMILY}" '
            f'font-size="15" '
            f'font-weight="600" '
            f'letter-spacing="0.12em" '
            f'opacity="0.75">'
            f'<textPath href="#arc-bottom" startOffset="50%" text-anchor="middle">'
            f'{escaped_posture_text}'
            f'</textPath>'
            f'</text>'
        )

    # ==================================================================
    # ASSEMBLAGE FINAL du SVG.
    # L'ordre des couches est crucial :
    #   ombre → glow → fond blanc → aplat couleur → filet decoratif
    #   → bordure nette → texte categorie → illustration → titre
    #   → sous-titre → posture.
    #
    # FINAL SVG ASSEMBLY.
    # Layer order is crucial:
    #   shadow → glow → white fill → colored fill → decorative ring
    #   → crisp border → category text → illustration → title
    #   → subtitle → posture text.
    # ==================================================================
    complete_svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
 viewBox="0 0 {BADGE_SIZE} {BADGE_SIZE}"
 width="{BADGE_SIZE}" height="{BADGE_SIZE}"
 role="img"
 aria-labelledby="badge-title">
<title id="badge-title">{badge_description}</title>
<defs>
<path id="arc-top" d="{TEXT_ARC_TOP_PATH}" fill="none"/>
<path id="arc-bottom" d="{TEXT_ARC_BOTTOM_PATH}" fill="none"/>
<clipPath id="badge-clip">
<path d="{chosen_shape_path}"/>
</clipPath>
<filter id="drop-shadow" x="-15%" y="-10%" width="130%" height="130%">
<feDropShadow dx="0" dy="3" stdDeviation="{SHADOW_BLUR}" flood-color="#000000" flood-opacity="{SHADOW_OPACITY}"/>
</filter>
</defs>
{shadow_layer}
{glow_layer}
{white_fill_layer}
{colored_fill_layer}
{inner_ring_layer}
{main_border_layer}
{category_text_section}
{illustration_section}
{title_section}
{subtitle_section}
{posture_text_section}
</svg>"""

    return complete_svg


# ============================================================================
# Fonctions utilitaires.
# Utility functions.
# ============================================================================

def _compute_title_font_size(title_text):
    """
    On calcule la taille de la police pour que le titre rentre dans le badge.
    Plus le texte est long, plus la police est petite.
    Compute font size so title fits inside the badge.
    """
    text_length = len(title_text)

    if text_length <= 8:
        return BADGE_SIZE * 0.065
    elif text_length <= 15:
        return BADGE_SIZE * 0.055
    elif text_length <= 25:
        return BADGE_SIZE * 0.042
    else:
        return BADGE_SIZE * 0.034


def _escape_svg_text(text):
    """
    On remplace les caracteres speciaux pour qu'ils s'affichent bien en SVG.
    Escape special characters for SVG display.
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text
