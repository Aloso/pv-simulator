#!/usr/bin/env python
from libpv.time_of_day import TimeOfDay, SECS_PER_DAY
from libpv.prng import continuous_prng

import argparse
import pika
import sys
from random import Random, randrange

QUEUE = 'meter'


def parse_args():
    parser = argparse.ArgumentParser(
        prog='meter',
        description='Send meter values to RabbitMQ')

    parser.add_argument(
        '-m', '--max-consumption',
        metavar='POWER',
        type=int,
        default=9000,
        help='the maximum amount of power consumption in Watt [default: 9000]')
    parser.add_argument(
        '-s', '--seed',
        type=int,
        help='the seed for randomness')
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="don't print information to stdout")

    return parser.parse_args()


def main():
    args = parse_args()

    quiet = args.quiet
    max_power = args.max_consumption
    seed = args.seed if args.seed is not None else randrange(sys.maxsize)

    if max_power < 0:
        raise CliError('max-consumption must be positive')

    if not quiet:
        print(f' [*] Connecting to `{QUEUE}` queue')

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE)

    if not quiet:
        print(f' [*] Generating values between 0 and {max_power} with seed {seed}')

    rng = continuous_prng(
        v_min=0,
        v_max=max_power,
        max_diff=max_power / 500,
        max_equal_values=300,
        randomness=Random(seed))

    for time in times_of_day(seconds_step=5):
        timestamp = time.seconds()
        value = -next(rng)

        channel.basic_publish(exchange='', routing_key=QUEUE, body=f'{timestamp}:{value}')

    connection.close()

    if not quiet:
        print('Done')


def times_of_day(seconds_step: int):
    t = TimeOfDay(0)  # midnight

    for _ in range(0, SECS_PER_DAY - seconds_step, seconds_step):
        t += seconds_step
        yield t


class CliError(Exception):
    def __init__(self, desc: str):
        self.description = desc


if __name__ == '__main__':
    try:
        main()
    except CliError as e:
        print(f'error: {e.description}')
        sys.exit(1)
