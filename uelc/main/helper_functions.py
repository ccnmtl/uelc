from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from pagetree.generic.views import generic_instructor_page, generic_edit_page

from gate_block.models import GateSubmission
from uelc.main.models import CaseMap, Case


def get_cases(request):
    try:
        user = User.objects.get(id=request.user.id)
        cohort = user.profile.cohort
        case = cohort.case
        return case
    except ObjectDoesNotExist:
        return


def admin_ajax_page_submit(section, user):
    for block in section.pageblock_set.all():
        if block.block().display_name == "Gate Block":
            block_obj = block.block()
            GateSubmission.objects.create(
                gateblock_id=block_obj.id,
                section=section,
                gate_user_id=user.id)


def admin_ajax_reset_page(section, user):
    case = Case.objects.get(hierarchy=section.hierarchy)
    try:
        casemap = CaseMap.objects.get(user=user, case=case)
    except ObjectDoesNotExist:
        casemap = CaseMap.objects.create(user=user, case=case)
        casemap.save()
    data = dict(question=0)
    casemap.save_value(section, data)
    for block in section.pageblock_set.all():
        if block.block().display_name == "Gate Block":
            gso = GateSubmission.objects.filter(
                section=section,
                gate_user_id=user.id)
            gso.delete()
    section.reset(user)


def page_submit(section, request):
    proceed = section.submit(request.POST, request.user)
    if proceed:
        next_section = section.get_next()
        if next_section:
            return HttpResponseRedirect(next_section.get_absolute_url())
        else:
            # they are on the "last" section of the site
            # all we can really do is send them back to this page
            return HttpResponseRedirect(section.get_absolute_url())
    # giving them feedback before they proceed
    return HttpResponseRedirect(section.get_absolute_url())


def reset_page(section, request):
    section.reset(request.user)
    return HttpResponseRedirect(section.get_absolute_url())


def get_root_context(request):
    context = dict()
    try:
        cases = get_cases(request)
        if cases:
            roots = [(case.hierarchy.get_absolute_url(),
                      case.hierarchy.name)
                     for case in cases]
            context = dict(roots=roots)
    except ObjectDoesNotExist:
        pass
    return context


def has_responses(section):
    quizzes = [p.block() for p in section.pageblock_set.all()
               if hasattr(p.block(), 'needs_submit')
               and p.block().needs_submit()]
    return quizzes != []


def get_user_map(hierarchy, user):
    case = Case.objects.get(hierarchy=hierarchy)
    # first check and see if a case map exists for the user
    # if not, they have not submitted an answer to a question
    try:
        casemap = CaseMap.objects.get(user=user, case=case)
    except ObjectDoesNotExist:
        casemap = CaseMap.objects.create(user=user, case=case)
        casemap.save()
    return casemap


@login_required
def pages_save_edit(request, hierarchy_name, path):
    # do auth on the request if you need the user to be logged in
    # or only want some particular users to be able to get here
    return generic_edit_page(request, path, hierarchy=hierarchy_name)


@login_required
def instructor_page(request, hierarchy_name, path):
    return generic_instructor_page(request, path, hierarchy=hierarchy_name)


def visit_root(section, fallback_url):
    """ if they try to visit the root, we need to send them
    either to the first section on the site, or to
    the admin page if there are no sections (so they
    can add some)"""
    ns = section.get_next()
    hierarchy = section.hierarchy
    if ns:
        if ns.hierarchy == hierarchy:
            # just send them to the first child
            return HttpResponseRedirect(section.get_next().get_absolute_url())
    # no sections available so
    # send them to the fallback
    return HttpResponseRedirect(fallback_url)
