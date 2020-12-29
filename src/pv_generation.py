from time_of_day import TimeOfDay
from prng import continuous_prng
from random import Random


class PvGenerator:
    "Generates PV (photovoltaic) power values"

    def __init__(self, sunrise: TimeOfDay, sunset: TimeOfDay, max_power: int):
        self.sunrise = sunrise
        self.sunset = sunset
        self.max_power = max_power

        self.day_len = sunset.seconds() - sunrise.seconds()
        self.zenith_time = sunrise + self.day_len / 2

        dawn_len = self.day_len / 10
        self.dawn_start = self.sunrise - dawn_len
        self.dusk_end = self.sunset + dawn_len

        self.poly_factor = -max_power / (self.day_len / 2) ** 2
        self.dawn_slope = max_power / (self.day_len / 2 + dawn_len) / 3

    def get_value(self, time: TimeOfDay) -> int:
        if time < self.dawn_start or time > self.dusk_end:
            return 0
        else:
            t1 = self.get_polynomial_value(time)
            t2 = self.get_dawn_or_dusk_value(time)
            return max(t1, t2)

    def get_dawn_or_dusk_value(self, time: TimeOfDay) -> int:
        if time < self.zenith_time:
            return (time.seconds() - self.dawn_start.seconds()) * self.dawn_slope
        else:
            return -(time.seconds() - self.dusk_end.seconds()) * self.dawn_slope

    def get_polynomial_value(self, time: TimeOfDay) -> int:
        x = time.seconds()
        z1 = self.sunrise.seconds()
        z2 = self.sunset.seconds()
        return self.poly_factor * (x - z1) * (x - z2)


def weather(noise_factor: float, randomness: Random):
    """
    Generates random but continuous factors to account for the current weather.
    The factors are between 0 and 1, where 1 means clear sky and 0 means really bad weather.

    `noise_factor` specifies the maximum influence of weather.
    For example, if `noise_factor` is 0.8, then all factors are between 0.2 and 1.
    If the `noise_factor` is 0, the `weather_factor` function always returns 1.
    """

    rng1 = continuous_prng(
        v_min=0,
        v_max=10_000,
        max_diff=10,
        max_equal_values=100,
        randomness=randomness)

    rng2 = continuous_prng(
        v_min=0,
        v_max=10_000,
        max_diff=10,
        max_equal_values=100,
        randomness=randomness)

    while True:
        weather = (next(rng1) / 10_000) * (next(rng2) / 10_000)
        yield 1 - (weather * noise_factor)
