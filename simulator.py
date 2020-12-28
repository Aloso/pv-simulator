#!/usr/bin/env python
from src.time_of_day import TimeOfDay
from src.prng import continuous_prng

import argparse
import os
import pika
from random import Random, randrange
import sys

QUEUE = 'meter'

# A flag to emit a CSV file instead (for debugging purposes)
CSV_OUTPUT = False


def parse_args():
    parser = argparse.ArgumentParser(
        prog='simulator',
        description='Write simulated meter and pv power values to a file')

    parser.add_argument(
        '-m', '--max-power',
        metavar='POWER',
        type=int,
        default=3500,
        help='the maximum amount of power produced in Watt [default: 3500]')
    parser.add_argument(
        '-i', '--sunrise',
        metavar='TIME',
        type=str,
        default='08:00',
        help='the time of sunrise [default: 8 am]')
    parser.add_argument(
        '-e', '--sunset',
        metavar='TIME',
        type=str,
        default='20:00',
        help='the time of sunset [default: 8 pm]')
    parser.add_argument(
        '-w', '--weather-noise',
        metavar='NOISE',
        type=float,
        default=0.4,
        help='the amount of noise caused by the weather. '
        '0 = no noise, 1 = lots of noise [default: 0.4]')
    parser.add_argument(
        '-s', '--seed',
        type=int,
        help='the seed for randomness')
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        type=str,
        default='pv_values.txt',
        help='the file where the values should be written to [default: pv_values.txt]')
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="don't print information to stdout")

    return parser.parse_args()


def main():
    args = parse_args()

    quiet = args.quiet
    max_power = args.max_power
    sunrise = TimeOfDay.parse_hms(args.sunrise)
    sunset = TimeOfDay.parse_hms(args.sunset)
    noise_factor = args.weather_noise
    seed = args.seed if args.seed is not None else randrange(sys.maxsize)

    with open(args.output, 'x') as file:
        if not quiet:
            print(f' [*] The sun shines between {sunrise} and {sunset}')
            print(f' [*] Maximum power output: {max_power}')
            print(f' [*] Noise factor: {noise_factor}')
            print(f' [*] Seed: {seed}')
            print(f' [*] Connecting to `{QUEUE}` queue')

        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE)

        seed = randrange(sys.maxsize)
        randomness = Random(seed)

        weather_gen = weather(noise_factor, randomness)
        pv_gen = PvGenerator(sunrise, sunset, max_power)

        def receive(ch, method, properties, body: bytes):
            time, meter_value = parse_meter_message(body)
            pv_value = round(pv_gen.get_value(time) * next(weather_gen))
            sum = meter_value + pv_value

            if CSV_OUTPUT:
                file.write(f'{time},{meter_value},{pv_value},{sum}\n')
            else:
                file.write(
                    f'[{time}] meter: {meter_value}    \tpv: {pv_value}   \tsum: {sum}\n')

        channel.basic_consume(
            queue=QUEUE,
            auto_ack=True,
            on_message_callback=receive)

        if not quiet:
            print(' [*] Waiting for messages. To exit press CTRL+C')

        channel.start_consuming()


def parse_meter_message(msg: bytes) -> (TimeOfDay, int):
    [timestamp, meter_value] = msg.decode('ascii').split(':')
    return TimeOfDay(int(timestamp)), int(meter_value)


class PvGenerator:
    "Generates PV (photovoltaic) power values"

    def __init__(self, sunrise: TimeOfDay, sunset: TimeOfDay, max_power: int):
        self.sunrise = sunrise
        self.sunset = sunset
        self.max_power = max_power

        self.day_len = sunset.seconds() - sunrise.seconds()
        self.zenith_time = sunrise + self.day_len / 2

        dawn_len = self.day_len / 10
        self.dawn_start = self.sunrise + -dawn_len
        self.dusk_end = self.sunset + dawn_len

        self.poly_factor = -max_power / (self.day_len / 2) ** 2
        self.dawn_slope = max_power / (self.day_len / 2 + dawn_len) / 3

    def get_value(self, time: TimeOfDay) -> int:
        x = time.seconds()
        if x < self.dawn_start.seconds() or x > self.dusk_end.seconds():
            return 0
        else:
            t1 = self.get_polynomial_value(time)
            t2 = self.get_dawn_or_dusk_value(time)
            return max(t1, t2)

    def get_dawn_or_dusk_value(self, time: TimeOfDay) -> int:
        x = time.seconds()
        if x < self.zenith_time.seconds():
            return (x - self.dawn_start.seconds()) * self.dawn_slope
        else:
            return (x - self.dusk_end.seconds()) * (-self.dawn_slope)

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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
    except FileExistsError as e:
        print('error: File %r already exists\n'
              'delete or rename it before trying again' % e.filename)
