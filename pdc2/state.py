DEFAULT_MOTOR_STATE = {"h": None, "m": None, "p": 1.0, "d": 1.0}

_state = {}


def get_motor_data(motor_id):
    return _state.setdefault(motor_id, dict(DEFAULT_MOTOR_STATE))


def update_motor_data(motor_id, data):
    old_data = get_motor_data(motor_id)
    old_data.update(**data)
