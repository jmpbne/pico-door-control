import rtc

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_datetime import datetime
from adafruit_ds3231 import DS3231

from pdc import config, state
from pdc.hardware import i2c

device = None


def init_rtc() -> None:
    global device

    # DS3231 library does not support custom I2C address in initializer
    device = DS3231(i2c.device)
    device.i2c_device = I2CDevice(i2c.device, config.I2C_ADDRESS_RTC)

    if device.lost_power:
        state.erase_eeprom()
        device.datetime = datetime(2000, 1, 1, 0, 0, 0).timetuple()

    rtc.set_time_source(device)
