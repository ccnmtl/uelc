from django import template
from django.db.models.query_utils import Q
from pagetree.models import PageBlock

from uelc.main.helper_functions import can_show


register = template.Library()


@register.assignment_tag
def get_previous_group_user_section(section, previous, part):
    # make sure that group users cannot go to the root page of a Part
    if previous.depth < 3:
        if part == 1:
            # 1st page in Part 1 does not have a prev link
            return False

        # If in part 2, and previous is a root (depth=1) or module (depth=2)
        # then skip back to Part 1's last leaf
        # @todo - replace this hard-coded logic
        part1 = section.get_root().get_children()[0]
        previous = part1.get_last_leaf()

    return previous


@register.assignment_tag
def is_not_last_group_user_section(section, part):
    return part == 1 or section != section.get_last_leaf()


@register.assignment_tag
def is_section_unlocked(request, section):
    q = Q(content_type__model='gateblock') | Q(content_type__model='casequiz')
    for block in section.pageblock_set.filter(q):
        if not block.block().unlocked(request.user, section):
            return False
    return True


@register.assignment_tag
def is_block_on_user_path(request, section, block, casemap_value):
    if not request.user.profile.is_group_user():
        return True

    if block.content_type.model != 'textblockdt':
        return False

    bl = block.block()
    choice = int(bl.choice)

    if choice == 0:
        return True

    return choice == can_show(request, section, casemap_value)


@register.assignment_tag
def get_quizblock_attr(quiz_id):
    block = PageBlock.objects.filter(content_type__model='casequiz',
                                     object_id=quiz_id).first()

    if block:
        edit_url = block.section.get_edit_url()
        label = block.section.label
        return dict(edit_url=edit_url, label=label)
