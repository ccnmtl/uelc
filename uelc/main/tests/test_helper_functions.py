from django.test import TestCase, RequestFactory
from pagetree.models import Hierarchy, UserLocation, Section
from quizblock.tests.test_models import FakeReq

from gate_block.models import GateBlock
from uelc.main.helper_functions import (
    admin_ajax_page_submit, admin_ajax_reset_page,
    page_submit, reset_page, get_user_map, get_user_last_location,
    gen_fac_token, gen_group_token
)
from uelc.main.models import CaseQuiz, Cohort, Case, CaseMap
from uelc.main.tests.factories import (
    CaseFactory, CaseMapFactory, GroupUpFactory, GroupUserFactory,
    HierarchyFactory, UELCModuleFactory)


class TestSubmissionResetFunctions(TestCase):

    def setUp(self):
        self.hierarchy = HierarchyFactory(name="main", base_url="/pages/main/")
        self.root = self.hierarchy.get_root()
        self.r = FakeReq()
        self.cohort = Cohort.objects.create(name="main_cohort")
        self.case = Case.objects.create(
            name="main_case",
            hierarchy=self.hierarchy)
        self.r.POST = {'description': 'description', 'rhetorical': False,
                       'allow_redo': True, 'show_submit_state': False}
        self.casequiz = CaseQuiz.create(self.r)
        self.root.add_pageblock_from_dict(self.casequiz.as_dict())
        self.section = self.hierarchy.get_root().get_first_leaf()
        self.section.add_pageblock_from_dict(self.casequiz.as_dict())
        self.section.append_pageblock('', '', self.casequiz)
        self.gate_block = GateBlock.objects.create()
        self.section.append_pageblock('', '', self.gate_block)
        self.grp_usr_profile = GroupUpFactory()

    def test_admin_ajax_page_submit(self):
        '''There are two unlock methods - one in
        CaseQuiz and another in GateBlock'''
        self.assertFalse(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))
        self.assertFalse(
            self.casequiz.unlocked(self.grp_usr_profile.user, self.section))
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        '''To test CaseQuiz unlocked we need to create a user visit...'''
        self.assertTrue(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))

    def test_admin_ajax_reset_page(self):
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        self.assertTrue(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))
        admin_ajax_reset_page(self.section, self.grp_usr_profile.user)
        self.assertFalse(self.gate_block.unlocked(
            self.grp_usr_profile.user, self.section))

    def test_reset_page(self):
        self.otr = FakeReq()
        self.otr.user = self.grp_usr_profile.user
        admin_ajax_page_submit(self.section, self.grp_usr_profile.user)
        reset_page(self.section, self.otr)
        self.assertFalse(
            self.gate_block.unlocked(self.grp_usr_profile.user, self.section))


class TestPageSubmitFunction(TestCase):

    def setUp(self):
        self.hierarchy = HierarchyFactory(name="main", base_url="/pages/main/")
        self.root = self.hierarchy.get_root()
        self.root.add_child_section_from_dict(
            {'label': "One", 'slug': "one",
             'children': [{'label': "Three", 'slug': "introduction"}]})
        self.root.add_child_section_from_dict({'label': "Two", 'slug': "two"})
        blocks = [{'label': 'Welcome UELC',
                   'css_extra': '',
                   'block_type': 'Test Block',
                   'body': 'You should now use the edit link to add content'}]
        self.root.add_child_section_from_dict({'label': 'Four', 'slug': 'four',
                                               'pageblocks': blocks})
        self.section = self.root.get_first_child()
        self.last_section = self.root.get_last_child()
        self.otr = FakeReq()
        self.otr.POST = {'description': 'description', 'rhetorical': False,
                         'allow_redo': True, 'show_submit_state': False}
        self.grp_usr_profile = GroupUpFactory()
        self.otr.user = self.grp_usr_profile.user

    def test_page_submit(self):
        self.first_request = page_submit(self.section, self.otr)
        self.assertEqual(
            self.first_request['Location'],
            self.section.get_next().get_absolute_url())
        self.last_request = page_submit(self.last_section, self.otr)
        self.assertEqual(
            self.last_request['Location'],
            self.last_section.get_absolute_url())


class TestGetUserMap(TestCase):
    def test_get_user_map_already_created(self):
        cm = CaseMapFactory()
        self.assertEqual(get_user_map(cm.case.hierarchy, cm.user), cm)

    def test_get_user_map_not_created(self):
        case = CaseFactory()
        user = GroupUserFactory()

        self.assertEqual(CaseMap.objects.count(), 0)
        get_user_map(case.hierarchy, user)
        self.assertEqual(CaseMap.objects.count(), 1)

    def test_get_user_map_multiple_matching_casemaps(self):
        case = CaseFactory()
        user = GroupUserFactory()
        cm1 = CaseMapFactory(case=case, user=user)
        CaseMapFactory(case=case, user=user)

        self.assertEqual(CaseMap.objects.count(), 2)
        self.assertEqual(get_user_map(case.hierarchy, user), cm1)
        self.assertEqual(CaseMap.objects.count(), 2)


class TestUserLastLocation(TestCase):

    def setUp(self):
        UELCModuleFactory()
        self.h = Hierarchy.objects.get(name='case-test')

    def test_get_user_last_location(self):
        user = GroupUpFactory().user
        self.assertIsNone(get_user_last_location(user, self.h))

        ul = UserLocation.objects.create(
            user=user, hierarchy=self.h, path='part-1/home/')

        self.assertEquals(get_user_last_location(user, self.h),
                          Section.objects.get(slug='home'))

        # invalid path -- the UserLocation should be cleared & None returned
        ul.path = 'part-1/deletedsection/'
        ul.save()
        self.assertIsNone(get_user_last_location(user, self.h))
        qs = UserLocation.objects.filter(user=user, hierarchy=self.h)
        self.assertFalse(qs.exists())


class TestUtils(TestCase):
    def setUp(self):
        UELCModuleFactory()
        self.h = Hierarchy.objects.get(name='case-test')

    def test_gen_fac_token(self):
        r = RequestFactory()
        gu = GroupUpFactory()
        r.user = gu.user
        r.META = {}
        hierarchy_name = 'module_%02d' % self.h.pk

        self.assertTrue(
            gen_fac_token(r, self.h).startswith(
                '{}:uelc.pages/{}/facilitator/:uelc.pages'
                '/{}/facilitator/.{}:'.format(
                    gu.user.username, hierarchy_name,
                    hierarchy_name, gu.user.username)))

    def test_gen_group_token(self):
        r = RequestFactory()
        gu = GroupUpFactory()
        r.user = gu.user
        r.META = {}
        root = self.h.get_root()

        self.assertTrue(
            gen_group_token(r, root.pk).startswith(
                '{}:uelc.{}:uelc.{}.{}:'.format(
                    gu.user.username, root.pk,
                    root.pk, gu.user.username)))
