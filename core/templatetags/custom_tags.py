from django import template
from django.template import loader
from pictures.templatetags.pictures import picture
from django.utils.html import format_html

register = template.Library()

def is_svg(file_field):
    """Check if the file is an SVG."""
    if not file_field:
        return False
    name = getattr(file_field, "name", str(file_field))
    return name.lower().endswith(".svg")

@register.simple_tag()
def svg_or_picture(img_src, img_alt, ratio, **kwargs):
    """
    If the file is a svg, return an html img
    Else return the image using "picture" template tag from django-pictures

    The usage is the same to the "picture" template tag from django-pictures
    """
    if is_svg(img_src.url):
        return format_html("<img src='{}' alt='{}' class='badge-svg-icon' />", img_src.url, img_alt)

    return picture(img_src, img_alt=img_alt, ratio=ratio, **kwargs)