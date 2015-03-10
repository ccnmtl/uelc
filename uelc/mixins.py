from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from pagetree.helpers import get_section_from_path


class LoggedInMixinSuperuser(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super(LoggedInMixinSuperuser, self).dispatch(*args, **kwargs)


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
