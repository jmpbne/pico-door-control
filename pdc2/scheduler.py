import asyncio
import time

import adafruit_datetime as datetime

from pdc import config
from pdc.hardware import motor, rtc
from pdc2 import state

SLEEP_VALUE = 5.0
SECONDS_IN_A_DAY = 24 * 60 * 60

motor_a = motor.Motor(config.MOTOR_A_PHASE1, config.MOTOR_A_PHASE2, config.MOTOR_A_SPEED)
motor_b = motor.Motor(config.MOTOR_B_PHASE1, config.MOTOR_B_PHASE2, config.MOTOR_B_SPEED)


async def scheduler():
    while True:
        if rtc.device.lost_power:
            print("*RTC device lost power")
            await asyncio.sleep(SLEEP_VALUE)
            continue

        now = datetime.datetime.now()
        now_timestamp = time.mktime(now.timetuple())

        print("---")
        for motor_id, motor_data in state._state.items():
            timestamp = motor_data.get("t")
            oneshot = motor_data.get("1")
            hour = motor_data.get("h")
            minute = motor_data.get("m")
            speed = motor_data.get("p")
            duration = motor_data.get("d")

            if not timestamp:
                if oneshot:
                    print(f"'{motor_id}' is an one-shot task without timestamp, skipping")
                    continue

                if hour is None or minute is None:
                    print(f"'{motor_id}' is not enabled, skipping")
                    continue

                print(f"'{motor_id}' does not have timestamp yet")

                dt = datetime.datetime.combine(now, datetime.time(hour, minute))
                if now > dt:
                    dt += datetime.timedelta(days=1)
                timestamp = time.mktime(dt.timetuple())
                motor_data["t"] = timestamp

                print(f"'{motor_id}' has new timestamp value of {timestamp}")

            if timestamp > now_timestamp:
                print(f"'{motor_id}' is delayed (now={now_timestamp}, schedule={timestamp})")
            else:
                print(f"'{motor_id}' is running (now={now_timestamp}, schedule={timestamp})")
                await run_motor_method(motor_id, speed, duration)
                if oneshot:
                    print(f"'{motor_id}' is an one-shot task")
                    motor_data["t"] = None
                else:
                    print(f"'{motor_id}' is not one-shot task, setting new timestamp")
                    motor_data["t"] = timestamp + SECONDS_IN_A_DAY

        await asyncio.sleep(SLEEP_VALUE)


async def run_motor_method(motor_id, speed, duration):
    if motor_id.startswith("ao"):
        method = open_motor_a
    elif motor_id.startswith("bo"):
        method = open_motor_b
    elif motor_id.startswith("ac"):
        method = close_motor_a
    elif motor_id.startswith("bc"):
        method = close_motor_b
    else:
        print(f"'{motor_id}' does not have associated handler")
        return

    await method(speed, duration)


async def open_motor_a(speed, duration):
    motor_a.open(speed)
    await asyncio.sleep(duration)
    motor_a.stop()
    await asyncio.sleep(1)


async def open_motor_b(speed, duration):
    motor_b.open(speed)
    await asyncio.sleep(duration)
    motor_b.stop()
    await asyncio.sleep(1)


async def close_motor_a(speed, duration):
    motor_a.close(speed)
    await asyncio.sleep(duration)
    motor_a.stop()
    await asyncio.sleep(1)


async def close_motor_b(speed, duration):
    motor_b.close(speed)
    await asyncio.sleep(duration)
    motor_b.stop()
    await asyncio.sleep(1)
