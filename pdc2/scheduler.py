import asyncio
import time

import adafruit_datetime as datetime

from pdc.hardware import rtc
from pdc2 import state

SLEEP_VALUE = 5.0
SECONDS_IN_A_DAY = 24 * 60 * 60


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
                if oneshot:
                    print(f"'{motor_id}' is an one-shot task")
                    motor_data["t"] = None
                else:
                    print(f"'{motor_id}' is not one-shot task, setting new timestamp")
                    motor_data["t"] = timestamp + SECONDS_IN_A_DAY

        await asyncio.sleep(SLEEP_VALUE)
