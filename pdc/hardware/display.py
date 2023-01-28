import displayio
import terminalio
from displayio import Group, I2CDisplay

from adafruit_display_text.bitmap_label import Label
from adafruit_displayio_sh1106 import SH1106

from pdc import config, state
from pdc.hardware import i2c

try:
    from typing import Any, List, Tuple

    WriteCommand = Tuple[int, int, str, bool]
except ImportError:
    Any = ...
    List = ...
    Tuple = ...
    WriteCommand = ...

device = None
font = terminalio.FONT


def init_display() -> None:
    global device

    displayio.release_displays()

    bus = I2CDisplay(i2c.device, device_address=config.I2C_ADDRESS_DISPLAY)
    device = SH1106(
        bus,
        width=config.DISPLAY_WIDTH,
        height=config.DISPLAY_HEIGHT,
        colstart=config.DISPLAY_OFFSET_X,
        auto_refresh=False,
        brightness=0.0,
    )

    # workaround - do not show REPL on boot
    device.show(Group())
    device.auto_refresh = True

    if not state.is_display_awake():
        sleep()


def update(data: List[WriteCommand]) -> None:
    buffer_width = config.DISPLAY_WIDTH // config.FONT_WIDTH
    buffer_height = config.DISPLAY_HEIGHT // config.FONT_HEIGHT
    buffer = " " * buffer_width * buffer_height

    for row, col, text, condition in data:
        if condition:
            text_start = row * buffer_width + col
            text_end = text_start + len(text)
            buffer = buffer[:text_start] + text + buffer[text_end:]

    group = Group()

    for row_idx in range(buffer_height):
        text_start = row_idx * buffer_width
        text_end = text_start + buffer_width
        text = buffer[text_start:text_end]

        text_area = Label(font, text=text, color=0xFFFFFF)
        text_area.x = 0
        text_area.y = (config.FONT_HEIGHT // 2) + config.FONT_HEIGHT * row_idx

        group.append(text_area)

    device.show(group)


def sleep() -> None:
    device.sleep()
    state.set_display_awake(False)


def wake() -> None:
    device.wake()
    state.set_display_awake(True)


def toggle() -> None:
    if state.is_display_awake():
        sleep()
    else:
        wake()


def write(row: int, col: int, text: str, *, cond: Any = True) -> WriteCommand:
    return row, col, text, bool(cond)
