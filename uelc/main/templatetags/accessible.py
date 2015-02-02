from django import template
from uelc.main.models import UELCHandler
from pagetree.models import PageBlock

register = template.Library()


class SubmittedNode(template.Node):
    def __init__(self, section, nodelist_true, nodelist_false=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.section = section

    def render(self, context):
        s = context[self.section]

        if 'request' in context:
            r = context['request']
            u = r.user

            if s.submitted(u):
                return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)


@register.tag('ifsubmitted')
def submitted(parser, token):
    section = token.split_contents()[1:][0]
    nodelist_true = parser.parse(('else', 'endifsubmitted'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifsubmitted',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return SubmittedNode(section, nodelist_true, nodelist_false)


@register.assignment_tag
def is_section_unlocked(request, section):
    unlocked = True
    for block in section.pageblock_set.all():
        bl = block.block()
        if hasattr(bl, 'needs_submit') and bl.display_name == 'Gate Block':
            unlocked = bl.unlocked(request.user, section)
        if hasattr(bl, 'needs_submit') and bl.display_name == 'Case Quiz':
            unlocked = bl.unlocked(request.user, section)
        if not unlocked:
            return False
    return unlocked


# Need to make this its own tempalte tag as it requires pulling in
# UELC Handler
@register.assignment_tag
def is_block_on_user_path(request, section, block, casemap_value):
    hand = UELCHandler.objects.get_or_create(
        hierarchy=section.hierarchy,
        depth=0,
        path=section.hierarchy.base_url)[0]
    can_show = hand.can_show(request, section, casemap_value)
    bl = block.block()
    if hasattr(bl, 'choice') and bl.display_name == 'Text BlockDT':
        #ad = bl.after_decision
        choice = bl.choice
        if int(choice) == can_show or int(choice) == 0:
            return True
    return False


@register.assignment_tag
def is_module(section):
    is_mod = False
    root = section.get_root()
    modules = root.get_children()
    for sections in modules:
        if sections.id == section.id:
            is_mod = True
    return is_mod


@register.assignment_tag
def is_from_another_module(section_one, section_two):
    mod_one = section_one.get_root()
    mod_two = section_two.get_root()
    if mod_one.id == mod_two.id:
        return False
    else:
        return True


@register.assignment_tag
def get_quizblock_attr(quiz_id):
    pbs = PageBlock.objects.filter(object_id=quiz_id)
    for pb in pbs:
        block = pb.block()
        if block.display_name == "Case Quiz":
            edit_url = block.pageblock().section.get_edit_url()
            label = block.pageblock().section.label
            return dict(edit_url=edit_url, label=label)
