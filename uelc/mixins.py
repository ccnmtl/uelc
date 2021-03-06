from django.contrib.auth.decorators import login_required, user_passes_test
from django.http.response import (
    HttpResponseForbidden, HttpResponseNotFound
)
from django.utils.decorators import method_decorator
from pagetree.helpers import get_section_from_path
from pagetree.models import Hierarchy
from uelc.main.helper_functions import get_cases


class LoggedInMixinAdmin(object):
    @method_decorator(user_passes_test(
        lambda u: not u.is_anonymous() and u.profile.profile_type == "admin"))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinAdmin, self).dispatch(*args, **kwargs)


class LoggedInFacilitatorMixin(object):
    @method_decorator(user_passes_test(
        lambda u: not u.is_anonymous() and
        not u.profile.profile_type == "group_user"))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInFacilitatorMixin, self).dispatch(*args, **kwargs)


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


class DynamicHierarchyMixin(object):
    def dispatch(self, *args, **kwargs):
        slugname = kwargs.pop('hierarchy_name', None)
        if slugname is None:
            return HttpResponseNotFound('hierarchy_name is None')
        url = '/pages/{}/'.format(slugname)
        try:
            h = Hierarchy.objects.get(base_url=url)
            self.hierarchy_base = h.base_url
            self.hierarchy_name = h.name
        except Hierarchy.DoesNotExist:
            msg = "No hierarchy with url %s found" % url
            return HttpResponseNotFound(msg)

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
        return HttpResponseForbidden("you don't have permission")
