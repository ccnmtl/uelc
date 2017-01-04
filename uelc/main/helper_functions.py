from datetime import datetime
import hashlib
import hmac
import json
from random import randint
import time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from pagetree.generic.views import generic_instructor_page, generic_edit_page
from pagetree.models import Hierarchy, Section, PageBlock

from gate_block.models import GateSubmission
from uelc.main.models import CaseMap, Case, CaseAnswer


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


def get_vals_from_casemap(casemap_value):
    vals = [int(i) for i in casemap_value if int(i) > 0]
    return vals


def get_part_by_section(section):
    key = 'uelc.{}.get_part_by_section'.format(section.pk)
    v = cache.get(key)
    if v is not None:
        return v

    modules = section.get_root().get_children()
    sec_module = section.get_module()
    part = 0
    for idx, module in enumerate(modules):
        if module == sec_module:
            part = idx

    if part == 0:
        v = 1
    else:
        v = float(2) + (part * .1)

    cache.set(key, v)
    return v


def get_partchoice_by_usermap(usermap):
    vals = get_vals_from_casemap(usermap.value)
    part = 1
    if len(vals) >= 2:
        part = float(2) + (vals[1] * .1)
    if len(vals) >= 4:
        part = part + float((vals[3] * .01))
    return part


def get_p1c1(casemap_value):
    return get_vals_from_casemap(casemap_value)[1]


def can_show(request, section, casemap_value):
    cmvl = list(casemap_value)
    tree = section.get_tree()
    section_index = [sec for sec in
                     range(len(tree))
                     if tree[sec] == section][0] + 1
    try:
        content_value = [int(i) for i in
                         reversed(cmvl[0:section_index])
                         if int(i) > 0][0]
    except IndexError:
        content_value = 0

    return content_value


def can_show_gateblock(gate_section, part_usermap,
                       part_section=None):
    if part_section is None:
        part_section = get_part_by_section(gate_section)

    can_show = False
    if part_section == 1 or part_section == round(part_usermap, 1):
        can_show = True
    return can_show


def p1pre(casemap_value):
    p1pre = 0
    vals = get_vals_from_casemap(casemap_value)
    if len(vals) > 1:
        p1pre = vals[0]
    return p1pre


def is_curveball(current_section, pageblocks=None):
    block = None
    if pageblocks is None and current_section is not None:
        pageblocks = current_section.pageblock_set.all()

    if pageblocks:
        for pb in pageblocks:
            block = pb.block()
            if (hasattr(block, 'display_name') and
                    block.display_name == "Curveball Block"):
                return (True, block)

    return (False, block)


def is_decision_block(current_section, user, pageblocks=None):
    if pageblocks is None:
        pageblocks = current_section.pageblock_set.all()
    for pb in pageblocks:
        block = pb.block()
        if (hasattr(block, 'display_name') and
                block.display_name == "Decision Block"):
            ss = block.submission_set.filter(user=user).last()
            ca = None
            if ss:
                response = ss.response_set.filter(
                    submission_id=ss.id).last()
                ca = CaseAnswer.objects.get(answer=response.answer())
            return (True, block, ca)
    return (False, None, None)


def is_next_curveball(section):
    key = 'uelc.{}.is_next_curveball'.format(section.pk)
    v = cache.get(key)
    if v is not None:
        return v

    nxt = section.get_next()
    is_cb = is_curveball(nxt)
    if is_cb[0]:
        cache.set(key, is_cb)
        return is_cb
    else:
        cache.set(key, False)
        return False


def content_blocks_by_hierarchy_and_class(hierarchy, cls):
    ctype = ContentType.objects.get_for_model(cls)
    return PageBlock.objects.filter(
        content_type__pk=ctype.pk, section__hierarchy=hierarchy).values_list(
            'object_id', flat=True)
