from busio import I2C
from rtc import RTC

from adafruit_ds3231 import DS3231

from controller import config

i2c = I2C(config.I2C_RTC_SCL, config.I2C_RTC_SDA)

rtc_internal = RTC()
rtc_external = DS3231(i2c)

# Store external RTC state in case it gets disconnected
_lost_power = rtc_external.lost_power


def init():
    if _lost_power:
        print("External RTC lost power")
        return

    print("Retrieving time from external RTC")
    rtc_internal.datetime = rtc_external.datetime


def get_datetime():
    if _lost_power:
        return None

    return rtc_internal.datetime


def set_datetime(dt):
    global _lost_power

    rtc_internal.datetime = dt
    rtc_external.datetime = dt
    _lost_power = False
