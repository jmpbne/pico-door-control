from adafruit_datetime import datetime

try:
    from typing import Optional
except ImportError:
    Optional = ...


def datetime_to_timearray(dt: datetime) -> list[int]:
    if not dt:
        return [0, 0, 0, 0]

    a, b = divmod(dt.hour, 10)
    c, d = divmod(dt.minute, 10)

    return [a, b, c, d]


def format_datetime(dt: Optional[datetime]) -> str:
    if not dt:
        return "--:--"

    return f"{dt.hour:02}:{dt.minute:02}"


def format_timearray(arr: list[int]) -> str:
    h1, h2, m1, m2 = arr
    return f"{h1}{h2}:{m1}{m2}"


def format_timearray_cursor(position: int) -> str:
    if position > 1:
        position += 1

    return " " * position + "‾"


def get_max_value_for_timearray_digit(position: int) -> int:
    if position == 0:
        return 2
    if position == 2:
        return 5

    return 9


def is_timearray_valid(arr: list[int]) -> bool:
    try:
        timearray_to_datetime(arr)
    except ValueError:
        return False
    else:
        return True


def timearray_to_datetime(arr: list[int]) -> datetime:
    hour = 10 * arr[0] + arr[1]
    minute = 10 * arr[2] + arr[3]

    return datetime(2000, 1, 1, hour, minute, 0)
