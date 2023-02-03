from busio import I2C
from rtc import RTC

from adafruit_ds3231 import DS3231

from controller import config

i2c = I2C(config.I2C_SCL, config.I2C_SDA)
rtc_internal = RTC()
rtc_external = DS3231(i2c)

if not rtc_external.lost_power:
    print("Retrieving time from external RTC")
    rtc_internal.datetime = rtc_external.datetime
else:
    print("External RTC lost power")
