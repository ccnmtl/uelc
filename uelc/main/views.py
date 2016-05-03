import json
import zmq
import urlparse
import sys
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView, View
from pagetree.generic.views import (
    PageView, EditView, UserPageVisitor, CloneHierarchyView
)
from pagetree.models import UserPageVisit, Hierarchy, Section, UserLocation
from quizblock.models import Question, Answer
from gate_block.models import GateBlock, SectionSubmission, GateSubmission
from uelc.main.helper_functions import (
    get_root_context, get_user_map, visit_root, gen_group_token,
    has_responses, reset_page, page_submit, admin_ajax_page_submit,
    gen_token, get_user_last_location
)
from uelc.mixins import (
    LoggedInMixin, LoggedInFacilitatorMixin,
    SectionMixin, LoggedInMixinAdmin, DynamicHierarchyMixin,
    RestrictedModuleMixin)
from uelc.main.models import (
    Cohort, UserProfile, Case, CaseMap,
    CaseAnswer, UELCHandler,
    LibraryItem)
from uelc.main.forms import (
    CreateUserForm, CreateHierarchyForm,
    EditUserPassForm, CaseAnswerForm, UELCCloneHierarchyForm
)

from curveball.models import Curveball, CurveballBlock

zmq_context = zmq.Context()


def behave_socket_open(socket):
    """Make the socket behave-compatible. :-/"""
    if sys.argv[1:2] == ['behave']:
        socket.linger = 0


def behave_socket_recv(socket):
    """ZMQ socket.recv() that doesn't hang on behave"""
    # TODO: behave hangs on socket.recv()
    if sys.argv[1:2] == ['behave']:
        try:
            socket.recv(zmq.NOBLOCK)
        except zmq.ZMQError:
            pass
    else:
        socket.recv()


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
            return self.root_section_check(request, ns, ns_hierarchy,
                                           hierarchy, base_url, pt)

        if self.section == self.module and pt == "group_user":
            '''forward them to the home page of the part'''

            nxt_path = self.get_path_of_next_section()

            ns_path = urlparse.urljoin(
                hierarchy.base_url,
                nxt_path)

            return HttpResponseRedirect(ns_path)

        r = self.gate_check(request.user)
        if r is not None:
            return r
        if not request.user.is_impersonate:
            self.upv = UserPageVisitor(self.section, request.user)
        return None

    def root_section_check(self, request, ns, ns_hierarchy,
                           hierarchy, base_url, pt):
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

    def get_path_of_next_section(self):
        nxt = self.section.get_next()
        if nxt is not None:
            return nxt.get_path()
        return self.section.get_path()

    def iterate_blocks(self, section):
        for block in section.pageblock_set.all():
            block_obj = block.block()
            if (hasattr(block_obj, 'needs_submit') and
                    block_obj.display_name == 'Gate Block'):
                return block_obj
        return False

    def get_next_gate(self, section):
        block = self.iterate_blocks(section)
        last_sibling = self.section.get_last_sibling()
        if block:
            return (block, section)
        block = self.iterate_blocks(last_sibling)
        if block:
            return (block, last_sibling)
        return False

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

    def notify_facilitators(self, request, path, notification):
        user = get_object_or_404(User, pk=request.user.pk)
        socket = zmq_context.socket(zmq.REQ)
        behave_socket_open(socket)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        msg = dict()

        if(notification['message'] == 'Decision Submitted'):
            cb = self.section.get_next()
            if (hasattr(cb, 'display_name') and
                    cb.display_name == "Curveball Block"):
                """We must ask the facilitator
                to select a curveball for the group"""
                facil_msg = "please select a curvball"
            else:
                facil_msg = "the group has made a decision"
            msg = dict(
                userId=user.id,
                path=path,
                sectionPk=self.section.pk,
                notification=notification,
                facil_msg=facil_msg)

        elif(notification['message'] == 'At Gate Block'):
            msg = dict(
                userId=user.id,
                path=path,
                sectionPk=self.section.pk,
                notification=notification)

        e = dict(address="%s.pages/%s/facilitator/" %
                 (settings.ZMQ_APPNAME, self.section.hierarchy.name),
                 content=json.dumps(msg))

        socket.send(json.dumps(e))
        behave_socket_recv(socket)

    def check_user(self, request, path):
        if not request.user.is_superuser and self.section.get_depth() == 2:
            skip_url = self.section.get_next().get_absolute_url()
            return HttpResponseRedirect(skip_url)

    def _get_section_submission(self, user):
        try:
            return SectionSubmission.objects.get(
                section=self.section,
                user=user)
        except SectionSubmission.DoesNotExist:
            return None

    def _get_gate_submission(self, user):
        try:
            return GateSubmission.objects.filter(
                section=self.section,
                gate_user=user).latest('submitted')
        except GateSubmission.DoesNotExist:
            return None

    def get(self, request, path):
        self.check_user(request, path)
        # skip the first child of part if not admin
        hierarchy = self.module.hierarchy
        case = Case.objects.get(hierarchy=hierarchy)
        uloc = UserLocation.objects.get_or_create(
            user=request.user,
            hierarchy=hierarchy)
        section_submission = self._get_section_submission(request.user)
        gate_submission = self._get_gate_submission(request.user)

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

        self.upv.visit()
        instructor_link = has_responses(self.section)
        decision_blocks = []
        gate_blocks = []
        for block in self.section.pageblock_set.all():
            b = block.block()
            display_name = b.display_name
            grp_usr = request.user.profile.is_group_user()
            # make sure that all pageblocks on page
            # have been submitted. Re: potential bug in
            # Section.submit() in Pageblock library
            decision_blocks = ensure_decision_block_submitted(
                b, display_name, request.user, block,
                decision_blocks)
            if display_name == 'Gate Block' and grp_usr:
                gate_blocks.append(dict(id=block.id))
                notification = dict(
                    data='',
                    message='At Gate Block')
                self.notify_facilitators(request, path, notification)
        # if gateblock is not unlocked then return to last known page
        # section.gate_check(user), doing this because hierarchy cannot
        # be "gated" because we will be skipping around depending on
        # user decisions.
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
            decision_blocks=decision_blocks,
            gate_blocks=gate_blocks,
            gate_submission=gate_submission,
            section_submission=section_submission,
            casemap=casemap,
            part=part,
            websockets_base=settings.WINDSOCK_WEBSOCKETS_BASE,
            token=gen_group_token(request, self.section.pk),
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
        if len(request.POST.keys()) < 3:
            messages.error(request, 'error',
                           extra_tags='quizSubmissionError')
            return HttpResponseRedirect(request.path)

        if request.POST.get('action', '') == 'reset':
            self.upv.visit(status="incomplete")
            return reset_page(self.section, request)

        # When quiz is submitted successfully, we
        # want the facilitator's dashboard to be updated
        # Will need to get the correct curveball choices to send
        # facilitator
        post_keys = request.POST.keys()
        q_id = None
        q_answer_set = None
        answer_value = None
        for k in post_keys:
            k_split = k.split('question')
            if len(k_split) > 1:
                q_id = k_split[1]
                answer_value = request.POST.get(k)
                q = Question.objects.get(id=q_id)
                q_answer_set = q.answer_set.all()
        answer_title = get_answer_title(q_answer_set, answer_value)
        notification = dict(
            data=answer_title,
            message='Decision Submitted')
        self.notify_facilitators(request, path, notification)
        return page_submit(self.section, request)


def get_answer_title(q_answer_set, answer_value):
    answer_title = None
    if q_answer_set:
        for an in q_answer_set:
            if an.value == answer_value:
                ca = CaseAnswer.objects.get(answer=an)
                answer_title = ca.display_title()
    return answer_title


def ensure_decision_block_submitted(b, display_name, user, block,
                                    decision_blocks):
    if display_name == 'Decision Block':
        # is the quiz really submitted?
        # if so add yes/no to dict
        quiz = b
        completed = quiz.is_submitted(quiz, user)
        decision_blocks.append(dict(id=block.id,
                                    completed=completed))
    return decision_blocks


class SubmitSectionView(LoggedInMixin,
                        TemplateView):
    extra_context = dict()
    template_name = 'pagetree/page.html'

    def notify_facilitators(self, request, section, notification):
        socket = zmq_context.socket(zmq.REQ)
        behave_socket_open(socket)
        socket.connect(settings.WINDSOCK_BROKER_URL)

        msg = dict(
            userId=request.user.id,
            sectionPk=section.pk,
            notification=notification)

        e = dict(address="%s.pages/%s/facilitator/" %
                 (settings.ZMQ_APPNAME, section.hierarchy.name),
                 content=json.dumps(msg))

        socket.send(json.dumps(e))
        behave_socket_recv(socket)

    def post(self, request):
        user = request.user
        section_id = request.POST.get('section', '')
        section = Section.objects.get(id=section_id)
        SectionSubmission.objects.get_or_create(section=section, user=user)

        notification = dict(
            data='',
            message='Section Submitted')
        self.notify_facilitators(request, section, notification)
        return HttpResponse('Success')


class UELCEditView(LoggedInFacilitatorMixin,
                   DynamicHierarchyMixin,
                   EditView):
    template_name = "pagetree/edit_page.html"
    extra_context = dict(edit_view=True)


class FacilitatorView(LoggedInFacilitatorMixin,
                      DynamicHierarchyMixin,
                      SectionMixin,
                      TemplateView):
    template_name = "pagetree/facilitator.html"
    extra_context = dict()

    def get_tree_depth(self, section):
        for idx, sec in enumerate(section.get_tree()):
            if sec == section:
                return idx

    def set_upv(self, user, section, status):
        upv = UserPageVisit.objects.filter(section=section, user=user).first()
        try:
            upv.status = status
            upv.save()
        except AttributeError:
            pass

    def post_library_item(self, request):
        doc = request.FILES.get('doc')
        name = request.POST.get('name')
        users = request.POST.getlist('user')
        case_id = request.POST.get('case')
        case = Case.objects.get(id=case_id)
        li = LibraryItem.objects.create(doc=doc, name=name, case=case)
        li.save()
        user_objs = User.objects.filter(id__in=users)
        for user in user_objs:
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
        li.first().user.clear()
        user_objs = User.objects.filter(id__in=users)
        for user in user_objs:
            li.first().user.add(user)

    def notify_group_user(self, section, user, notification):
        socket = zmq_context.socket(zmq.REQ)
        behave_socket_open(socket)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        msg = dict(userId=user.id,
                   username=user.username,
                   hierarchy=section.hierarchy.name,
                   nextUrl=section.get_next().get_absolute_url(),
                   section=section.pk,
                   notification=notification)
        e = dict(address="%s.%d" %
                 (settings.ZMQ_APPNAME, section.pk),
                 content=json.dumps(msg))
        socket.send(json.dumps(e))
        behave_socket_recv(socket)

    def notify_facilitator(self, request, section, user, msg):
        socket = zmq_context.socket(zmq.REQ)
        behave_socket_open(socket)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        notification = dict(
            data='',
            message=msg)
        msg = dict(
            userId=user.id,
            sectionPk=section.pk,
            notification=notification)

        e = dict(address="%s.pages/%s/facilitator/" %
                 (settings.ZMQ_APPNAME, section.hierarchy.name),
                 content=json.dumps(msg))

        socket.send(json.dumps(e))
        behave_socket_recv(socket)

    def post_curveball_select(self, request):
        '''Show the facilitator their choices for the curveball,
        facilitator selects what curveball the group will see'''
        group_user = User.objects.get(id=request.POST.get('user_id'))
        cb_id = request.POST.get('curveball')
        cb = Curveball.objects.get(id=cb_id)

        cb_block_id = request.POST.get('curveball-block-id')
        cb_block = CurveballBlock.objects.get(id=cb_block_id)

        '''Now we decide which curveball is visible when the gate unlocks'''
        cb_block.create_submission(group_user, cb)

    def post_gate_action(self, request):
        user = User.objects.get(id=request.POST.get('user_id'))
        action = request.POST.get('gate-action')
        section = Section.objects.get(id=request.POST.get('section'))
        # this is second part - where we want to notify
        # the student they can proceed
        if action == 'submit':
            self.set_upv(user, section, "complete")
            self.notify_group_user(section, user, "Open Gate")
            self.notify_facilitator(request, section, user, "Open Gate")
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
        if request.POST.get('curveball-select'):
            self.post_curveball_select(request)
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
            user_last_location = get_user_last_location(user, hierarchy)

            um = get_user_map(hierarchy, user)
            part_usermap = hand.get_partchoice_by_usermap(um)

            gate_section = []
            uloc = UserLocation.objects.get_or_create(
                user=user,
                hierarchy=hierarchy)

            for g in gateblocks:
                gateblock_section = g.pageblock().section
                pageblocks = gateblock_section.pageblock_set.all()
                part = hand.get_part_by_section(gateblock_section)
                gate_section.append([
                    gateblock_section,
                    g,
                    g.unlocked(user, section),
                    self.get_tree_depth(gateblock_section),
                    g.status(
                        gateblock_section,
                        user, hierarchy,
                        uloc[0],
                        pageblocks),
                    hand.can_show_gateblock(gateblock_section,
                                            part_usermap,
                                            part),
                    (part, part_usermap),
                    hand.is_curveball(gateblock_section, pageblocks),
                    hand.is_decision_block(
                        gateblock_section,
                        user,
                        pageblocks),
                    hand.is_next_curveball(gateblock_section)
                ])

            gate_section.sort(cmp=lambda x, y: cmp(x[3], y[3]))
            user_sections.append([user, gate_section, user_last_location])

        quizzes = []
        for p in section.pageblock_set.all():
            block_obj = p.block()
            if hasattr(block_obj, 'needs_submit') and block_obj.needs_submit():
                quizzes.append(block_obj)
        context = dict(
            is_facilitator_view=True,
            section=section,
            quizzes=quizzes,
            user_sections=user_sections,
            module=section.get_module(),
            modules=root.get_children(),
            root=section.hierarchy.get_root(),
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
        profile_type = request.POST.get('user_profile', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        error = self.check_for_errors(username, password1, password2)
        if error is None and profile_type != '':
            cohort = self.get_cohort_or_none(request)

            user = User.objects.create_user(
                username=username, password=password1)
            UserProfile.objects.create(
                user=user,
                profile_type=profile_type,
                cohort=cohort)

            if profile_type != "group_user":
                user.is_staff = True

            user.save()
            user.profile.set_image_upload_permissions(user)

        if error is not None:
            messages.error(request, error, extra_tags='createUserViewError')

        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)

    def check_for_errors(self, username, password1, password2):
        user_filter = User.objects.filter(username=username)
        error = None
        if user_filter.exists():
            error = 'That username already exists! Please enter a new one.'
        elif len(username) > 30:
            error = 'The username needs to be 30 characters or fewer',
        elif password1 == '':
            error = 'The password is blank'
        elif password1 != password2:
            error = 'The passwords don\'t match.'
        return error

    def get_cohort_or_none(self, request):
        cohort_id = request.POST.get('cohort', '')
        if cohort_id:
            return Cohort.objects.get(id=cohort_id)
        return None


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
        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)


class UELCAdminEditUserView(LoggedInMixinAdmin,
                            TemplateView):
    template_name = "pagetree/uelc_admin.html"
    extra_context = dict()

    def post(self, request):
        url = request.META.get('HTTP_REFERER')

        username = request.POST.get('username', '')
        if len(username) > 30:
            messages.error(
                request,
                'The username needs to be 30 characters or fewer.',
                extra_tags='createUserViewError')
            return HttpResponseRedirect(url)

        user_id = request.POST.get('user_id', '')
        profile = request.POST.get('profile_type', '')
        cohort_id = request.POST.get('cohort', '')

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(
                request,
                'User not found.',
                extra_tags='createUserViewError')
            return HttpResponseRedirect(url)

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
        return HttpResponseRedirect(reverse('uelcadmin'))


class UELCAdminCreateHierarchyView(LoggedInMixinAdmin,
                                   TemplateView):
        template_name = "pagetree/uelc_admin.html"
        extra_context = dict()

        def post(self, request):
            name = request.POST.get('name', '')
            url = '/pages/' + name + '/'
            hier = Hierarchy.objects.filter(Q(base_url=url) | Q(name=name))

            if hier.exists():
                action_args = dict(
                    error="Hierarchy exists! Please use the exisiting one,\
                          or create one with a different name and url.")
                messages.error(request, action_args['error'],
                               extra_tags='createCaseViewError')
                url = request.META.get('HTTP_REFERER')
                return HttpResponseRedirect(url)

            hier = Hierarchy.objects.create(
                base_url=url,
                name=name)
            hier.save()
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)


class UELCAdminDeleteHierarchyView(LoggedInMixinAdmin,
                                   TemplateView):
    extra_context = dict()

    def post(self, request):
        hierarchy_id = request.POST.get('hierarchy_id')
        hier = Hierarchy.objects.get(id=hierarchy_id)
        hier.delete()
        url = request.META.get('HTTP_REFERER')
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

        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)


class UELCAdminDeleteCohortView(LoggedInMixinAdmin,
                                TemplateView):
    extra_context = dict()

    def post(self, request):
        cohort_id = request.POST.get('cohort_id')
        cohort = Cohort.objects.get(id=cohort_id)

        # make sure that the userprofile cohort
        # is set to None to prevent the userprofile
        # cohort being Null
        for user in cohort.users:
            user.profile.cohort = None
            user.profile.save()
        cohort.delete()
        url = request.META.get('HTTP_REFERER')
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

        url = request.META.get('HTTP_REFERER')
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
        case_exists_name = Case.objects.filter(name=name)
        case_exists_hier = Case.objects.filter(hierarchy=hierarchy)
        if case_exists_name.exists():
            action_args = dict(
                error="Case with this name already exists!\
                      Please use existing case or rename.")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
        if case_exists_hier.exists():
            action_args = dict(
                error="Case already exists! A case has already\
                      been created that is attached to the\
                      selected hierarchy. Do you need to create\
                      another hierarchy or should you use\
                      an existing case?")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
        if hierarchy == "" or cohort == "":
            action_args = dict(
                error="Please make sure a hierarchy and\
                      cohort is selected")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)

        hier_obj = Hierarchy.objects.get(id=hierarchy)
        coh_obj = Cohort.objects.get(id=cohort)
        case = Case.objects.create(
            name=name,
            description=description,
            hierarchy=hier_obj)
        case.cohort.add(coh_obj)
        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)


class UELCAdminDeleteCaseView(LoggedInMixinAdmin,
                              TemplateView):
    extra_context = dict()

    def post(self, request):
        case_id = request.POST.get('case_id')
        case = Case.objects.get(id=case_id)
        case.delete()
        url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(url)


class UELCAdminEditCaseView(LoggedInMixinAdmin,
                            TemplateView):
    extra_context = dict()

    def post(self, request):
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        hierarchy = request.POST.get('hierarchy', '')
        cohorts = request.POST.getlist('cohort', '')
        case_exists_name = Case.objects.filter(name=name)
        case_exists_hier = Case.objects.filter(hierarchy=hierarchy)
        case_id = request.POST.get('case_id', '')

        if case_exists_name.count() > 1:
            action_args = dict(
                error="Case with this name already exists!\
                      Please use existing case or rename.")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
        if case_exists_hier.count() > 1:
            action_args = dict(
                error="Case already exists! A case has already\
                      been created that is attached to the\
                      selected hierarchy. Do you need to create\
                      another hierarchy or should you use\
                      an existing case?")
            messages.error(request, action_args['error'],
                           extra_tags='createCaseViewError')
            url = request.META.get('HTTP_REFERER')
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
        url = request.META.get('HTTP_REFERER')
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

        inty = self.get_inty(value, request)

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

    def get_inty(self, value, request):
        if value:
            return int(value)
        elif request.POST.get('answer-value'):
            return request.POST.get('answer-value')
        else:
            return 0


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


class CloneHierarchyWithCasesView(CloneHierarchyView):
    form_class = UELCCloneHierarchyForm

    def form_valid(self, form):
        rv = super(CloneHierarchyWithCasesView, self).form_valid(form)
        name = form.cleaned_data['name']

        clone = Hierarchy.objects.get(name=name)
        clone.get_root().clear_tree_cache()
        hierarchy_id = self.kwargs.get('hierarchy_id')
        original = get_object_or_404(Hierarchy, pk=hierarchy_id)
        original_cases = Case.objects.filter(hierarchy=original)

        for case in original_cases:
            # Clone the original hierarchy's cases
            newcase = Case.objects.create(
                hierarchy=clone,
                name=name,
                description=case.description)
            for cohort in case.cohort.all():
                newcase.cohort.add(cohort)
            for casemap in CaseMap.objects.filter(case=case):
                CaseMap.objects.get_or_create(
                    case=newcase,
                    user=casemap.user)

        return rv
