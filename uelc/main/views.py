import json
import zmq
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View
from pagetree.generic.views import PageView, EditView, UserPageVisitor
from pagetree.models import UserPageVisit, Hierarchy, Section, UserLocation
from quizblock.models import Question, Answer
from gate_block.models import GateBlock
from uelc.main.helper_functions import (
    get_root_context, get_user_map, visit_root,
    has_responses, reset_page, page_submit, admin_ajax_page_submit,
    gen_token)
from uelc.mixins import (
    LoggedInMixin, LoggedInFacilitatorMixin,
    SectionMixin, LoggedInMixinAdmin, DynamicHierarchyMixin,
    RestrictedModuleMixin)
from uelc.main.models import (
    Cohort, UserProfile, CreateUserForm, Case,
    EditUserPassForm, CreateHierarchyForm,
    CaseAnswerForm, CaseAnswer, UELCHandler,
    LibraryItem,
    )


zmq_context = zmq.Context()
other_zmq_context = zmq.Context()

class IndexView(TemplateView):
    template_name = "main/index.html"

    def get(self, request):
        root_context = get_root_context(request)
        if 'roots' in root_context.keys():
            roots = [root for root in root_context['roots']]
            hierarchy_names = [root[1] for root in roots]
            hierarchies = Hierarchy.objects.filter(name__in=hierarchy_names)
            cases = Case.objects.filter(
                hierarchy__in=hierarchies).order_by('id')
            context = dict(
                roots=roots,
                cases=cases
            )
            return render(request, self.template_name, context)

        return render(request, self.template_name, root_context)


class UELCPageView(LoggedInMixin,
                   DynamicHierarchyMixin,
                   RestrictedModuleMixin,
                   PageView):
    template_name = "pagetree/page.html"
    no_root_fallback_url = "/"
    gated = False

    def perform_checks(self, request, path):
        self.section = self.get_section(path)
        self.root = self.section.hierarchy.get_root()
        self.module = self.section.get_module()
        pt = request.user.profile.profile_type
        ns = self.section.get_next()
        hierarchy = self.section.hierarchy
        if ns:
            ns_hierarchy = ns.hierarchy
        else:
            ns_hierarchy = False
        base_url = self.section.hierarchy.base_url
        if self.section.is_root():
            if not ns or not(ns_hierarchy == hierarchy):
                if not pt == "group_user":
                    # then root has no children yet
                    action_args = dict(
                        error="You just tried accessing a case that has \
                              no content. You have been forwarded over \
                              to the root page of the case so that you \
                              can and add some content if you wish to.")
                    messages.error(request, action_args['error'],
                                   extra_tags='rootUrlError')
                    request.path = base_url+'edit/'
                    return HttpResponseRedirect(request.path)
                else:
                    action_args = dict(
                        error="For some reason the case you tried to \
                              access does not have any content yet. \
                              Please choose another case, or alert \
                              your facilitator.")
                    messages.error(request, action_args['error'],
                                   extra_tags='rootUrlError')
                    request.path = '/'
                    return HttpResponseRedirect(request.path)
            return visit_root(self.section, self.no_root_fallback_url)
        r = self.gate_check(request.user)
        if r is not None:
            return r
        if not request.user.is_impersonate:
            self.upv = UserPageVisitor(self.section, request.user)
        return None

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

    def run_section_gatecheck(self, user, path):
        section_gatecheck = self.section.gate_check(self.request.user)
        if not section_gatecheck[0]:
            gate_section_gateblock = self.get_next_gate(self.section)
            if not gate_section_gateblock:
                block_unlocked = True
            else:
                block_unlocked = gate_section_gateblock[0].unlocked(
                    self.request.user, gate_section_gateblock[1])
                if not block_unlocked:
                    back_url = self.section.get_previous().get_absolute_url()
                    return HttpResponseRedirect(back_url)

    def check_part_path(self, casemap, hand, part):
        if part > 1 and self.request.user.profile.is_group_user():
            # set user on right path
            # get user 1st par chice p1c1 and
            # forward to that part
            p1c1 = hand.get_p1c1(casemap.value)
            p2_section = self.root.get_children()[p1c1]
            p2_url = p2_section.get_next().get_absolute_url()
            if not self.module == p2_section:
                return (True, p2_url)
            return [False, p2_url]
        return (False, False)

    def get_library_items(self, case):
        user = self.request.user
        library_items = LibraryItem.objects.filter(case=case, user=user)
        return library_items

    def notify_fascilitators(self, request, path, notification):
        user = get_object_or_404(User, pk=request.user.pk)
        socket = zmq_context.socket(zmq.REQ)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        msg = dict(user_id=user.id,
                   path=path,
                   section_pk=self.section.pk,
                   notification=notification)
        e = dict(address="%s.pages/%s/facilitator/" % 
                (settings.ZMQ_APPNAME, self.section.hierarchy.name),
                content=json.dumps(msg))
        socket.send(json.dumps(e))
        socket.recv()

    def get(self, request, path):
        # skip the first child of part if not admin
        if not request.user.is_superuser and self.section.get_depth() == 2:
            skip_url = self.section.get_next().get_absolute_url()
            return HttpResponseRedirect(skip_url)
        hierarchy = self.module.hierarchy
        case = Case.objects.get(hierarchy=hierarchy)
        uloc = UserLocation.objects.get_or_create(
            user=request.user,
            hierarchy=hierarchy)
        # handler stuff
        hand = UELCHandler.objects.get_or_create(
            hierarchy=hierarchy,
            depth=0,
            path=hierarchy.base_url)[0]
        casemap = get_user_map(hierarchy, request.user)
        part = hand.get_part_by_section(self.section)
        tree_path = self.check_part_path(casemap, hand, part)
        roots = get_root_context(self.request)

        if tree_path[0]:
            return HttpResponseRedirect(tree_path[1])

        allow_redo = False
        needs_submit = self.section.needs_submit()
        if needs_submit:
            allow_redo = self.section.allow_redo()
        if not request.user.is_impersonate:
            self.upv.visit()
        instructor_link = has_responses(self.section)
        case_quizblocks = []

        for block in self.section.pageblock_set.all():
            display_name = block.block().display_name
            # make sure that all pageblocks on page
            # have been submitted. Re: potential bug in
            # Section.submit() in Pageblock library
            if display_name == 'Decision Block':
                # is the quiz really submitted?
                # if so add yes/no to dict
                quiz = block.block()
                completed = quiz.is_submitted(quiz, request.user)
                if not completed and request.user.profile.is_group_user():
                    '''TODO: notify facilitator that student has landed on Decision Block'''
                    print "GroupUser at a Decision Block"
                    self.notify_fascilitators(request, path, 'Decision Block')
                case_quizblocks.append(dict(id=block.id,
                                            completed=completed))
            if display_name == 'Gate Block' and request.user.profile.is_group_user():
                '''TODO: notify facilitator that student has landed
                on Decision Block if not completed'''
                print "GroupUser at a GateBlock"
                self.notify_fascilitators(request, path, 'At Gate Block')
        # if gateblock is not unlocked then return to last known page
        # section.gate_check(user), doing this because hierarchy cannot
        # be "gated" because we will be skipping around depending on
        # user decisions.
        self.run_section_gatecheck(request.user, path)
        uloc[0].path = path
        uloc[0].save()
        
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
            # library_items=self.get_library_items(case),
            part=part,
            roots=roots['roots']
        )
        context.update(self.get_extra_context())
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
        # a hidden input, key "case" and csrf token
        # is included on all case_quiz submissions thus,
        # musthave more than two keys
        if len(request.POST.keys()) > 2:
            if request.POST.get('action', '') == 'reset':
                self.upv.visit(status="incomplete")
                return reset_page(self.section, request)
            # When quiz is submitted successfully, we
            # want the facilitator's dashboard to be updated
            self.notify_fascilitators(request, path, 'Decision Submitted')
            return page_submit(self.section, request)
        else:
            action_args = dict(error='error')
            messages.error(request, action_args['error'],
                           extra_tags='quizSubmissionError')
            return HttpResponseRedirect(request.path)


class UELCEditView(LoggedInFacilitatorMixin,
                   DynamicHierarchyMixin,
                   EditView):
    template_name = "pagetree/edit_page.html"
    extra_context = dict(edit_view=True)


class FacilitatorView(LoggedInFacilitatorMixin,
                      DynamicHierarchyMixin,
                      TemplateView,
                      SectionMixin):
    template_name = "pagetree/facilitator.html"
    extra_context = dict()

    def get_tree_depth(self, section):
        tree_depth = 0
        for sec in section.get_tree():
            tree_depth += 1
            if sec == section:
                return tree_depth

    def set_upv(self, user, section, status):
        try:
            upv = UserPageVisit.objects.filter(section=section, user=user)[0]
            upv.status = status
            upv.save()
        except IndexError:
            pass
        return

    def post_library_item(self, request):
        doc = request.FILES.get('doc')
        name = request.POST.get('name')
        users = request.POST.getlist('user')
        case_id = request.POST.get('case')
        case = Case.objects.get(id=case_id)
        li = LibraryItem.objects.create(doc=doc, name=name, case=case)
        li.save()
        for index in range(len(users)):
            user = User.objects.get(id=users[index])
            li.user.add(user)

    def post_library_item_delete(self, request):
        item_id = request.POST.get('library-item-id')
        li = LibraryItem.objects.get(id=item_id)
        li.delete()

    def post_library_item_edit(self, request):
        doc = request.FILES.get('doc')
        name = request.POST.get('name')
        users = request.POST.getlist('user')
        li_id = request.POST.get('library-item-id')
        li = LibraryItem.objects.filter(id=li_id)
        if doc:
            li.update(doc=doc)
        if name:
            li.update(name=name)
        li[0].user.clear()
        for index in range(len(users)):
            user = User.objects.get(id=users[index])
            li[0].user.add(user)

    def notify_group_user(self, section, user, notification):
        print "notify group user"
        print "user"
        print user
        print type(user)
        print "section"
        print section
        print type(section)
        print "section.get_absolute_url()"
        print section.get_absolute_url()
        print type(section.get_absolute_url())
        print "section.hierarchy.name"
        print section.hierarchy.name
        print type(section.hierarchy.name)
        user = get_object_or_404(User, pk=user.pk)
        socket = zmq_context.socket(zmq.REQ)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        msg = dict(user_id=user.id,
                   hierarchy=section.hierarchy.name,
                   section=section.get_absolute_url(),
                   notification=notification)
        e = dict(address="%s.pages/%s/" % 
                (settings.ZMQ_APPNAME, section.hierarchy.name, section.get_absolute_url()),
                content=json.dumps(msg))
        socket.send(json.dumps(e))
        socket.recv()

    def post_gate_action(self, request):
        user = User.objects.get(id=request.POST.get('user_id'))
        action = request.POST.get('gate-action')
        section = Section.objects.get(id=request.POST.get('section'))
        # this is second part - where we want to notify
        # the student they can proceed
        if action == 'submit':
            self.set_upv(user, section, "complete")
            self.notify_group_user(section, user, "Open Gate")
            admin_ajax_page_submit(section, user)

    def post(self, request, path):
        # posted library items
        if request.POST.get('library-item'):
            self.post_library_item(request)
        if request.POST.get('library-item-delete'):
            self.post_library_item_delete(request)
        if request.POST.get('library-item-edit'):
            self.post_library_item_edit(request)
        if request.POST.get('gate-action'):
            self.post_gate_action(request)
        return HttpResponseRedirect(request.path)

    def dispatch(self, request, *args, **kwargs):
        path = kwargs['path']
        rv = self.perform_checks(request, path)
        if rv is not None:
            return rv
        return super(FacilitatorView, self).dispatch(request, *args, **kwargs)

    def get(self, request, path):
        '''
        * get the section of each gateblock
        * determine number of levels in tree
        * determine the level and place of the section in the tree
        '''
        user = self.request.user
        section = self.get_section(path)
        root = section.hierarchy.get_root()
        roots = get_root_context(self.request)
        hierarchy = section.hierarchy
        case = Case.objects.get(hierarchy=hierarchy)
        # library_item = LibraryItem
        # library_items = LibraryItem.objects.all()
        # is there really only going to be one cohort per case?
        cohort = case.cohort.get(user_profile_cohort__user=user)
        cohort_user_profiles = cohort.user_profile_cohort.filter(
            profile_type="group_user").order_by('user__username')
        cohort_users = [profile.user for profile in cohort_user_profiles]
        gateblocks = GateBlock.objects.filter(
            pageblocks__section__hierarchy=hierarchy)
        hand = UELCHandler.objects.get_or_create(
            hierarchy=hierarchy,
            depth=0,
            path=hierarchy.base_url)[0]
        user_sections = []
        for user in cohort_users:
            um = get_user_map(hierarchy, user)
            part_usermap = hand.get_partchoice_by_usermap(um)
            gate_section = [[g.pageblock().section,
                             g,
                             g.unlocked(user, section),
                             self.get_tree_depth(g.pageblock().section),
                             g.status(user, hierarchy),
                             hand.can_show_gateblock(g.pageblock().section,
                                                     part_usermap),
                             (hand.get_part_by_section(g.pageblock().section),
                              part_usermap)]
                            for g in gateblocks]
            gate_section.sort(cmp=lambda x, y: cmp(x[3], y[3]))
            user_sections.append([user, gate_section])

        quizzes = [p.block() for p in section.pageblock_set.all()
                   if hasattr(p.block(), 'needs_submit')
                   and p.block().needs_submit()]
        context = dict(section=section,
                       quizzes=quizzes,
                       user_sections=user_sections,
                       module=section.get_module(),
                       modules=root.get_children(),
                       root=section.hierarchy.get_root(),
                       # library_item=library_item,
                       # library_items=library_items,
                       case=case,
                       websockets_base=settings.WINDSOCK_WEBSOCKETS_BASE,
                       token=gen_token(request, section.hierarchy.name),
                       roots=roots['roots']
                       )
        return render(request, self.template_name, context)


class UELCAdminCreateUserView(
        LoggedInMixinAdmin,
        TemplateView):

    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        username = request.POST.get('username', '')
        password = make_password(request.POST.get('password1', ''))
        profile_type = request.POST.get('user_profile', '')
        cohort_id = request.POST.get('cohort', '')
        if cohort_id:
            cohort = Cohort.objects.get(id=cohort_id)
        else:
            cohort = None
        user_exists = User.objects.filter(Q(username=username))
        if len(user_exists) == 0 and not profile_type == "":
            user = User.objects.create(username=username, password=password)
            UserProfile.objects.create(
                user=user,
                profile_type=profile_type,
                cohort=cohort)
            if not profile_type == "group_user":
                user.is_staff = True
            user.save()
            user.profile.set_image_upload_permissions(user)

        if len(user_exists) > 0:
            action_args = dict(
                error="That username already exists! Please enter a new one.")
            messages.error(request, action_args['error'],
                           extra_tags='createUserViewError')

        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminDeleteUserView(LoggedInMixinAdmin,
                              TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        if not user.is_superuser:
            user.delete()
        else:
            action_args = dict(
                error="Sorry, you are not permitted to \
                      delete superuser accounts.")
            messages.error(request, action_args['error'],
                           extra_tags='deleteSuperUser')
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminEditUserView(LoggedInMixinAdmin,
                            TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        username = request.POST.get('username', '')
        user_id = request.POST.get('user_id', '')
        profile = request.POST.get('profile_type', '')
        cohort_id = request.POST.get('cohort', '')
        user = User.objects.get(pk=user_id)
        if cohort_id:
            cohort = Cohort.objects.get(id=cohort_id)
        else:
            cohort = None
        user.profile.cohort = cohort
        user.profile.profile_type = profile
        if not profile == "group_user":
            user.is_staff = True
        else:
            user.is_staff = False
        user.profile.save()
        user.profile.set_image_upload_permissions(user)
        user.username = username
        user.save()
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminEditUserPassView(LoggedInMixinAdmin,
                                TemplateView):
    template_name = "pagetree/uelc_admin_user_pass_reset.html"
    extra_context = dict()

    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        form = EditUserPassForm
        return render(
            request,
            self.template_name,
            dict(edit_user_pass_form=form, user=user))

    def post(self, request, pk):
        user = User.objects.get(pk=pk)
        password = request.POST.get('newPassword1', '')
        user.set_password(password)
        user.save()
        action_args = dict(
            success="User password has been updated!")
        messages.success(request, action_args['success'],
                         extra_tags='userPasswordSuccess')
        return HttpResponseRedirect('uelcadmin')


class UELCAdminCreateHierarchyView(LoggedInMixinAdmin,
                                   TemplateView):
        template_name = "pagetree/uelc_admin.html"
        extra_context = dict()

        def post(self, request):
            name = request.POST.get('name', '')
            url = '/pages/' + name + '/'
            hier = Hierarchy.objects.filter(Q(base_url=url) | Q(name=name))

            if len(hier) > 0:
                action_args = dict(
                    error="Hierarchy exists! Please use the exisiting one,\
                          or create one with a different name and url.")
                messages.error(request, action_args['error'],
                               extra_tags='createCaseViewError')
                url = request.META['HTTP_REFERER']
                return HttpResponseRedirect(url)

            hier = Hierarchy.objects.create(
                base_url=url,
                name=name)
            hier.save()
            url = request.META['HTTP_REFERER']
            return HttpResponseRedirect(url)


class UELCAdminDeleteHierarchyView(LoggedInMixinAdmin,
                                   TemplateView):
    extra_context = dict()

    def post(self, request):
        hierarchy_id = request.POST.get('hierarchy_id')
        hier = Hierarchy.objects.get(id=hierarchy_id)
        hier.delete()
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminCaseView(LoggedInMixinAdmin,
                        TemplateView):
    template_name = "pagetree/uelc_admin_case.html"
    extra_context = dict()

    def dispatch(self, request, *args, **kwargs):
        return super(UELCAdminCaseView, self).dispatch(
            request, *args, **kwargs)

    def get_case_from_hierarchy(self, hierarchy):
        return hierarchy.case_set.first()

    def get_context_data(self, *args, **kwargs):
        path = self.request.path
        casemodel = Case
        cohortmodel = Cohort
        create_user_form = CreateUserForm
        create_hierarchy_form = CreateHierarchyForm
        users = User.objects.all().order_by('username')
        hierarchies = Hierarchy.objects.all()
        cases = Case.objects.all().order_by('name')
        cohorts = Cohort.objects.all().order_by('name')
        hierarchy_cases = [[h, self.get_case_from_hierarchy(h)]
                           for h in hierarchies]
        context = dict(users=users,
                       path=path,
                       cases=cases,
                       cohorts=cohorts,
                       casemodel=casemodel,
                       cohortmodel=cohortmodel,
                       create_user_form=create_user_form,
                       create_hierarchy_form=create_hierarchy_form,
                       hierarchy_cases=hierarchy_cases,
                       )
        return context


class UELCAdminCreateCohortView(LoggedInMixinAdmin,
                                TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        name = request.POST.get('name', '')
        try:
            cohort = Cohort.objects.create(name=name)
            cohort.save()
        except IntegrityError:
            action_args = dict(
                error="A cohort with that name already exists!\
                      Please change the name,\
                      or use the existing cohort.")
            messages.error(request, action_args['error'],
                           extra_tags='createCohortViewError')

        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminDeleteCohortView(LoggedInMixinAdmin,
                                TemplateView):
    extra_context = dict()

    def post(self, request):
        cohort_id = request.POST.get('cohort_id')
        cohort = Cohort.objects.get(id=cohort_id)
        cohort.delete()
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminEditCohortView(LoggedInMixinAdmin,
                              TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        name = request.POST.get('name', '')
        cohort_id = request.POST.get('cohort_id', '')
        user_list = request.POST.getlist('users')
        cohort_obj = Cohort.objects.get(pk=cohort_id)
        cohort_users = cohort_obj.users
        try:
            cohort_obj.name = name
            cohort_obj.save()
            user_list_objs = User.objects.filter(pk__in=user_list)
            for user in cohort_users:
                if user.id not in user_list:
                    user.profile.cohort = None
                    user.profile.save()
            for user in user_list_objs:
                user.profile.cohort = cohort_obj
                user.profile.save()
        except IntegrityError:
            action_args = dict(
                error="A cohort with that name already exists!\
                      Please change the name,\
                      or use the existing cohort.")
            messages.error(request, action_args['error'],
                           extra_tags='editCohortViewError')

        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminCreateCaseView(LoggedInMixinAdmin,
                              TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        name = request.POST.get('name', '')
        hierarchy = request.POST.get('hierarchy', '')
        cohort = request.POST.get('cohort', '')
        description = request.POST.get('description', '')
        case_exists_name = Case.objects.filter(Q(name=name))
        case_exists_hier = Case.objects.filter(Q(hierarchy=hierarchy))
        if len(case_exists_name):
            action_args = dict(
                error="Case with this name already exists!\
                      Please use existing case or rename.")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META['HTTP_REFERER']
            return HttpResponseRedirect(url)
        if len(case_exists_hier):
            action_args = dict(
                error="Case already exists! A case has already\
                      been created that is attached to the\
                      selected hierarchy. Do you need to create\
                      another hierarchy or should you use\
                      an existing case?")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META['HTTP_REFERER']
            return HttpResponseRedirect(url)
        if hierarchy == "" or cohort == "":
            action_args = dict(
                error="Please make sure a hierarchy and\
                      cohort is selected")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META['HTTP_REFERER']
            return HttpResponseRedirect(url)

        hier_obj = Hierarchy.objects.get(id=hierarchy)
        coh_obj = Cohort.objects.get(id=cohort)
        case = Case.objects.create(
            name=name,
            description=description,
            hierarchy=hier_obj)
        case.cohort.add(coh_obj)
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminDeleteCaseView(LoggedInMixinAdmin,
                              TemplateView):
    extra_context = dict()

    def post(self, request):
        case_id = request.POST.get('case_id')
        case = Case.objects.get(id=case_id)
        case.delete()
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminEditCaseView(LoggedInMixinAdmin,
                            TemplateView):
    extra_context = dict()

    def post(self, request):
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        hierarchy = request.POST.get('hierarchy', '')
        cohorts = request.POST.getlist('cohort', '')
        case_exists_name = Case.objects.filter(Q(name=name))
        case_exists_hier = Case.objects.filter(Q(hierarchy=hierarchy))
        case_id = request.POST.get('case_id', '')

        if len(case_exists_name) > 1:
            action_args = dict(
                error="Case with this name already exists!\
                      Please use existing case or rename.")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META['HTTP_REFERER']
            return HttpResponseRedirect(url)
        if len(case_exists_hier) > 1:
            action_args = dict(
                error="Case already exists! A case has already\
                      been created that is attached to the\
                      selected hierarchy. Do you need to create\
                      another hierarchy or should you use\
                      an existing case?")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META['HTTP_REFERER']
            return HttpResponseRedirect(url)
        if hierarchy == "" or cohorts == "":
            action_args = dict(
                error="Please make sure a hierarchy and\
                      cohort is selected")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            return HttpResponseRedirect('/uelcadmin/')

        coh_obj = Cohort.objects.filter(id__in=cohorts)
        case = Case.objects.get(id=case_id)
        case.name = name
        case.description = description
        case.cohort.clear()
        case.cohort.add(*coh_obj)
        case.save()
        url = request.META['HTTP_REFERER']
        return HttpResponseRedirect(url)


class UELCAdminView(LoggedInMixinAdmin,
                    TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def dispatch(self, request, *args, **kwargs):
        return super(UELCAdminView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        path = self.request.path
        casemodel = Case
        cohortmodel = Cohort
        create_user_form = CreateUserForm
        create_hierarchy_form = CreateHierarchyForm
        users = User.objects.all().order_by('username')
        hierarchies = Hierarchy.objects.all()
        cases = Case.objects.all()
        cohorts = Cohort.objects.all().order_by('name')
        context = dict(users=users,
                       path=path,
                       cases=cases,
                       cohorts=cohorts,
                       casemodel=casemodel,
                       cohortmodel=cohortmodel,
                       create_user_form=create_user_form,
                       create_hierarchy_form=create_hierarchy_form,
                       hierarchies=hierarchies,
                       )
        return context


class UELCAdminCohortView(LoggedInMixinAdmin,
                          TemplateView):
    template_name = "pagetree/uelc_admin_cohort.html"
    extra_context = dict()

    def dispatch(self, request, *args, **kwargs):
        return super(UELCAdminCohortView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        path = self.request.path
        casemodel = Case
        cohortmodel = Cohort
        create_user_form = CreateUserForm
        create_hierarchy_form = CreateHierarchyForm
        users = User.objects.all().order_by('username')
        hierarchies = Hierarchy.objects.all()
        cases = Case.objects.all()
        cohorts = Cohort.objects.all().order_by('name')
        context = dict(users=users,
                       path=path,
                       cases=cases,
                       cohorts=cohorts,
                       casemodel=casemodel,
                       cohortmodel=cohortmodel,
                       create_user_form=create_user_form,
                       create_hierarchy_form=create_hierarchy_form,
                       hierarchies=hierarchies,
                       )
        return context


class UELCAdminUserView(LoggedInMixinAdmin,
                        TemplateView):
    template_name = "pagetree/uelc_admin_user.html"
    extra_context = dict()

    def dispatch(self, request, *args, **kwargs):
        return super(UELCAdminUserView, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        path = self.request.path
        casemodel = Case
        cohortmodel = Cohort
        create_user_form = CreateUserForm
        create_hierarchy_form = CreateHierarchyForm
        users = User.objects.all().order_by('username')
        hierarchies = Hierarchy.objects.all()
        cases = Case.objects.all()
        cohorts = Cohort.objects.all().order_by('name')
        context = dict(users=users,
                       path=path,
                       cases=cases,
                       cohorts=cohorts,
                       casemodel=casemodel,
                       cohortmodel=cohortmodel,
                       create_user_form=create_user_form,
                       create_hierarchy_form=create_hierarchy_form,
                       hierarchies=hierarchies,
                       )
        return context


class AddCaseAnswerToQuestionView(View):
    template_name = 'quizblock/edit_question.html'

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        form = CaseAnswerForm()
        return render(
            request,
            self.template_name,
            dict(question=question, case_answer_form=form))

    def post(self, request, pk):
        '''This solution assumes that the user cannot submit
        multiple responses - it does not check to see if an answer is
        already associated with the question...'''
        question = get_object_or_404(Question, pk=pk)
        value = request.POST.get('value', "")
        title = request.POST.get('title', "")
        if title == "":
            form = CaseAnswerForm(request.POST)
            return render(
                request,
                self.template_name,
                dict(question=question, case_answer_form=form))
        description = request.POST.get('description', "")
        if value:
            inty = int(value)
        elif request.POST.get('answer-value'):
            inty = request.POST.get('answer-value')
        else:
            inty = 0
        if not title:
            title = request.POST.get('case-answer-title', "")
            if not title:
                title = '---'
        if not description:
            description = request.POST.get('case-answer-description', "")
            if not description:
                description = '----'
        ans = Answer.objects.create(
            question=question,
            value=inty)
        case_ans = CaseAnswer.objects.create(
            answer=ans,
            title=title,
            description=description)
        case_ans.save()
        return render(
            request,
            self.template_name,
            dict(question=question, case_answer_form=CaseAnswerForm()))


class EditCaseAnswerView(View):
    template_name = 'quizblock/edit_answer.html'

    def get(self, request, pk):
        case_answer = get_object_or_404(CaseAnswer, pk=pk)
        form = CaseAnswerForm(initial={'value': case_answer.answer.value,
                                       'title': case_answer.title,
                                       'description': case_answer.description})
        return render(
            request,
            self.template_name,
            dict(case_answer_form=form, case_answer=case_answer))

    def post(self, request, pk):
        case_answer = get_object_or_404(CaseAnswer, pk=pk)
        form = CaseAnswerForm(request.POST)
        if form.is_valid():
            case_answer.title = request.POST.get('title')
            case_answer.description = request.POST.get('description')
            case_answer.save()
            ans = Answer.objects.get(caseanswer=case_answer.pk)
            ans.value = int(request.POST.get('value'))
            ans.save()
            return HttpResponseRedirect(reverse("edit-case-answer",
                                                args=[case_answer.id]))
        return render(
            request,
            self.template_name,
            dict(case_answer_form=form, case_answer=case_answer))


class DeleteCaseAnswerView(LoggedInMixinAdmin,
                           View):
    '''I am doing a regular view instead of a delete view,
    because the delete view will only delete the caseanswer,
    we want to delete the case answer and corresponding answer'''

    def post(self, request, pk):
        case_answer = get_object_or_404(CaseAnswer, pk=pk)
        question = case_answer.answer.question.id
        case_answer.answer.delete()
        case_answer.delete()
        return HttpResponseRedirect(reverse(
            "add-case-answer-to-question", args=[question]))
