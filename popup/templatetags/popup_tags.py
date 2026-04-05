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

    template = loader.get_template("popup/popup.html")

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
