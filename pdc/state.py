import json

from adafruit_datetime import datetime

from pdc import config
from pdc.hardware import eeprom

try:
    from typing import Any
except ImportError:
    Any = ...

DISPLAY_AWAKE = "da"
OPENING_COOLDOWN = "oc"
OPENING_DURATION = "od"
OPENING_DUTY_CYCLE = "op"
OPENING_TIME = "ot"

DEFAULT_VALUES = {
    DISPLAY_AWAKE: True,
    OPENING_COOLDOWN: False,
    OPENING_DURATION: config.MOTOR_DURATION_DEFAULT,
    OPENING_DUTY_CYCLE: config.MOTOR_DUTY_CYCLE_DEFAULT,
    OPENING_TIME: None,
}

_state = {}


def dump_to_eeprom() -> None:
    raw = json.dumps(
        {k: dump_value(v) for k, v in _state.items()}, separators=(",", ":")
    )
    eeprom.dump(raw)


def dump_value(value: Any) -> Any:
    try:
        return value.isoformat()
    except AttributeError:
        return value


def load_from_eeprom() -> None:
    raw = eeprom.load()

    _state.clear()
    _state.update({k: load_value(v) for k, v in json.loads(raw).items()})


def load_value(value: Any) -> Any:
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return value


def get(key: str) -> Any:
    return _state.get(key, DEFAULT_VALUES.get(key))


def put(key: str, value: Any) -> None:
    if get(key) != value:
        _state[key] = value
        dump_to_eeprom()


def is_display_awake() -> bool:
    return get(DISPLAY_AWAKE)


def is_opening_cooldown() -> bool:
    return get(OPENING_COOLDOWN)


def get_opening_duration() -> int:
    return get(OPENING_DURATION)


def get_opening_duty_cycle() -> int:
    return get(OPENING_DUTY_CYCLE)


def get_opening_time() -> datetime:
    return get(OPENING_TIME)


def set_display_awake(value: bool) -> None:
    put(DISPLAY_AWAKE, value)


def set_opening_cooldown(value: bool) -> None:
    put(OPENING_COOLDOWN, value)


def set_opening_duration(value: int) -> None:
    put(OPENING_DURATION, value)


def set_opening_duty_cycle(value: int) -> None:
    put(OPENING_DUTY_CYCLE, value)


def set_opening_time(value: datetime) -> None:
    put(OPENING_TIME, value)
