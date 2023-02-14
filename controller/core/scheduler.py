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

        schedule_data = {
            "id": motor_id,
            "duration": duration,
            "speed": speed,
            "oneshot": False,
            "timestamp": schedule_timestamp,
        }
        data.append(schedule_data)


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

    schedule_data = {
        "id": motor_id,
        "duration": duration,
        "speed": speed,
        "oneshot": True,
        "timestamp": time.time(),
    }

    for existing_data in data:
        oneshot = existing_data.get("oneshot")
        existing_id = existing_data.get("id")

        if oneshot and motor_id == existing_id:
            existing_data.clear()
            existing_data.update(**schedule_data)
            return

    data.append(schedule_data)


async def run():
    while True:
        if len(data) == 0:
            await asyncio.sleep(RUN_RATE)
            continue

        current_time = rtc.get_datetime()
        current_timestamp = time.mktime(current_time)

        for schedule_data in list(data):
            schedule_timestamp = schedule_data.get("timestamp")
            if schedule_timestamp is None or current_timestamp <= schedule_timestamp:
                continue

            print(f"Executing scheduled action on motor ID '{schedule_data}'")

            motor_id = schedule_data.get("id")
            if motor_id == constants.MOTOR_OPEN_ID:
                await open_motor(schedule_data)
            elif motor_id == constants.MOTOR_CLOSE_ID:
                await close_motor(schedule_data)
            else:
                print(f"Warning: unknown motor ID '{motor_id}'")

            oneshot = schedule_data.get("oneshot")
            if oneshot:
                schedule_data["timestamp"] = None
            else:
                schedule_data["timestamp"] += SECONDS_IN_A_DAY

        await asyncio.sleep(RUN_RATE)


async def open_motor(data):
    print("Opening")

    en1 = DigitalInOut(board.GP18)
    en2 = DigitalInOut(board.GP20)

    en1.direction = Direction.OUTPUT
    en2.direction = Direction.OUTPUT

    en1.value = False
    en2.value = True

    await asyncio.sleep(data.get("duration"))

    en1.value = False
    en2.value = False

    en1.deinit()
    en2.deinit()


async def close_motor(data):
    print("Closing")

    en1 = DigitalInOut(board.GP21)
    en2 = DigitalInOut(board.GP26)

    en1.direction = Direction.OUTPUT
    en2.direction = Direction.OUTPUT

    en1.value = False
    en2.value = True

    await asyncio.sleep(data.get("duration"))

    en1.value = False
    en2.value = False

    en1.deinit()
    en2.deinit()
