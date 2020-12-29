SECS_PER_DAY = 60 * 60 * 24


def rem_euclid(lhs: int, rhs: int) -> int:
    "Calculates the least nonnegative remainder of `lhs (mod rhs)`"

    r = lhs % rhs
    if r < 0:
        if rhs < 0:
            return r - rhs
        else:
            return r + rhs
    else:
        return r


class TimeOfDay:
    """
    A time, with seconds precision, between 00:00:00 and 23:59:59

    Example
    -------
    ```
    t = TimeOfDay.from_hms(h=16, m=30) # 4:30 pm
    ```
    """

    def __init__(self, seconds=0):
        "Creates a `TimeOfDay` instance from seconds. The number can be negative and arbitrarily large."
        self.time = rem_euclid(seconds, SECS_PER_DAY)

    @staticmethod
    def from_hms(h=0, m=0, s=0):
        """Creates a `TimeOfDay` instance from hours, minutes and seconds.
        The values can be negative and arbitrarily large."""

        h = rem_euclid(h, 24)
        m = rem_euclid(m, 60)
        s = rem_euclid(s, 60)
        return TimeOfDay(h * 3600 + m * 60 * s)

    @staticmethod
    def parse_hms(input: str):
        """Creates a `TimeOfDay` instance from hours, minutes and seconds, formatted as string.
        Examples: `TimeOfDay.parse('03:50 pm')`, `TimeOfDay.parse('15:50:00')`"""

        if input.endswith('am') or input.endswith('pm'):
            [h, m, s, *_] = input[:-2].strip().split(':') + ['0', '0']

            h = int(h) if input.endswith('am') else int(h) + 12
            m = int(m)
            s = int(s)
            return TimeOfDay.from_hms(h, m, s)
        else:
            [h, m, s, *_] = input.split(':') + ['0', '0']
            return TimeOfDay.from_hms(int(h), int(m), int(s))

    def seconds(self) -> int:
        "The number of seconds since midnight (00:00:00)"
        return self.time

    def hms(self) -> (int, int, int):
        "The number of hours, minutes and seconds since midnight (00:00:00)"

        h = int(self.time / 3600)
        m = int(self.time / 60 % 60)
        s = int(self.time % 60)
        return h, m, s

    def __str__(self):
        (h, m, s) = self.hms()

        if h < 10:
            h = '0' + str(h)
        if m < 10:
            m = '0' + str(m)
        if s < 10:
            s = '0' + str(s)

        return f'{h}:{m}:{s}'

    def __add__(self, seconds: int):
        time = rem_euclid(self.time + seconds, SECS_PER_DAY)
        return TimeOfDay(time)

    def __sub__(self, seconds: int):
        time = rem_euclid(self.time - seconds, SECS_PER_DAY)
        return TimeOfDay(time)

    def __lt__(self, rhs) -> bool:
        return self.seconds() < rhs.seconds()

    def __gt__(self, rhs) -> bool:
        return self.seconds() > rhs.seconds()
