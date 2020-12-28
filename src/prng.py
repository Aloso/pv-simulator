from random import Random


def continuous_prng(
        v_min: int, v_max: int,
        max_diff: int, max_equal_values: int,
        randomness: Random):
    "Random number generator, where each value differs from the previous value by at most `max_diff`"

    next_value = None
    prev = None
    equal_values = 0

    while True:
        if equal_values == 0:
            equal_values = randomness.randint(1, max_equal_values)
            next_value = randomness.randint(v_min, v_max)

            if prev is None:
                prev = randomness.randint(v_min, v_max)
        elif next_value == prev:
            v_range = (v_max - v_min) / 200
            next_min = max(v_min, next_value - v_range)
            next_max = min(v_max, next_value + v_range)
            next_value = randomness.randint(int(next_min), int(next_max))

        if abs(next_value - prev) <= max_diff:
            prev = next_value
        elif prev < next_value:
            prev += max_diff
        else:
            prev -= max_diff

        equal_values -= 1

        yield int(prev)
