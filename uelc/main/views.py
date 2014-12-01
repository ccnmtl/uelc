from django.views.generic.base import TemplateView
from pagetree.generic.views import PageView, EditView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from pagetree.models import UserPageVisit, Hierarchy
from pagetree.generic.views import generic_instructor_page, generic_edit_page
from django.shortcuts import render
from django.contrib.auth.models import User
from uelc.main.models import Case
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http.response import HttpResponseNotFound


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)


class LoggedInMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixin, self).dispatch(*args, **kwargs)


def get_cases(request):
    try:
        user = User.objects.get(id=request.user.id)
        cohorts = user.profile.cohorts
        cohort_names = cohorts.split(', ')
        cases = Case.objects.filter(cohort__name__in=cohort_names)
        return cases
    except ObjectDoesNotExist:
        return


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


class UELCPageView(LoggedInMixin,
                   DynamicHierarchyMixin,
                   RestrictedModuleMixin,
                   PageView):
    template_name = "pagetree/page.html"
    gated = True

    def get(self, request, path):
        allow_redo = False
        needs_submit = self.section.needs_submit()
        if needs_submit:
            allow_redo = self.section.allow_redo()
        self.upv.visit()
        instructor_link = has_responses(self.section)
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


class UELCEditView(LoggedInMixinSuperuser,
                   DynamicHierarchyMixin,
                   EditView):
    template_name = "pagetree/edit_page.html"


@login_required
def pages_save_edit(request, hierarchy_name, path):
    # do auth on the request if you need the user to be logged in
    # or only want some particular users to be able to get here
    return generic_edit_page(request, path, hierarchy=hierarchy_name)


@login_required
def instructor_page(request, hierarchy_name, path):
    return generic_instructor_page(request, path, hierarchy=hierarchy_name)
