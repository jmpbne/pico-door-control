from controller.core import state

DURATION_KEY = "d"
SPEED_KEY = "s"
HOUR_KEY = "h"
MINUTE_KEY = "m"
COUNT_KEY = "c"
RATE_KEY = "r"

DURATION_DEFAULT = 1
SPEED_DEFAULT = 100
HOUR_DEFAULT = 0
MINUTE_DEFAULT = 0
COUNT_DEFAULT = 0
RATE_DEFAULT = 2

default_state = {
    DURATION_KEY: DURATION_DEFAULT,
    SPEED_KEY: SPEED_DEFAULT,
    HOUR_KEY: HOUR_DEFAULT,
    MINUTE_KEY: MINUTE_DEFAULT,
    COUNT_KEY: COUNT_DEFAULT,
    RATE_KEY: RATE_DEFAULT,
}


def get_value(motor_id, key, default):
    return state.data.get(motor_id, {}).get(key, default)


def set_value(motor_id, key, value):
    state.data.setdefault(motor_id, dict(default_state))[key] = value

    # TODO: update NVM data and restart scheduler
    print(state.data)


class ControlService:
    @staticmethod
    def get_duration(motor_id):
        return get_value(motor_id, DURATION_KEY, DURATION_DEFAULT)

    @staticmethod
    def get_speed(motor_id):
        return get_value(motor_id, SPEED_KEY, SPEED_DEFAULT)

    @staticmethod
    def get_hour(motor_id):
        return get_value(motor_id, HOUR_KEY, HOUR_DEFAULT)

    @staticmethod
    def get_minute(motor_id):
        return get_value(motor_id, MINUTE_KEY, MINUTE_DEFAULT)

    @staticmethod
    def get_count(motor_id):
        return get_value(motor_id, COUNT_KEY, COUNT_DEFAULT)

    @staticmethod
    def get_rate(motor_id):
        return get_value(motor_id, RATE_KEY, RATE_DEFAULT)

    @staticmethod
    def set_duration(motor_id, duration):
        set_value(motor_id, DURATION_KEY, duration)

    @staticmethod
    def set_speed(motor_id, speed):
        set_value(motor_id, SPEED_KEY, speed)

    @staticmethod
    def set_hour(motor_id, hour):
        set_value(motor_id, HOUR_KEY, hour)

    @staticmethod
    def set_minute(motor_id, minute):
        set_value(motor_id, MINUTE_KEY, minute)

    @staticmethod
    def set_count(motor_id, count):
        set_value(motor_id, COUNT_KEY, count)

    @staticmethod
    def set_rate(motor_id, rate):
        set_value(motor_id, RATE_KEY, rate)
