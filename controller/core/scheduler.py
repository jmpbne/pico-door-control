import board
import time
from digitalio import DigitalInOut, Direction

import asyncio

from controller import constants
from controller.core import rtc
from controller.service.control import ControlService

RUN_RATE = 5.0
SECONDS_IN_A_DAY = 60 * 60 * 24

data = []


class Event:
    def __init__(self, *, motor_id, timestamp, duration, speed, oneshot=False):
        self.motor_id = motor_id
        self.timestamp = timestamp
        self.duration = duration
        self.speed = speed
        self.oneshot = oneshot


def init_motor(motor_id):
    count = ControlService.get_count(motor_id)
    if count < 0:
        return

    duration = ControlService.get_duration(motor_id)
    speed = ControlService.get_speed(motor_id)
    hour = ControlService.get_hour(motor_id)
    minute = ControlService.get_minute(motor_id)
    rate = ControlService.get_rate(motor_id)

    current_time = rtc.get_datetime()
    current_timestamp = time.mktime(current_time)

    for it in range(count):
        offset = hour * 60 + rate * it + minute
        hh, mm = divmod(offset, 60)

        if hh > 23:
            continue  # FIXME

        print(f"Creating scheduled event at {hh:02d}:{mm:02d} for ID '{motor_id}'")

        schedule_time = time.struct_time(
            (
                current_time.tm_year,
                current_time.tm_mon,
                current_time.tm_mday,
                hh,
                mm,
                0,
                -1,
                -1,
                -1,
            )
        )

        schedule_timestamp = time.mktime(schedule_time)
        if current_timestamp > schedule_timestamp:
            schedule_timestamp += SECONDS_IN_A_DAY

        event = Event(
            motor_id=motor_id,
            duration=duration,
            speed=speed,
            timestamp=schedule_timestamp,
        )
        data.append(event)


def init():
    data.clear()

    if rtc.get_datetime() is None:
        print("Clock is not set, scheduler will not be started")
        return

    for motor_id in (constants.MOTOR_OPEN_ID, constants.MOTOR_CLOSE_ID):
        init_motor(motor_id)


def request_oneshot(motor_id):
    print(f"Creating one-time event for ID '{motor_id}'")

    duration = ControlService.get_duration(motor_id)
    speed = ControlService.get_speed(motor_id)

    event = Event(
        motor_id=motor_id,
        duration=duration,
        speed=speed,
        oneshot=True,
        timestamp=time.time(),
    )

    for idx, existing_event in enumerate(data):
        if existing_event.oneshot and motor_id == existing_event.motor_id:
            data[idx] = event
            return

    data.append(event)


async def run():
    while True:
        if len(data) == 0:
            await asyncio.sleep(RUN_RATE)
            continue

        current_time = rtc.get_datetime()
        current_timestamp = time.mktime(current_time)

        for event in list(data):
            if event.timestamp is None or current_timestamp <= event.timestamp:
                continue

            print(f"Executing scheduled action on motor ID '{event.motor_id}'")

            if event.motor_id == constants.MOTOR_OPEN_ID:
                await open_motor(event)
            elif event.motor_id == constants.MOTOR_CLOSE_ID:
                await close_motor(event)
            else:
                print(f"Warning: unknown motor ID '{event.motor_id}'")

            if event.oneshot:
                event.timestamp = None
            else:
                event.timestamp += SECONDS_IN_A_DAY

        await asyncio.sleep(RUN_RATE)


async def control_motor(event, en1_pin, en2_pin):
    en1 = DigitalInOut(en1_pin)
    en2 = DigitalInOut(en2_pin)

    en1.direction = Direction.OUTPUT
    en2.direction = Direction.OUTPUT

    en1.value = False
    en2.value = True

    await asyncio.sleep(event.duration)

    en1.value = False
    en2.value = False

    en1.deinit()
    en2.deinit()


async def open_motor(event):
    print("Opening")
    await control_motor(event, board.GP18, board.GP20)


async def close_motor(event):
    print("Closing")
    await control_motor(event, board.GP21, board.GP26)
