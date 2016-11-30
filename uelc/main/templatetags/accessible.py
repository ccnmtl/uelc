from django import template
from django.db.models.query_utils import Q
from pagetree.models import PageBlock

from uelc.main.models import UELCHandler


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


# Need to make this its own tempalte tag as it requires pulling in
# UELC Handler
@register.assignment_tag
def is_block_on_user_path(request, section, block, casemap_value):
    if not request.user.profile.profile_type == 'group_user':
        return True
    hand = UELCHandler.objects.get_or_create(
        hierarchy=section.hierarchy,
        depth=0,
        path=section.hierarchy.base_url)[0]
    can_show = hand.can_show(request, section, casemap_value)
    bl = block.block()
    if hasattr(bl, 'choice') and bl.display_name == 'Text Block':
        choice = bl.choice
        if int(choice) == can_show or int(choice) == 0:
            return True
    return False


@register.assignment_tag
def get_quizblock_attr(quiz_id):
    pbs = PageBlock.objects.filter(object_id=quiz_id)
    for pb in pbs:
        block = pb.block()
        if block.display_name == 'Decision Block':
            edit_url = block.pageblock().section.get_edit_url()
            label = block.pageblock().section.label
            return dict(edit_url=edit_url, label=label)
