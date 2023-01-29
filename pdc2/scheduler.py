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
        for key, data in state._state.items():
            timestamp = data.get("t")
            oneshot = data.get("1")
            hour = data.get("h")
            minute = data.get("m")

            if not timestamp:
                if oneshot:
                    print(f"'{key}' is an one-shot task without timestamp, skipping")
                    continue

                if hour is None or minute is None:
                    print(f"'{key}' is not enabled, skipping")
                    continue

                print(f"'{key}' does not have timestamp yet")

                dt = datetime.datetime.combine(now, datetime.time(hour, minute))
                if now > dt:
                    dt += datetime.timedelta(days=1)
                timestamp = time.mktime(dt.timetuple())
                data["t"] = timestamp

                print(f"'{key}' has new timestamp value of {timestamp}")

            if timestamp > now_timestamp:
                print(f"'{key}' is skipped (now={now_timestamp}, schedule={timestamp})")
            else:
                print(f"'{key}' is running (now={now_timestamp}, schedule={timestamp})")
                if oneshot:
                    print(f"'{key}' is an one-shot task")
                    data["t"] = None
                else:
                    print(f"'{key}' is not one-shot task, setting new timestamp")
                    data["t"] = timestamp + SECONDS_IN_A_DAY

        await asyncio.sleep(SLEEP_VALUE)
