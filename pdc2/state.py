import json
import time

from adafruit_datetime import datetime

from pdc.hardware import eeprom

DEFAULT_MOTOR_STATE = {"h": None, "m": None, "p": 1.0, "d": 1.0}

_state = {}


def get_motor_data(motor_id):
    return _state.setdefault(motor_id, dict(DEFAULT_MOTOR_STATE))


def update_motor_data(motor_id, data):
    old_data = get_motor_data(motor_id)
    old_data.update(**data)

    save_to_eeprom()


def append_oneshot_motor_data(motor_id):
    dt = datetime.now()

    data = dict(get_motor_data(motor_id))
    data["h"] = dt.hour
    data["m"] = dt.minute
    data["1"] = True
    data["t"] = time.time()

    _state[motor_id + "1"] = data


def load_from_eeprom():
    raw = eeprom.load()

    data = json.loads(raw)
    assert type(data) is dict

    _state.clear()
    _state.update(**data)


def save_to_eeprom():
    data = {}

    for key, value in _state.items():
        print(key, value)
        if not key.endswith("1"):
            data[key] = {k: value.get(k) for k in ("h", "m", "p", "d")}

    raw = json.dumps(data)
    eeprom.dump(raw)
