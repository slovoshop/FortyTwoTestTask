
from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag
def edit_link(anyobject):
    try:
        reverse_path = 'admin:{}_{}_change'.format(anyobject._meta.app_label,
                                                   anyobject._meta.model_name)
    except AttributeError:
        raise template.TemplateSyntaxError(
            'edit_link tag requires a model instance')

    return reverse(reverse_path, args=(anyobject.id,))
