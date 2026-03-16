from django import template
from django.template import loader

register = template.Library()

POPUP_CLOSE_JS_FUNCTION = "closePopup"
POPUP_OPEN_JS_FUNCTION = "openPopup"
POPUP_CONTENT_ID = "customPopup-content"

@register.simple_block_tag
def popup(content, popup_width="40%", *args, **kwargs):
    outside_click_close = kwargs.pop("outside_click_close", False)
    esc_key_close = kwargs.pop("esc_key_close", True)


    template = loader.get_template('base/includes/popup.html')

    return template.render({
        "content": content,
        "open_func_name": POPUP_OPEN_JS_FUNCTION,
        "close_func_name": POPUP_CLOSE_JS_FUNCTION,
        "popup_content_id":POPUP_CONTENT_ID,
        "popup_width":popup_width,
        "outside_click_close":outside_click_close,
        "esc_key_close" : esc_key_close
    })

@register.simple_tag
def popup_close():
    return f"{POPUP_CLOSE_JS_FUNCTION}()"

@register.simple_tag
def popup_open():
    return f"{POPUP_OPEN_JS_FUNCTION}()"

@register.simple_tag
def popup_content_id():
    return f"#{POPUP_CONTENT_ID}"