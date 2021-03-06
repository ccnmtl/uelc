import json

from django.test import TestCase
from pagetree.models import Hierarchy, PageBlock
from quizblock.models import Submission
from quizblock.tests.test_models import FakeReq

from uelc.main.models import TextBlockDT, CaseQuiz, CaseMap
from uelc.main.tests.factories import (
    AdminUserFactory, AdminUpFactory, FacilitatorUpFactory,
    GroupUpFactory, CaseFactory, GroupUserFactory,
    CohortFactory, CaseMapFactory,
    TextBlockDTFactory, CaseQuizFactory,
    UELCModuleFactory, ImageUploadItemFactory, CaseAnswerFactory,
    AnswerFactory, QuestionFactory, QuizFactory
)


class BasicModelTest(TestCase):

    def setup(self):
        self.user = AdminUserFactory()


class TestAdminUp(TestCase):

    def test_unicode(self):
        upro = AdminUpFactory()
        self.assertEqual(upro.display_name(),
                         upro.user.first_name)
        self.assertTrue(upro.is_admin())


class TestFacilitatorUp(TestCase):

    def test_unicode(self):
        upro = FacilitatorUpFactory()
        self.assertEqual(upro.display_name(),
                         upro.user.first_name)
        self.assertTrue(upro.is_assistant())

    def test_edit_form(self):
        edit_form = FacilitatorUpFactory(cohort=CohortFactory()).edit_form()
        self.assertTrue('username' in edit_form.fields)
        self.assertTrue('profile_type' in edit_form.fields)
        self.assertTrue('cohort' in edit_form.fields)


class TestGroupUp(TestCase):

    def test_unicode(self):
        upro = GroupUpFactory()
        self.assertEqual(upro.display_name(),
                         upro.user.first_name)
        self.assertTrue(upro.is_group_user())
        self.assertTrue(str(upro).startswith("user"))

    def test_cohorts(self):
        upro = GroupUpFactory()
        self.assertTrue(upro.cohort)


class CohortTest(TestCase):
    def test_unicode(self):
        case = CaseFactory()
        cohort = CohortFactory()
        case.cohort.add(cohort)
        self.assertEqual(case.status, 'd')
        self.assertEqual(cohort.display_name(), cohort.name)
        self.assertTrue(str(cohort).startswith("cohort "))

    def test_get_users(self):
        cohort = CohortFactory()
        facil = FacilitatorUpFactory(cohort=cohort)
        grp1 = GroupUpFactory(cohort=cohort)
        grp2 = GroupUpFactory(cohort=cohort)
        self.assertTrue(facil.user in cohort._get_users())
        self.assertTrue(grp1.user in cohort._get_users())
        self.assertTrue(grp2.user in cohort._get_users())

    def test_casename(self):
        cohort = CohortFactory()
        case = CaseFactory()
        case.cohort.add(cohort)
        self.assertIsNotNone(cohort.casename)
        self.assertTrue(case, cohort.casename)

    def test_get_case(self):
        '''test incomplete'''
        cohort = CohortFactory()
        case = CaseFactory()
        case.cohort.add(cohort)
        self.assertIsNotNone(cohort.case)
        self.assertTrue(case, cohort.case)

    def test_usernames(self):
        cohort = CohortFactory()
        facil = FacilitatorUpFactory(cohort=cohort)
        grp1 = GroupUpFactory(cohort=cohort)
        grp2 = GroupUpFactory(cohort=cohort)
        self.assertTrue(facil.user.username in cohort.usernames())
        self.assertTrue(grp1.user.username in cohort.usernames())
        self.assertTrue(grp2.user.username in cohort.usernames())

    def test_add_form(self):
        add_form = CohortFactory().add_form()
        self.assertTrue('name' in add_form.fields)

    def test_edit_form(self):
        cohort = CohortFactory()
        case = CaseFactory()
        case.cohort.add(cohort)
        edit_form = cohort.edit_form()
        self.assertTrue('name' in edit_form.fields)


class CaseTest(TestCase):
    def setUp(self):
        self.case = CaseFactory()
        self.cohort = CohortFactory()
        self.case.cohort.add(self.cohort)

    def test_unicode(self):
        self.assertEqual(self.case.display_name(), self.case.name)
        self.assertTrue(str(self.case).startswith("case "))

    def test_add_form(self):
        add_form = CaseFactory().add_form()
        self.assertTrue('name' in add_form.fields)
        self.assertTrue('hierarchy' in add_form.fields)
        self.assertTrue('cohort' in add_form.fields)

    def test_case_get_cohorts(self):
        self.assertIsNotNone(self.case._get_cohorts())
        self.assertTrue(self.cohort in self.case._get_cohorts())

    def test_case_cohortnames(self):
        self.assertIsNotNone(self.case.cohortnames())
        self.assertTrue(self.cohort.name in self.case.cohortnames())


class CaseMapTest(TestCase):
    def test_get_value(self):
        cm = CaseMapFactory()
        self.assertEqual(cm.get_value(), "")

    def test_add_value_places_noop(self):
        cm = CaseMapFactory()
        cm.add_value_places(0)


class TextBlockDTTest(TestCase):
    def test_add_form(self):
        f = TextBlockDT.add_form()
        self.assertTrue('body' in f.fields)

    def test_edit_form(self):
        t = TextBlockDTFactory()
        self.assertTrue('body' in t.edit_form().fields)

    def test_save(self):
        t = TextBlockDTFactory()
        vals = dict(body="a new body",
                    choice="2")
        t.edit(vals, None)
        self.assertEqual(t.body, "a new body")
        self.assertEqual(t.choice, "2")

    def test_summary_render_short(self):
        t = TextBlockDTFactory(body="a body <>")
        self.assertEqual(t.summary_render(), "a body &lt;>")

    def test_summary_render_long(self):
        t = TextBlockDTFactory(body="foo" * 100)
        self.assertTrue(t.summary_render().endswith("..."))


class ImageUploadItemTest(TestCase):
    def test_unicode(self):
        imgup = ImageUploadItemFactory()
        self.assertEqual(imgup.display_name(), imgup.name)
        self.assertEqual(str(imgup), imgup.name)


class CaseQuizTest(TestCase):
    def test_create(self):
        r = FakeReq()
        r.POST = {'description': 'description', 'rhetorical': True,
                  'allow_redo': True, 'show_submit_state': False}
        casequiz = CaseQuiz.create(r)
        self.assertEquals(casequiz.description, 'description')
        self.assertEquals(casequiz.display_name, 'Decision Block')

    def test_create_from_dict(self):
        quizdictionary = CaseQuiz(description='description')
        d = quizdictionary.as_dict()
        casequiz = CaseQuiz.create_from_dict(d)
        self.assertEquals(casequiz.description, 'description')
        self.assertEquals(casequiz.allow_redo, quizdictionary.allow_redo)

    def test_add_form(self):
        frm = CaseQuiz.add_form()
        self.assertTrue('description' in frm.fields)

    def test_is_submitted_and_unlocked(self):
        user = GroupUserFactory()
        cq = CaseQuizFactory()
        self.assertFalse(cq.unlocked(user, cq))
        self.assertFalse(cq.is_submitted(cq, user))
        # cq.submit(user, dict(case=cf.pk))
        sub = Submission.objects.create(quiz=cq, user=user)
        self.assertTrue(cq.is_submitted(cq, user))
        self.assertTrue(sub in cq.submission_set.filter(user=user))

    def test_make_casemap(self):
        m = UELCModuleFactory()
        cq = CaseQuizFactory()
        user = GroupUserFactory()
        cq.pageblocks.add(PageBlock.objects.last())
        data = {'question': m.case.pk}
        cq.make_casemap(user, data, None, 'question')
        self.assertEqual(
            CaseMap.objects.get(user=user, case_id=m.case.pk).value,
            '0000000000000000{}00000'.format(m.case.pk))

    def test_make_casemap_with_multiple_casemaps(self):
        m = UELCModuleFactory()
        cq = CaseQuizFactory()
        user = GroupUserFactory()
        CaseMap.objects.create(user=user, case_id=m.case.pk)
        CaseMap.objects.create(user=user, case_id=m.case.pk)
        cq.pageblocks.add(PageBlock.objects.last())
        data = {'question': m.case.pk}
        cq.make_casemap(user, data, None, 'question')
        self.assertEqual(
            CaseMap.objects.filter(user=user, case_id=m.case.pk).count(),
            2)


class CaseAnswerTest(TestCase):
    def setUp(self):
        self.caseans = CaseAnswerFactory(
            answer=AnswerFactory(question=QuestionFactory(quiz=QuizFactory())))

    def test_unicode(self):
        self.assertEqual(self.caseans.default_question(),
                         self.caseans.answer.question_id)
        self.assertEqual(self.caseans.display_answer(), self.caseans.answer)
        self.assertEqual(self.caseans.display_title(), self.caseans.title)
        self.assertEqual(self.caseans.display_description(),
                         self.caseans.description)

    def test_edit_form(self):
        edit_form = self.caseans.edit_form()
        self.assertEqual(type(edit_form).__name__, 'CaseAnswerForm')


class UELCModuleFactoryTest(TestCase):
    def test_is_valid_from_factory(self):
        UELCModuleFactory()

    def test_is_json_serializable(self):
        UELCModuleFactory()
        h = Hierarchy.objects.get(name='case-test')
        json.dumps(h.as_dict())

    def test_can_clone_hierarchy(self):
        UELCModuleFactory()
        h = Hierarchy.objects.get(name='case-test')
        clone = Hierarchy.clone(h, 'cloned', '/pages/cloned/')
        self.assertEqual(clone.name, 'cloned')
        self.assertEqual(clone.base_url, '/pages/cloned/')
