from django.test import TestCase
# from django.test.client import Client
from pagetree.helpers import get_hierarchy
from factories import GroupUpFactory, AdminUpFactory, \
    CaseFactory, CohortFactory, UELCModuleFactory
from pagetree.tests.factories import ModuleFactory
from quizblock.tests.test_models import FakeReq
from uelc.main.models import CaseQuiz
from uelc.main.helper_functions import (
    admin_ajax_page_submit, admin_ajax_reset_page,
    page_submit, get_root_context, has_responses)


class TestHelperFunctions(TestCase):

    def setUp(self):
        UELCModuleFactory("main", "/pages/main/")
        self.hierarchy = get_hierarchy(name='main')
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.grp_usr_profile = GroupUpFactory()

    def test_admin_ajax_page_submit(self):
        '''Prior to running method it should be false no?'''
        self.assertFalse(self.section.unlocked(self.grp_usr_profile.user))
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        self.assertTrue(self.section.unlocked(self.grp_usr_profile.user))

    def test_admin_ajax_reset_page(self):
        self.assertTrue(self.section.unlocked(self.grp_usr_profile.user))
        admin_ajax_reset_page(self.section, self.grp_usr_profile.user)
        self.assertFalse(self.section.unlocked(self.grp_usr_profile.user))

    def test_page_submit(self):
        pass

    def test_reset_page(self):
        pass

    def test_get_root_context(self):
        pass

    def test_has_responses(self):
        pass





# def admin_ajax_reset_page(section, user):
# 48    0        for block in section.pageblock_set.all():
# 49    0            if block.block().display_name == "Gate Block":
# 50    0                gso = GateSubmission.objects.filter(
# 51                        section=section,
# 52                        gate_user_id=user.id)
# 53    0                gso.delete()
# 54    0        section.reset(user)
# 55        
# 56        
# 57    1    def page_submit(section, request):
# 58    0        proceed = section.submit(request.POST, request.user)
# 59    0        if proceed:
# 60    0            next_section = section.get_next()
# 61    0            if next_section:
# 62    0                return HttpResponseRedirect(next_section.get_absolute_url())
# 63                else:
# 64                    # they are on the "last" section of the site
# 65                    # all we can really do is send them back to this page
# 66    0                return HttpResponseRedirect(section.get_absolute_url())
# 67            # giving them feedback before they proceed
# 68    0        return HttpResponseRedirect(section.get_absolute_url())
# 69        
# 70        
# 71    1    def reset_page(section, request):
# 72    0        section.reset(request.user)
# 73    0        return HttpResponseRedirect(section.get_absolute_url())
# 74        
# 75        
# 76    1    def get_root_context(request):
# 77    1        context = dict()
# 78    1        try:
# 79    1            cases = get_cases(request)
# 80    1            if cases:
# 81    0                roots = [(case.hierarchy.get_absolute_url(),
# 82                              case.hierarchy.name)
# 83                             for case in cases]
# 84    0                context = dict(roots=roots)
# 85    0        except ObjectDoesNotExist:
# 86    0            pass
# 87    1        return context
# 88def has_responses(section):
# 99    0        quizzes = [p.block() for p in section.pageblock_set.all()
# 100                       if hasattr(p.block(), 'needs_submit')
# 101                       and p.block().needs_submit()]
# 102    0        return quizzes != []