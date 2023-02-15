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


def _get_value(motor_id, key, default):
    return state.data.get(motor_id, {}).get(key, default)


def _set_value(motor_id, key, value):
    state.data.setdefault(motor_id, dict(default_state))[key] = value

    state.save_state()
    scheduler.init()


def run_oneshot(motor_id):
    scheduler.request_oneshot(motor_id)


def get_duration(motor_id):
    return _get_value(motor_id, constants.DURATION_KEY, constants.DURATION_DEFAULT)


def get_speed(motor_id):
    return _get_value(motor_id, constants.SPEED_KEY, constants.SPEED_DEFAULT)


def get_hour(motor_id):
    return _get_value(motor_id, constants.HOUR_KEY, constants.HOUR_DEFAULT)


def get_minute(motor_id):
    return _get_value(motor_id, constants.MINUTE_KEY, constants.MINUTE_DEFAULT)


def get_count(motor_id):
    return _get_value(motor_id, constants.COUNT_KEY, constants.COUNT_DEFAULT)


def get_rate(motor_id):
    return _get_value(motor_id, constants.RATE_KEY, constants.RATE_DEFAULT)


def set_duration(motor_id, duration):
    _set_value(motor_id, constants.DURATION_KEY, duration)


def set_speed(motor_id, speed):
    _set_value(motor_id, constants.SPEED_KEY, speed)


def set_hour(motor_id, hour):
    _set_value(motor_id, constants.HOUR_KEY, hour)


def set_minute(motor_id, minute):
    _set_value(motor_id, constants.MINUTE_KEY, minute)


def set_count(motor_id, count):
    _set_value(motor_id, constants.COUNT_KEY, count)


def set_rate(motor_id, rate):
    _set_value(motor_id, constants.RATE_KEY, rate)
