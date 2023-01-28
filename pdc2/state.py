DEFAULT_MOTOR_STATE = {"h": None, "m": None, "p": 1.0, "d": 1.0}

_state = {}


def get(motor_id):
    return _state.setdefault(motor_id, dict(DEFAULT_MOTOR_STATE))
