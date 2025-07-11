from django import template

register = template.Library()

# yourapp/templatetags/form_filters.py


@register.filter(name="add_class")
def add_class(field, css_class):
    existing_classes = field.field.widget.attrs.get("class", "")
    classes = (existing_classes + " " + css_class).strip()
    return field.as_widget(attrs={"class": classes})


@register.filter(name="attr")
def attr(field, attr_str):
    """
    Generic filter to add arbitrary attribute(s) e.g. 'aria-describedby=help_id'
    Usage: {{ field|attr:"aria-describedby=help_id" }}
    """
    attrs = {}
    for pair in attr_str.split():
        if "=" in pair:
            k, v = pair.split("=", 1)
            attrs[k] = v
    return field.as_widget(attrs=attrs)
