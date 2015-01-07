from django.views.generic.base import TemplateView
from pagetree.generic.views import PageView, EditView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from pagetree.models import UserPageVisit, Hierarchy, Section, UserLocation
from pagetree.generic.views import generic_instructor_page, generic_edit_page
from django.shortcuts import render
from django.contrib.auth.models import User
from uelc.main.models import Case, CaseMap, UELCHandler
from gate_block.models import GateBlock, GateSubmission
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import HttpResponseNotFound
from pagetree.helpers import get_section_from_path


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


class SectionMixin(object):
    def get_section(self, path):
        return get_section_from_path(
            path,
            hierarchy_name=self.hierarchy_name,
            hierarchy_base=self.hierarchy_base)

    def get_extra_context(self):
        return self.extra_context

    def perform_checks(self, request, path):
        return None


def get_cases(request):
    try:
        user = User.objects.get(id=request.user.id)
        cohorts = user.profile.cohorts
        cohort_names = cohorts.split(', ')
        cases = Case.objects.filter(cohort__name__in=cohort_names)
        return cases
    except ObjectDoesNotExist:
        return


def admin_ajax_page_submit(section, user, post):
    for block in section.pageblock_set.all():
        if block.block().display_name == "Gate Block":
            block_obj = block.block()
            GateSubmission.objects.create(
                gateblock_id=block_obj.id,
                section=section,
                gate_user_id=user.id)


def admin_ajax_reset_page(section, user):
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


class IndexView(TemplateView):
    template_name = "main/index.html"

    def get(self, request):
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
        return render(request, self.template_name, context)


def has_responses(section):
    quizzes = [p.block() for p in section.pageblock_set.all()
               if hasattr(p.block(), 'needs_submit')
               and p.block().needs_submit()]
    return quizzes != []


class DynamicHierarchyMixin(object):
    def dispatch(self, *args, **kwargs):
        name = kwargs.pop('hierarchy_name', None)
        if name is None:
            msg = "No hierarchy named %s found" % name
            return HttpResponseNotFound(msg)
        else:
            self.hierarchy_name = name
            self.hierarchy_base = Hierarchy.objects.get(name=name).base_url
        return super(DynamicHierarchyMixin, self).dispatch(*args, **kwargs)


class RestrictedModuleMixin(object):
    def dispatch(self, *args, **kwargs):
        cases = get_cases(self.request)
        if cases:
            for case in cases:
                case_hier_id = case.hierarchy_id
                case_hier = Hierarchy.objects.get(id=case_hier_id)
                if case_hier.name == self.hierarchy_name:
                    return super(RestrictedModuleMixin,
                                 self).dispatch(*args, **kwargs)
        return HttpResponse("you don't have permission")


def get_user_map(pageview, request):
    hierarchy = pageview.module.hierarchy
    case = Case.objects.get(hierarchy=hierarchy)
    user = request.user
    # first check and see if a case map exists for the user
    # if not, they have not submitted an answer to a question
    try:
        casemap = CaseMap.objects.get(user=user, case=case)
    except ObjectDoesNotExist:
        casemap = CaseMap.objects.create(user=user, case=case)
        casemap.save()
    return casemap


class UELCPageView(LoggedInMixin,
                   DynamicHierarchyMixin,
                   RestrictedModuleMixin,
                   PageView):
    template_name = "pagetree/page.html"
    gated = False

    def itterate_blocks(self, section):
        for block in section.pageblock_set.all():
            display_name = block.block().display_name
            if (hasattr(block.block(), 'needs_submit') and
                    display_name == 'Gate Block'):
                return block.block()
        return False

    def get_next_gate(self, section):
        block = self.itterate_blocks(section)
        last_sibling = self.section.get_last_sibling()
        if block:
            return (block, section)
        block = self.itterate_blocks(last_sibling)
        if block:
            return (block, last_sibling)
        return False

    def run_section_gatecheck(self, user, path, uloc):
        section_gatecheck = self.section.gate_check(self.request.user)
        if not section_gatecheck[0]:
            #gate_section = section_gatecheck[1]
            gate_section_gateblock = self.get_next_gate(self.section)
            if not gate_section_gateblock:
                block_unlocked = True
            else:
                block_unlocked = gate_section_gateblock[0].unlocked(
                    self.request.user, gate_section_gateblock[1])
                if not block_unlocked:
                    back_url = self.section.get_previous().get_absolute_url()
                    return HttpResponseRedirect(back_url)
        else:

            uloc[0].path = path
            uloc[0].save()

    def get(self, request, path):
        hierarchy = self.module.hierarchy
        case = Case.objects.get(hierarchy=hierarchy)
        uloc = UserLocation.objects.get_or_create(
            user=request.user,
            hierarchy=hierarchy)
        casemap = get_user_map(self, request)
        allow_redo = False
        needs_submit = self.section.needs_submit()
        if needs_submit:
            allow_redo = self.section.allow_redo()
        self.upv.visit()
        instructor_link = has_responses(self.section)
        case_quizblocks = []
        #prev_section = self.section.get_previous()
        for block in self.section.pageblock_set.all():
            # make sure that all pageblocks on page
            # have been submitted. Re: potential bug in
            # Section.submit() in Pageblock library
            if hasattr(block.block(), "unlocked"):
                block.block().unlocked(request.user, self.section)
                display_name = block.block().display_name
                if (hasattr(block.block(), 'needs_submit') and
                        display_name == 'Case Quiz'):
                        # is the quiz really submitted?
                        # if so add yes/no to dict
                        quiz = block.block()
                        completed = quiz.is_submitted(quiz, request.user)
                        case_quizblocks.append(dict(id=block.id,
                                                    completed=completed))

        # if gateblock is not unlocked then return to last known page
        # section.gate_check(user), doing this because hierarchy cannot
        # be "gated" because we will be skipping around depending on
        # user decisions.
        self.run_section_gatecheck(request.user, path, uloc)

        context = dict(
            section=self.section,
            module=self.module,
            needs_submit=needs_submit,
            allow_redo=allow_redo,
            is_submitted=self.section.submitted(request.user),
            modules=self.root.get_children(),
            root=self.section.hierarchy.get_root(),
            instructor_link=instructor_link,
            is_view=True,
            case=case,
            case_quizblocks=case_quizblocks,
            casemap=casemap,
        )
        context.update(self.get_extra_context())

        # handler stuff
        if casemap is None:
            #upv = self.section.get_uservisit(request.user)
            hand = UELCHandler.objects.get_or_create(
                hierarchy=hierarchy,
                depth=0)[0]
            cml = hand.create_case_map_list(casemap)
            hand.populate_map_obj(cml)
            # case_parts = self.section.get_root().get_children()
            # 3 things prevent users from proceeding when gated = True
            # 1) a pageblock that is locked
            # 2) a section that is not_submitted if need_submit
            # 3) a upv that is "incomplete" -->
            #    section.get_uservisit(request.user)
            #    also can be--> section.gate_check(user)
        return render(request, self.template_name, context)

    def get_extra_context(self, **kwargs):
        menu = []
        visits = UserPageVisit.objects.filter(user=self.request.user,
                                              status='complete')
        visit_ids = visits.values_list('section__id', flat=True)
        previous_unlocked = True
        for section in self.root.get_descendants():
            unlocked = section.id in visit_ids
            item = {
                'id': section.id,
                'url': section.get_absolute_url(),
                'label': section.label,
                'depth': section.depth,
                'slug': section.slug,
                'disabled': not(previous_unlocked or section.id in visit_ids)
            }
            if section.depth == 3 and section.get_children():
                item['toggle'] = True
            menu.append(item)
            previous_unlocked = unlocked
            uv = self.section.get_uservisit(self.request.user)
            try:
                status = uv.status
            except AttributeError:
                status = 'incomplete'
        return {'menu': menu, 'page_status': status}

    def post(self, request, path):
        # user has submitted a form. deal with it
        # make sure that they have not submitted
        # a blank form, key "case" is included on
        # all case_quiz submissions thus, must
        # have more than one key

        if len(request.POST.keys()) > 1:
            if request.POST.get('action', '') == 'reset':
                self.upv.visit(status="incomplete")
                return reset_page(self.section, request)
            #self.upv.visit(status="complete")
            return page_submit(self.section, request)
        else:
            return HttpResponseRedirect(request.path)


class UELCEditView(LoggedInMixinSuperuser,
                   DynamicHierarchyMixin,
                   EditView):
    template_name = "pagetree/edit_page.html"


class FacilitatorView(LoggedInMixinSuperuser,
                      DynamicHierarchyMixin,
                      TemplateView,
                      SectionMixin):
    template_name = "pagetree/facilitator.html"
    extra_context = dict()

    def set_upv(self, user, section, status):
        try:
            upv = UserPageVisit.objects.filter(section=section, user=user)[0]
            upv.status = status
            upv.save()
        except IndexError:
            pass
        return

    def post(self, request, path):
        # need to override the user if submitted by facilitator
        # user or facilitator has submitted a form. deal with it
        user = User.objects.get(id=request.POST.get('user_id'))
        action = request.POST.get('action')
        section = Section.objects.get(id=request.POST.get('section'))
        post = request.POST
        if action == 'submit':
            self.set_upv(user, section, "complete")
            admin_ajax_page_submit(section, user, post)
        if action == 'reset':
            self.set_upv(user, section, "incomplete")
            admin_ajax_reset_page(section, user)
        return HttpResponseRedirect(request.path)

    def dispatch(self, request, *args, **kwargs):
        path = kwargs['path']
        rv = self.perform_checks(request, path)
        if rv is not None:
            return rv
        return super(FacilitatorView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        '''
        * get the section of each gateblock
        * determine number of levels in tree
        * determine the level and place of the section in the tree
        '''
        path = kwargs['path']
        user = self.request.user
        section = self.get_section(path)
        root = section.hierarchy.get_root()
        hierarchy = section.hierarchy
        case = Case.objects.get(hierarchy=hierarchy)
        # is there really only going to be one cohort per case?
        cohort = case.cohort
        cohort_users = cohort.user.all()
        gateblocks = GateBlock.objects.all()
        user_sections = []
        for user in cohort_users:
            gate_sections = [(g.pageblock().section,
                              g, g.unlocked(user, section))
                             for g in gateblocks]
            user_sections.append([user, gate_sections])
        quizzes = [p.block() for p in section.pageblock_set.all()
                   if hasattr(p.block(), 'needs_submit')
                   and p.block().needs_submit()]
        context = dict(section=section,
                       quizzes=quizzes,
                       user_sections=user_sections,
                       module=section.get_module(),
                       modules=root.get_children(),
                       root=section.hierarchy.get_root())
        context.update(self.get_extra_context())
        return context


@login_required
def pages_save_edit(request, hierarchy_name, path):
    # do auth on the request if you need the user to be logged in
    # or only want some particular users to be able to get here
    return generic_edit_page(request, path, hierarchy=hierarchy_name)


@login_required
def instructor_page(request, hierarchy_name, path):
    return generic_instructor_page(request, path, hierarchy=hierarchy_name)
