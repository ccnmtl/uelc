from django import template

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
