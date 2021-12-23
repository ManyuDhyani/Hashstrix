from django import template

register = template.Library()

@register.filter
def modulo(num, val):
    print(val)
    print(num, type(num))
    return num % val == 0