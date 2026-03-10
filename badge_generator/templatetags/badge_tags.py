"""
Tags de template pour le generateur de badges.
On a besoin d'un tag pour afficher le SVG sans echappement HTML.
Custom template tags for the badge generator.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="safe_svg")
def safe_svg(svg_content):
    """
    On marque le contenu SVG comme sur pour l'affichage.
    Django echappe le HTML par defaut. Ce filtre dit a Django
    que le contenu SVG est sur et peut etre affiche tel quel.
    Mark SVG content as safe for display (bypass Django escaping).
    """
    if not svg_content:
        return ""
    return mark_safe(svg_content)
