import board
import time
from digitalio import DigitalInOut, Direction

import asyncio

from controller import constants
from controller.core import rtc, state
from controller.service.control import ControlService

ID_KEY = "id"
ONESHOT_KEY = "o"
TIMESTAMP_KEY = "t"

data = []


def init_motor(motor_id, motor_data):
    duration = motor_data.get(constants.DURATION_KEY)
    speed = motor_data.get(constants.SPEED_KEY)
    hour = motor_data.get(constants.HOUR_KEY)
    minute = motor_data.get(constants.MINUTE_KEY)
    count = motor_data.get(constants.COUNT_KEY)
    rate = motor_data.get(constants.RATE_KEY)

    if count < 1:
        return

    for idx in range(count):
        offset = hour * 60 + rate * idx + minute
        hh, mm = divmod(offset, 60)

        if hh > 23:
            continue  # FIXME

        sched_data = {
            ID_KEY: motor_id,
            constants.DURATION_KEY: duration,
            constants.SPEED_KEY: speed,
            constants.HOUR_KEY: hh,
            constants.MINUTE_KEY: mm,
            ONESHOT_KEY: False,
            TIMESTAMP_KEY: None,
        }

        data.append(sched_data)


def init():
    if rtc.get_datetime() is None:
        print("Clock is not set, scheduler will not be started")
        return

    data.clear()

    for motor_id in (constants.MOTOR_OPEN_ID, constants.MOTOR_CLOSE_ID):
        if motor_data := state.data.get(motor_id):
            init_motor(motor_id, motor_data)

    print(data)


def request_oneshot(motor_id):
    print(f"Requesting one-shot for {motor_id}...")

    sched_data = {
        ID_KEY: motor_id,
        constants.DURATION_KEY: ControlService.get_duration(motor_id),
        constants.SPEED_KEY: ControlService.get_speed(motor_id),
        constants.HOUR_KEY: None,
        constants.MINUTE_KEY: None,
        ONESHOT_KEY: True,
        TIMESTAMP_KEY: time.time(),
    }

    for event_data in data:
        oneshot = event_data.get(ONESHOT_KEY)
        if oneshot:
            event_data.clear()
            event_data.update(**sched_data)
            return

    data.append(sched_data)


async def run():
    while True:
        current = rtc.get_datetime()
        if current is None:
            await asyncio.sleep(5.0)
            continue

        current_ts = time.mktime(current)
        current_list = list(current)

        print(current)

        for event_data in list(data):
            # Initialize timestamps on first iteration
            if event_data.get(TIMESTAMP_KEY) is None:
                mid = event_data.get(ID_KEY)
                hour = event_data.get(constants.HOUR_KEY)
                minute = event_data.get(constants.MINUTE_KEY)

                dd = list(current_list)
                dd[3] = hour
                dd[4] = minute
                dd[5] = 0

                date = time.struct_time(dd)
                date_ts = time.mktime(date)

                if current_ts > date_ts:
                    date_ts += 60 * 60 * 24

                print(f"Creating new event at {hour:02d}:{minute:02d} for ID {mid}")
                event_data[TIMESTAMP_KEY] = date_ts

            # Check if it's time
            if current_ts > event_data.get(TIMESTAMP_KEY):
                print("Event:", event_data)

                mid = event_data.get(ID_KEY)
                if mid == constants.MOTOR_OPEN_ID:
                    print("opening")
                    await open_motor(event_data)
                elif mid == constants.MOTOR_CLOSE_ID:
                    print("closing")
                    await close_motor(event_data)
                else:
                    print(f"unknown: {mid}")

                if event_data.get(ONESHOT_KEY):
                    event_data[TIMESTAMP_KEY] = 9999999999  # FIXME
                else:
                    event_data[TIMESTAMP_KEY] += 60 * 60 * 24

                print("After:", event_data)
            else:
                print("SKIP: ", event_data)

        await asyncio.sleep(5.0)
        print("---")


async def open_motor(data):
    en1 = DigitalInOut(board.GP18)
    en2 = DigitalInOut(board.GP20)

    en1.direction = Direction.OUTPUT
    en2.direction = Direction.OUTPUT

    en1.value = False
    en2.value = True

    await asyncio.sleep(data.get(constants.DURATION_KEY))

    en1.value = False
    en2.value = False

    en1.deinit()
    en2.deinit()


async def close_motor(data):
    en1 = DigitalInOut(board.GP21)
    en2 = DigitalInOut(board.GP26)

    en1.direction = Direction.OUTPUT
    en2.direction = Direction.OUTPUT

    en1.value = False
    en2.value = True

    await asyncio.sleep(data.get(constants.DURATION_KEY))

    en1.value = False
    en2.value = False

    en1.deinit()
    en2.deinit()
