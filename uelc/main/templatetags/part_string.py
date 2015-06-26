from django import template

register = template.Library()


@register.filter(name='convert')
def convert(arg):
    if arg > 1:
        part = str(arg).split('.')[0]
        choice1 = str(arg).split('.')[1][0]
        part_choice = 'part' + part + ' Choice-' + choice1
        return part_choice
    else:
        return 'part' + str(arg)


@register.filter(name='convert_part2')
def convert_part2(arg):
    if arg > 1:
        if not round(arg, 1) == round(arg, 2):
            '''then part 2 decision has been made'''
            choice = str(arg).split('.')[1][1]
            return 'p2c2-' + choice
        else:
            choice = str(arg).split('.')[1]
            return 'p1c2-' + choice
    else:
        return 0


@register.filter(name='part')
def part(arg):
    return int(arg)
