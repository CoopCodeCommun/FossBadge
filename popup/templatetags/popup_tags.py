from django import template
from django.template import loader
from pictures.templatetags.pictures import picture
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


POPUP_CLOSE_JS_FUNCTION = "closePopup"
POPUP_OPEN_JS_FUNCTION = "openPopup"
POPUP_SCROLL_TOP_JS_FUNCTION="scrollToTopContent"
POPUP_CONTENT_ID = "customPopup-content"


@register.simple_block_tag
def popup(content, width="40%", name="default", *args, **kwargs):
    outside_click_close = kwargs.pop("outside_click_close", False)
    esc_key_close = kwargs.pop("esc_key_close", True)

    template = loader.get_template("popup/popup.html")

    return template.render(
        {
            "content": content,
            "width": width,
            "outside_click_close": outside_click_close,
            "esc_key_close": esc_key_close,
            "name" : name,
        }
    )

@register.simple_tag
def popup_common():
    template = loader.get_template("popup/popup_common.html")
    return template.render()


@register.simple_tag
def popup_close(name="default"):
    return mark_safe(f"{POPUP_CLOSE_JS_FUNCTION}('{name}')")


@register.simple_tag
def popup_open(name="default", width=None):
    return mark_safe(f"{POPUP_OPEN_JS_FUNCTION}('{name}','{width}')")


@register.simple_tag
def popup_content_id(name="default"):
    return mark_safe(f"#{POPUP_CONTENT_ID}-{name}")


@register.simple_tag
def popup_scroll_to_top(name="default",):
    return mark_safe(f"{POPUP_SCROLL_TOP_JS_FUNCTION}('{name}')")
