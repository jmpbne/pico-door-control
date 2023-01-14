import rtc
from time import struct_time

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_ds3231 import DS3231

from pdc import config
from pdc.hardware.i2c import i2c

_rtc = None


def init_clock() -> None:
    global _rtc

    _rtc = DS3231(i2c)
    _rtc.i2c_device = I2CDevice(i2c, config.I2C_ADDRESS_RTC)

    rtc.set_time_source(_rtc)

    # todo: handle rtc.lost_power (reset related settings and set new date?)


def set_clock(dt: struct_time) -> None:
    _rtc.datetime = dt
