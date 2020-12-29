#!/usr/bin/env python
from src.time_of_day import TimeOfDay
from src.pv_generation import PvGenerator, weather

import argparse
import os
import pika
from random import Random, randrange
import sys

QUEUE = 'meter'


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
    csv_output = args.output.endswith('.csv')

    if sunrise > sunset:
        raise CliError("sunrise can't occur after sunset")
    if max_power < 0:
        raise CliError('max-power must be positive')
    if noise_factor < 0 or noise_factor > 1:
        raise CliError('noise-factor must be between 0 and 1')

    with open(args.output, 'x') as file:
        if not quiet:
            print(f' [*] The sun shines between {sunrise} and {sunset}')
            print(f' [*] Maximum power output: {max_power}')
            print(f' [*] Noise factor: {noise_factor}')
            print(f' [*] Seed: {seed}')
            print(f' [*] Connecting to `{QUEUE}` queue')

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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

            if csv_output:
                file.write(f'{time},{meter_value},{pv_value},{sum}\n')
            else:
                file.write(f'[{time}] M:{meter_value} P:{pv_value} S:{sum}\n')

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


class CliError(Exception):
    def __init__(self, desc: str):
        self.description = desc


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
    except FileExistsError as e:
        print(f'error: File `{e.filename}`` already exists\n'
              'delete or rename it before trying again')
        sys.exit(1)
    except CliError as e:
        print(f'error: {e.description}')
        sys.exit(1)
