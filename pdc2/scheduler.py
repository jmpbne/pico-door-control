import asyncio
import time

from adafruit_datetime import datetime, timedelta
from adafruit_datetime import time as dtime

from pdc.hardware import rtc
from pdc2 import state

SLEEP_VALUE = 5.0


async def scheduler():
    while True:
        if rtc.device.lost_power:
            print("*RTC device lost power")
            await asyncio.sleep(SLEEP_VALUE)
            continue

        now = datetime.now()
        now_epoch = time.mktime(now.timetuple())

        print("---")
        for key, data in state._state.items():
            hour = data.get("h")
            minute = data.get("m")

            if (
                (not data.get("t"))
                and (not data.get("1"))
                and (hour is not None)
                and (minute is not None)
            ):
                print(f"*'{key}' does not have timestamp set")

                dt1 = datetime.combine(now, dtime(hour, minute))
                dt2 = dt1 + timedelta(days=1)

                if now < dt1:
                    data["t"] = time.mktime(dt1.timetuple())
                    print(f"*'{key}': it is {now}, next run on {dt1}")
                else:
                    data["t"] = time.mktime(dt2.timetuple())
                    print(f"*[sched] '{key}': it is {now}, next run on {dt2}")

            timestamp = data.get("t")
            if not timestamp:
                print(f"*'{key}: timestamp not set, ignoring")
                continue

            if now_epoch > timestamp:
                print(f"'{key}': it is {now_epoch}, scheduled for {timestamp}, running")
                if data.get("1"):
                    print(f"'{key}' is oneshot, not setting timestamp")
                    data["t"] = None
                else:
                    print(f"'{key}' is not oneshot, setting new timestamp")
                    data["t"] = timestamp + (60 * 60 * 24)
            else:
                print(f"'{key}': it is {now_epoch}, scheduled for {timestamp}, ignoring")

        await asyncio.sleep(SLEEP_VALUE)
