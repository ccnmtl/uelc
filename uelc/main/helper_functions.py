import json
import hmac
import hashlib
import time
from datetime import datetime
from random import randint
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404

from pagetree.generic.views import generic_instructor_page, generic_edit_page
from pagetree.models import Hierarchy, Section

from gate_block.models import GateSubmission
from uelc.main.models import CaseMap, Case


def get_cases(request):
    """
    Returns the cases for the current user if available. Otherwise,
    returns None.
    """
    try:
        user = User.objects.get(id=request.user.id)
        cohort = user.profile.cohort
        cases = cohort.case
        return cases
    except AttributeError:
        return None


def admin_ajax_page_submit(section, user):
    for block in section.pageblock_set.all():
        block_obj = block.block()
        if block_obj.display_name == "Gate Block":
            GateSubmission.objects.create(
                gateblock_id=block_obj.id,
                section=section,
                gate_user_id=user.id)


def admin_ajax_reset_page(section, user):
    case = Case.objects.get(hierarchy=section.hierarchy)
    try:
        casemap, created = CaseMap.objects.get_or_create(user=user, case=case)
    except CaseMap.MultipleObjectsReturned:
        casemap = CaseMap.objects.filter(user=user, case=case).first()
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
        roots = [('None', 'None')]
        if cases:
            roots = [(case.hierarchy.get_absolute_url(),
                      case.hierarchy.name)
                     for case in cases]
        context = dict(roots=roots)
    except ObjectDoesNotExist:
        pass
    return context


def get_user_map(hierarchy, user):
    case = Case.objects.get(hierarchy=hierarchy)
    # first check and see if a case map exists for the user
    # if not, they have not submitted an answer to a question
    try:
        casemap, created = CaseMap.objects.get_or_create(user=user, case=case)
    except CaseMap.MultipleObjectsReturned:
        # The CaseMap should really have (user, case) unique_together,
        # but until then, don't fail if this is encountered.
        casemap = CaseMap.objects.filter(user=user, case=case).first()
    return casemap


@login_required
def pages_save_edit(request, hierarchy_name, path):
    # do auth on the request if you need the user to be logged in
    # or only want some particular users to be able to get here
    return generic_edit_page(request, path, hierarchy=hierarchy_name)


@login_required
def instructor_page(request, hierarchy_name, path):
    return generic_instructor_page(request, path, hierarchy=hierarchy_name)


@login_required
def fresh_token(request, hierarchy_name=None):
    if hierarchy_name is None:
        hierarchy_name = 'main'
    hierarchy = get_object_or_404(Hierarchy, name=hierarchy_name)
    return HttpResponse(
        json.dumps(
            dict(hierarchy=hierarchy.as_dict(),
                 token=gen_fac_token(request, hierarchy),
                 websockets_base=settings.WINDSOCK_WEBSOCKETS_BASE)),
        content_type='applicaton/json')


@login_required
def fresh_grp_token(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    return HttpResponse(
        json.dumps(dict(section=section.as_dict(),
                        token=gen_group_token(request, section.pk),
                        websockets_base=settings.WINDSOCK_WEBSOCKETS_BASE)),
        content_type='applicaton/json')


def gen_token(request, sub_prefix):
    username = request.user.username
    pub_prefix = sub_prefix + "." + username
    now = int(time.mktime(datetime.now().timetuple()))
    salt = randint(0, 2 ** 20)
    ip_address = (request.META.get("HTTP_X_FORWARDED_FOR", "") or
                  request.META.get("REMOTE_ADDR", ""))
    hmc = hmac.new(settings.WINDSOCK_SECRET,
                   '%s:%s:%s:%d:%d:%s' % (username, sub_prefix,
                                          pub_prefix, now, salt,
                                          ip_address),
                   hashlib.sha1
                   ).hexdigest()
    return '%s:%s:%s:%d:%d:%s:%s' % (username, sub_prefix,
                                     pub_prefix, now, salt,
                                     ip_address, hmc)


def gen_fac_token(request, hierarchy):
    hierarchy_name = "module_%02d" % hierarchy.pk
    sub_prefix = "%s.pages/%s/facilitator/" % (settings.ZMQ_APPNAME,
                                               hierarchy_name)
    return gen_token(request, sub_prefix)


def gen_group_token(request, section_pk):
    sub_prefix = "%s.%d" % (settings.ZMQ_APPNAME, section_pk)
    return gen_token(request, sub_prefix)


def get_user_last_location(user, hierarchy):
    """Returns last Pagetree Section the user has visited in the hierarchy"""
    ul = user.userlocation_set.filter(hierarchy=hierarchy).first()
    if ul is None:
        return None

    section = hierarchy.find_section_from_path(ul.path)
    if section is None:
        # If we can't find the Section from the path, it may be
        # an outdated path. In that case, clear the UserLocation
        ul.delete()

    return section
