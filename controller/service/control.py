from controller import constants
from controller.core import scheduler, state

default_state = {
    constants.DURATION_KEY: constants.DURATION_DEFAULT,
    constants.SPEED_KEY: constants.SPEED_DEFAULT,
    constants.HOUR_KEY: constants.HOUR_DEFAULT,
    constants.MINUTE_KEY: constants.MINUTE_DEFAULT,
    constants.COUNT_KEY: constants.COUNT_DEFAULT,
    constants.RATE_KEY: constants.RATE_DEFAULT,
}


def get_value(motor_id, key, default):
    return state.data.get(motor_id, {}).get(key, default)


def set_value(motor_id, key, value):
    state.data.setdefault(motor_id, dict(default_state))[key] = value

    state.save_state()
    scheduler.init()


class ControlService:
    @staticmethod
    def get_duration(motor_id):
        return get_value(motor_id, constants.DURATION_KEY, constants.DURATION_DEFAULT)

    @staticmethod
    def get_speed(motor_id):
        return get_value(motor_id, constants.SPEED_KEY, constants.SPEED_DEFAULT)

    @staticmethod
    def get_hour(motor_id):
        return get_value(motor_id, constants.HOUR_KEY, constants.HOUR_DEFAULT)

    @staticmethod
    def get_minute(motor_id):
        return get_value(motor_id, constants.MINUTE_KEY, constants.MINUTE_DEFAULT)

    @staticmethod
    def get_count(motor_id):
        return get_value(motor_id, constants.COUNT_KEY, constants.COUNT_DEFAULT)

    @staticmethod
    def get_rate(motor_id):
        return get_value(motor_id, constants.RATE_KEY, constants.RATE_DEFAULT)

    @staticmethod
    def set_duration(motor_id, duration):
        set_value(motor_id, constants.DURATION_KEY, duration)

    @staticmethod
    def set_speed(motor_id, speed):
        set_value(motor_id, constants.SPEED_KEY, speed)

    @staticmethod
    def set_hour(motor_id, hour):
        set_value(motor_id, constants.HOUR_KEY, hour)

    @staticmethod
    def set_minute(motor_id, minute):
        set_value(motor_id, constants.MINUTE_KEY, minute)

    @staticmethod
    def set_count(motor_id, count):
        set_value(motor_id, constants.COUNT_KEY, count)

    @staticmethod
    def set_rate(motor_id, rate):
        set_value(motor_id, constants.RATE_KEY, rate)
