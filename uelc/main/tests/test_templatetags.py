from django.test import TestCase

from django.test.client import RequestFactory
from pagetree.models import Hierarchy, Section

from uelc.main.templatetags.accessible import get_previous_group_user_section,\
    is_not_last_group_user_section, is_section_unlocked
from uelc.main.templatetags.part_string import convert, convert_part2
from uelc.main.tests.factories import UELCModuleFactory, GroupUpFactory
from uelc.main.views import UELCPageView


class TestPartString(TestCase):

    def test_convert(self):
        self.assertEquals(convert(0), 'part0')
        self.assertEquals(convert(1), 'part1')
        self.assertEquals(convert(2.1), 'part2 Choice-1')
        self.assertEquals(convert(2.2), 'part2 Choice-2')

        # unexpected input
        with self.assertRaises(IndexError):
            self.assertEquals(convert(2), 'part2')

    def test_convert_part2(self):
        self.assertEquals(convert_part2(0), 0)
        self.assertEquals(convert_part2(1), 0)
        self.assertEquals(convert_part2(2.1), 'p1c2-1')
        self.assertEquals(convert_part2(2.2), 'p1c2-2')
        self.assertEquals(convert_part2(2.11), 'p2c2-1')

        # unexpected input
        with self.assertRaises(IndexError):
            self.assertEquals(convert_part2(2), 'part2')


class TestAccessible(TestCase):

    def setUp(self):
        UELCModuleFactory()
        self.h = Hierarchy.objects.get(name='case-test')

        self.view = UELCPageView()
        self.view.hierarchy_base = self.h.base_url
        self.view.hierarchy_name = self.h.name

        self.view.request = RequestFactory().get('/')

    def test_get_previous_group_user_section(self):
        section = Section.objects.get(slug='home')
        previous = section.get_previous()  # part-1
        part = 1

        self.assertFalse(get_previous_group_user_section(
            section, previous, part))

        section = Section.objects.get(slug='intro')
        previous = section.get_previous()  # home
        part = 1

        self.assertEquals(get_previous_group_user_section(
            section, previous, part), previous)

        section = Section.objects.get(slug='your-second-decision')
        previous = section.get_previous()  # Part 2 Choice 1
        part = 2

        prev = get_previous_group_user_section(
            section, previous, part)
        self.assertEquals(prev.slug, 'results')

    def test_is_not_last_group_user_section(self):
        section = Section.objects.get(slug='home')
        self.assertTrue(is_not_last_group_user_section(section, 1))

        section = Section.objects.get(slug='confirm-second-decision')
        self.assertTrue(is_not_last_group_user_section(section, 2))

        section = Section.objects.get(slug='end-of-experience')
        self.assertFalse(is_not_last_group_user_section(section, 2))

    def test_is_section_unlocked(self):
        self.view.request.user = GroupUpFactory().user

        # no blocks
        section = Section.objects.get(slug='home')
        self.assertTrue(is_section_unlocked(self.view.request, section))

        # gate block
        section = Section.objects.get(slug='confirm-first-decision')
        self.assertFalse(is_section_unlocked(self.view.request, section))

        # decision block
        section = Section.objects.get(slug='your-first-decision')
        self.assertFalse(is_section_unlocked(self.view.request, section))
