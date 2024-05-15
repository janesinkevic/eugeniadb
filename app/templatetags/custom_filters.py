from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    """Get an attribute from an object by its name."""
    return getattr(obj, attr_name, 0)

@register.simple_tag
def get_dynamic_attr(obj, prefix, attr_name):
    """Constructs a dynamic attribute name and retrieves its value from the object."""
    dynamic_attr = f"{prefix}{attr_name}"
    return getattr(obj, dynamic_attr, "N/A")