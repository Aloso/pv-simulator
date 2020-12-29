#!/usr/bin/env python
import sys, os, random, unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=import-error

from libpv.time_of_day import TimeOfDay, rem_euclid


class TestTimeOfDay(unittest.TestCase):
    def testInit(self):
        self.assertEqual(str(TimeOfDay(0)), '00:00:00')
        self.assertEqual(str(TimeOfDay(60)), '00:01:00')
        self.assertEqual(str(TimeOfDay(250_000)), '21:26:40')
        self.assertEqual(str(TimeOfDay(6_000_000)), '10:40:00')
        self.assertEqual(str(TimeOfDay(-1)), '23:59:59')
        self.assertEqual(str(TimeOfDay(-6_000_000)), '13:20:00')

    def testFromHms(self):
        self.assertEqual(TimeOfDay.from_hms(), TimeOfDay())
        self.assertEqual(TimeOfDay.from_hms(h=1), TimeOfDay(3600))
        self.assertEqual(TimeOfDay.from_hms(h=-25), TimeOfDay(82800))
        self.assertEqual(TimeOfDay.from_hms(s=-1), TimeOfDay(59))
        self.assertEqual(TimeOfDay.from_hms(m=-119), TimeOfDay(60))
        self.assertEqual(TimeOfDay.from_hms(2, 5, 8), TimeOfDay(7508))

    def testToHms(self):
        self.assertEqual(TimeOfDay().hms(), (0, 0, 0))
        self.assertEqual(TimeOfDay(3600).hms(), (1, 0, 0))
        self.assertEqual(TimeOfDay(82800).hms(), (23, 0, 0))
        self.assertEqual(TimeOfDay(59).hms(), (0, 0, 59))
        self.assertEqual(TimeOfDay(60).hms(), (0, 1, 0))
        self.assertEqual(TimeOfDay(7508).hms(), (2, 5, 8))

    def testParsing(self):
        self.assertEqual(TimeOfDay.parse_hms('0'), TimeOfDay(0))
        self.assertEqual(TimeOfDay.parse_hms('00:00:00'), TimeOfDay(0))
        self.assertEqual(TimeOfDay.parse_hms('0 am'), TimeOfDay(0))
        self.assertEqual(TimeOfDay.parse_hms('4 am'), TimeOfDay.from_hms(4))
        self.assertEqual(TimeOfDay.parse_hms('4 pm'), TimeOfDay.from_hms(16))
        self.assertEqual(TimeOfDay.parse_hms('12:34:56'), TimeOfDay.from_hms(12, 34, 56))
        self.assertEqual(TimeOfDay.parse_hms('1:2:3'), TimeOfDay.from_hms(1, 2, 3))
        self.assertEqual(TimeOfDay.parse_hms('1:2pm'), TimeOfDay.from_hms(13, 2))

    def testComparisons(self):
        self.assertEqual(TimeOfDay(0), TimeOfDay(0))
        self.assertEqual(TimeOfDay(24 * 60 * 60), TimeOfDay(-48 * 60 * 60))
        self.assertLess(TimeOfDay(0), TimeOfDay(1))
        self.assertGreater(TimeOfDay(1), TimeOfDay(0))

    def testAdding(self):
        self.assertEqual(TimeOfDay(0) + 10, TimeOfDay(10))
        self.assertEqual(TimeOfDay(30) - 10, TimeOfDay(20))


if __name__ == '__main__':
    unittest.main()
