from time import struct_time

from controller.core import rtc


class SystemOptionsService:
    @staticmethod
    def get_hour():
        try:
            return rtc.get_datetime().tm_hour
        except AttributeError:
            return None

    @staticmethod
    def get_minute():
        try:
            return rtc.get_datetime().tm_min
        except AttributeError:
            return None

    @staticmethod
    def set_hour(hour):
        minute = SystemOptionsService.get_minute() or 0
        dt = struct_time((2000, 1, 1, hour, minute, 0, -1, -1, -1))

        rtc.set_datetime(dt)

    @staticmethod
    def set_minute(minute):
        hour = SystemOptionsService.get_hour() or 0
        dt = struct_time((2000, 1, 1, hour, minute, 0, -1, -1, -1))

        rtc.set_datetime(dt)
