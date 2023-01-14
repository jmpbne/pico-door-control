from adafruit_datetime import datetime

from pdc import config

try:
    from typing import Any
except ImportError:
    Any = ...

DISPLAY_AWAKE = "display_awake"
OPENING_COOLDOWN = "opening_cooldown"
OPENING_DURATION = "opening_duration"
OPENING_DUTY_CYCLE = "opening_duty_cycle"
OPENING_TIME = "opening_time"

_state = {
    DISPLAY_AWAKE: True,
    OPENING_COOLDOWN: False,
    OPENING_DURATION: config.MOTOR_DURATION_DEFAULT,
    OPENING_DUTY_CYCLE: config.MOTOR_DUTY_CYCLE_DEFAULT,
    OPENING_TIME: None,
}


def get(key: str) -> Any:
    return _state.get(key)


def put(key: str, value: Any) -> None:
    if get(key) != value:
        _state[key] = value
        print("New state:", _state)


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
