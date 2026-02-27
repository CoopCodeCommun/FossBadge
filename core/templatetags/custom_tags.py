from django import template
from django.template import loader, Context

register = template.Library()

@register.simple_block_tag
def popup(content):
    template = loader.get_template('includes/popup.html')
    return template.render({
        "content": content,
    })