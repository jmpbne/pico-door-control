from rtc import RTC

from adafruit_datetime import datetime


def init_clock() -> RTC:
    clock = RTC()
    clock.datetime = datetime(2000, 1, 1, 0, 0, 0).timetuple()

    return clock


def set_clock(dt: datetime) -> None:
    clock = RTC()
    clock.datetime = dt
