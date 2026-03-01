from django import template
from django.template import loader

register = template.Library()

POPUP_CLOSE_JS_FUNCTION = "closePopup"
POPUP_OPEN_JS_FUNCTION = "openPopup"

@register.simple_block_tag
def popup(content):
    template = loader.get_template('includes/popup.html')
    return template.render({
        "content": content,
        "open_func_name": POPUP_OPEN_JS_FUNCTION,
        "close_func_name": POPUP_CLOSE_JS_FUNCTION
    })

@register.simple_tag
def popup_close():
    return f"{POPUP_CLOSE_JS_FUNCTION}()"

@register.simple_tag
def popup_open():
    return f"{POPUP_OPEN_JS_FUNCTION}()"