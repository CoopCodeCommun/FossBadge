from django import template
from django.template import loader
from pictures.templatetags.pictures import picture
from django.utils.html import format_html

register = template.Library()

POPUP_CLOSE_JS_FUNCTION = "closePopup"
POPUP_OPEN_JS_FUNCTION = "openPopup"
POPUP_SCROLL_TOP_JS_FUNCTION="scrollToTopContent"
POPUP_CONTENT_ID = "customPopup-content"


@register.simple_block_tag
def popup(content, popup_width="40%", *args, **kwargs):
    outside_click_close = kwargs.pop("outside_click_close", False)
    esc_key_close = kwargs.pop("esc_key_close", True)

    template = loader.get_template("base/includes/popup.html")

    return template.render(
        {
            "content": content,
            "open_func_name": POPUP_OPEN_JS_FUNCTION,
            "close_func_name": POPUP_CLOSE_JS_FUNCTION,
            "scroll_top_func_name":POPUP_SCROLL_TOP_JS_FUNCTION,
            "popup_content_id": POPUP_CONTENT_ID,
            "popup_width": popup_width,
            "outside_click_close": outside_click_close,
            "esc_key_close": esc_key_close,
        }
    )


@register.simple_tag
def popup_close():
    return f"{POPUP_CLOSE_JS_FUNCTION}()"


@register.simple_tag
def popup_open():
    return f"{POPUP_OPEN_JS_FUNCTION}()"


@register.simple_tag
def popup_content_id():
    return f"#{POPUP_CONTENT_ID}"

@register.simple_tag
def popup_scroll_to_top():
    return f"{POPUP_SCROLL_TOP_JS_FUNCTION}()"


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