import asyncio
import time

from controller import constants
from controller.core import rtc, state

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


async def run():
    while True:
        current = rtc.get_datetime()
        current_ts = time.mktime(current)
        current_list = list(current)

        print(current)

        for motor_data in list(data):
            # Initialize timestamps on first iteration
            if motor_data.get(TIMESTAMP_KEY) is None:
                mid = motor_data.get(ID_KEY)
                hour = motor_data.get(constants.HOUR_KEY)
                minute = motor_data.get(constants.MINUTE_KEY)

                dd = list(current_list)
                dd[3] = hour
                dd[4] = minute
                dd[5] = 0

                date = time.struct_time(dd)
                date_ts = time.mktime(date)

                if current_ts > date_ts:
                    date_ts += 60 * 60 * 24

                print(f"Creating new event at {hour:02d}:{minute:02d} for ID {mid}")
                motor_data[TIMESTAMP_KEY] = date_ts

            # Check if it's time
            if current_ts > motor_data.get(TIMESTAMP_KEY):
                print("Event:", motor_data)
                motor_data[TIMESTAMP_KEY] += 60 * 60 * 24
                print("After:", motor_data)

        await asyncio.sleep(5.0)
        print("---")
