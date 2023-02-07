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


def get_settings(motor_id):
    # TODO: do not modify state here
    return state.data.setdefault(motor_id, dict(default_state))


def post_set_settings(motor_id):
    # TODO: update NVM data and restart scheduler
    print(get_settings(motor_id))


class ControlService:
    @staticmethod
    def get_duration(motor_id):
        return get_settings(motor_id).get(DURATION_KEY)

    @staticmethod
    def get_speed(motor_id):
        return get_settings(motor_id).get(SPEED_KEY)

    @staticmethod
    def get_hour(motor_id):
        return get_settings(motor_id).get(HOUR_KEY)

    @staticmethod
    def get_minute(motor_id):
        return get_settings(motor_id).get(MINUTE_KEY)

    @staticmethod
    def get_count(motor_id):
        return get_settings(motor_id).get(COUNT_KEY)

    @staticmethod
    def get_rate(motor_id):
        return get_settings(motor_id).get(RATE_KEY)

    @staticmethod
    def set_duration(motor_id, duration):
        get_settings(motor_id)[DURATION_KEY] = duration
        post_set_settings(motor_id)

    @staticmethod
    def set_speed(motor_id, speed):
        get_settings(motor_id)[SPEED_KEY] = speed
        post_set_settings(motor_id)

    @staticmethod
    def set_hour(motor_id, hour):
        get_settings(motor_id)[HOUR_KEY] = hour
        post_set_settings(motor_id)

    @staticmethod
    def set_minute(motor_id, minute):
        get_settings(motor_id)[MINUTE_KEY] = minute
        post_set_settings(motor_id)

    @staticmethod
    def set_count(motor_id, count):
        get_settings(motor_id)[COUNT_KEY] = count
        post_set_settings(motor_id)

    @staticmethod
    def set_rate(motor_id, rate):
        get_settings(motor_id)[RATE_KEY] = rate
        post_set_settings(motor_id)
