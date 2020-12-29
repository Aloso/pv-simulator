#!/usr/bin/env python
from prng import continuous_prng

import itertools
import random
import unittest


class TestContinuousPrng(unittest.TestCase):
    def setUp(self):
        self.max_diff = 50
        self.prng = continuous_prng(0, 1000, self.max_diff, 50, random.Random(0))

    def testEquality(self):
        self.assertEqual(
            [x for x in itertools.islice(self.prng, 100)],
            [
                861, 811, 776, 777, 772, 771, 774, 776, 777, 776,
                778, 778, 782, 780, 783, 780, 779, 776, 772, 776,
                775, 778, 782, 779, 778, 747, 743, 748, 748, 750,
                753, 749, 699, 649, 599, 549, 499, 449, 444, 444,
                448, 453, 451, 454, 456, 458, 461, 460, 455, 458,
                453, 449, 450, 455, 460, 510, 560, 610, 660, 710,
                760, 810, 847, 847, 845, 845, 841, 839, 843, 841,
                839, 836, 839, 841, 837, 833, 833, 836, 838, 834,
                833, 836, 835, 831, 834, 834, 837, 835, 785, 735,
                685, 635, 585, 560, 564, 563, 565, 561, 565, 566,
            ])

    def testContinuity(self):
        last = next(self.prng)

        for n in itertools.islice(self.prng, 100_000):
            self.assertLessEqual(abs(last - n), self.max_diff)
            last = n


if __name__ == '__main__':
    unittest.main()
