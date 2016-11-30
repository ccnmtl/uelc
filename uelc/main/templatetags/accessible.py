from django import template
from uelc.main.models import UELCHandler
from pagetree.models import PageBlock

register = template.Library()


@register.assignment_tag
def get_next_hierarchy_section(request, section):
    hierarchy = section.hierarchy
    if hierarchy == section.get_next().hierarchy:
        return True


@register.assignment_tag
def get_previous_group_user_section(request, section, previous, part):
    # make sure that group users cannot go to the
    # root page of the Part. Also make sure that the
    # 1st page in Part 1 does not have a prev link.
    prev_sec = previous
    if prev_sec.depth < 3:
        if part == 1:
            return False
        p1 = section.get_root().get_children()[0]
        prev_sec = p1.get_last_leaf()
    return prev_sec


@register.assignment_tag
def is_not_last_group_user_section(request, section, part):
    # make sure next button does not render at end of part 2
    if part > 1 and section == section.get_last_leaf():
        return False
    return True


@register.assignment_tag
def is_section_unlocked(request, section):
    unlocked = True
    for block in section.pageblock_set.all():
        bl = block.block()
        if hasattr(bl, 'needs_submit') and bl.display_name == 'Gate Block':
            unlocked = bl.unlocked(request.user, section)
        if hasattr(bl, 'needs_submit') and bl.display_name == 'Decision Block':
            unlocked = bl.unlocked(request.user, section)
        if not unlocked:
            return False
    return unlocked


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
