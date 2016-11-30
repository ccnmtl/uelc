from django.test import TestCase

from uelc.main.templatetags.part_string import convert, convert_part2


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
