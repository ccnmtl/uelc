import hmac
import hashlib
import time
from datetime import datetime
from random import randint
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from pagetree.generic.views import generic_instructor_page, generic_edit_page
from pagetree.models import Hierarchy, Section

from gate_block.models import GateSubmission
from uelc.main.models import CaseMap, Case


def get_cases(request):
    try:
        user = User.objects.get(id=request.user.id)
        cohort = user.profile.cohort
        case = cohort.case
        return case
    except AttributeError:
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
        else:
            roots = [('None', 'None')]
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


@login_required
def fresh_token(request, hierarchy_name):
    hierarchy = get_object_or_404(Hierarchy, name=hierarchy_name)
    return dict(hierarchy=hierarchy, token=gen_token(request, hierarchy.name),
                websockets_base=settings.WINDSOCK_WEBSOCKETS_BASE)


def gen_token(request, hierarchy_name):
    username = request.user.username
    sub_prefix = "%s.pages/%s/facilitator/" % (settings.ZMQ_APPNAME, hierarchy_name)
    pub_prefix = sub_prefix + "." + username
    now = int(time.mktime(datetime.now().timetuple()))
    salt = randint(0, 2 ** 20)
    ip_address = (request.META.get("HTTP_X_FORWARDED_FOR", "")
                  or request.META.get("REMOTE_ADDR", ""))
    hmc = hmac.new(settings.WINDSOCK_SECRET,
                   '%s:%s:%s:%d:%d:%s' % (username, sub_prefix,
                                          pub_prefix, now, salt,
                                          ip_address),
                   hashlib.sha1
                   ).hexdigest()
    return '%s:%s:%s:%d:%d:%s:%s' % (username, sub_prefix,
                                     pub_prefix, now, salt,
                                     ip_address, hmc)


@login_required
def fresh_grp_token(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    print "fresh_grp_token"
    print fresh_grp_token
    return dict(section=section, token=gen_group_token(request, section.pk),
                websockets_base=settings.WINDSOCK_WEBSOCKETS_BASE)


def gen_group_token(request, section_pk):
    print "gen_group_token"
    print gen_group_token
    username = request.user.username
    sub_prefix = "%s.%d" % (settings.ZMQ_APPNAME, section_pk)
    print "sub_prefix"
    print sub_prefix
    pub_prefix = sub_prefix + "." + username
    now = int(time.mktime(datetime.now().timetuple()))
    salt = randint(0, 2 ** 20)
    ip_address = (request.META.get("HTTP_X_FORWARDED_FOR", "")
                  or request.META.get("REMOTE_ADDR", ""))
    hmc = hmac.new(settings.WINDSOCK_SECRET,
                   '%s:%s:%s:%d:%d:%s' % (username, sub_prefix,
                                          pub_prefix, now, salt,
                                          ip_address),
                   hashlib.sha1
                   ).hexdigest()
    print "before return"
    return '%s:%s:%s:%d:%d:%s:%s' % (username, sub_prefix,
                                     pub_prefix, now, salt,
                                     ip_address, hmc)
