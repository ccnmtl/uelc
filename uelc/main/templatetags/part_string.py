from django import template

register = template.Library()

@register.filter(name='convert')
def convert(arg):
    if arg > 1:
        part = str(arg).split('.')[0]
        choice = str(arg).split('.')[1]
        part_choice = 'part' + part + ' Choice-' + choice
        return part_choice
    else:
        return 'part' + str(arg)