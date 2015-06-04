from django import template

register = template.Library()


@register.assignment_tag
def get_selected_curveball(user, curveball_block):
    selected_curveball = curveball_block.get_latest_curveball_submission(user)
    return selected_curveball
