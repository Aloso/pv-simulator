#!/usr/bin/env python
import sys, os, random, unittest, itertools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# pylint: disable=import-error

from libpv.pv_generation import PvGenerator, weather
from libpv.time_of_day import TimeOfDay


def generate_360_times():
    t = TimeOfDay(0)
    while True:
        yield t
        t += 240
        if t.seconds() < 240:
            break


class TestPvGeneration(unittest.TestCase):
    def testEquality(self):
        gen = PvGenerator(TimeOfDay.from_hms(8), TimeOfDay.from_hms(20), 3500)
        self.assertEqual(
            [round(gen.get_value(x)) for x in generate_360_times()],
            [
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11,
                22, 32, 43, 54, 65, 76, 86, 97, 108, 119, 130, 140, 151,
                162, 173, 184, 194, 205, 216, 229, 304, 378, 451, 523,
                595, 665, 735, 803, 871, 938, 1004, 1069, 1134, 1197,
                1260, 1322, 1383, 1443, 1502, 1560, 1618, 1674, 1730,
                1785, 1839, 1892, 1944, 1996, 2046, 2096, 2145, 2193,
                2240, 2286, 2332, 2376, 2420, 2463, 2504, 2545, 2586,
                2625, 2663, 2701, 2738, 2774, 2809, 2843, 2876, 2908,
                2940, 2971, 3000, 3029, 3058, 3085, 3111, 3137, 3161,
                3185, 3208, 3230, 3251, 3271, 3291, 3309, 3327, 3344,
                3360, 3375, 3389, 3403, 3415, 3427, 3438, 3448, 3457,
                3465, 3472, 3479, 3484, 3489, 3493, 3496, 3498, 3500,
                3500, 3500, 3498, 3496, 3493, 3489, 3484, 3479, 3472,
                3465, 3457, 3448, 3438, 3427, 3415, 3403, 3389, 3375,
                3360, 3344, 3327, 3309, 3291, 3271, 3251, 3230, 3208,
                3185, 3161, 3137, 3111, 3085, 3058, 3029, 3000, 2971,
                2940, 2908, 2876, 2843, 2809, 2774, 2738, 2701, 2663,
                2625, 2586, 2545, 2504, 2463, 2420, 2376, 2332, 2286,
                2240, 2193, 2145, 2096, 2046, 1996, 1944, 1892, 1839,
                1785, 1730, 1674, 1618, 1560, 1502, 1443, 1383, 1322,
                1260, 1197, 1134, 1069, 1004, 938, 871, 803, 735, 665,
                595, 523, 451, 378, 304, 229, 216, 205, 194, 184, 173, 162,
                151, 140, 130, 119, 108, 97, 86, 76, 65, 54, 43, 32, 22, 11,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            ])

    def testContinuityAndBounds(self):
        gen = PvGenerator(TimeOfDay.from_hms(8), TimeOfDay.from_hms(20), 3500)
        last = gen.get_value(TimeOfDay(0))

        for time in generate_360_times():
            power = gen.get_value(time)
            self.assertGreaterEqual(power, 0)
            self.assertLessEqual(power, 3500)
            self.assertLess(abs(power - last), 80)
            last = power


class TestWeatherGeneration(unittest.TestCase):
    def testEquality(self):
        w = weather(0.6, random.Random(4))
        self.assertEqual(
            [round(x * 10, 3) for x in itertools.islice(w, 100)],
            [
                9.201, 9.197, 9.193, 9.19, 9.186, 9.183, 9.179, 9.175, 9.172, 9.168,
                9.165, 9.161, 9.158, 9.154, 9.15, 9.147, 9.143, 9.14, 9.137, 9.133,
                9.13, 9.126, 9.123, 9.119, 9.116, 9.113, 9.109, 9.106, 9.102, 9.099,
                9.096, 9.102, 9.107, 9.113, 9.119, 9.124, 9.13, 9.136, 9.141, 9.147,
                9.152, 9.158, 9.164, 9.169, 9.175, 9.18, 9.186, 9.191, 9.197, 9.202,
                9.208, 9.213, 9.219, 9.224, 9.23, 9.235, 9.24, 9.246, 9.251, 9.257,
                9.253, 9.25, 9.247, 9.243, 9.24, 9.237, 9.234, 9.23, 9.227, 9.224,
                9.221, 9.218, 9.215, 9.211, 9.208, 9.205, 9.202, 9.199, 9.196, 9.193,
                9.19, 9.187, 9.183, 9.18, 9.177, 9.174, 9.171, 9.168, 9.165, 9.162,
                9.159, 9.157, 9.154, 9.151, 9.148, 9.145, 9.142, 9.139, 9.136, 9.133,
            ])

    def testNoiseFactor(self):
        w = weather(0.4, random.Random(3))
        for n in itertools.islice(w, 200_000):
            self.assertLessEqual(0.6, n)
            self.assertLessEqual(n, 1)


if __name__ == '__main__':
    unittest.main()
