import displayio
from busio import I2C
from displayio import Group, I2CDisplay

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.bitmap_label import Label
from adafruit_displayio_sh1106 import SH1106

from pdc import config

try:
    from typing import Any, List, Tuple

    WriteCommand = Tuple[int, int, str, bool]
except ImportError:
    Any = ...
    List = ...
    Tuple = ...
    WriteCommand = ...


class Display:
    def __init__(self) -> None:
        displayio.release_displays()

        i2c = I2C(config.DISPLAY_SCL, config.DISPLAY_SDA)
        bus = I2CDisplay(i2c, device_address=config.DISPLAY_ADDRESS)

        self.display = SH1106(
            bus,
            width=config.DISPLAY_WIDTH,
            height=config.DISPLAY_HEIGHT,
            colstart=config.DISPLAY_OFFSET_X,
            auto_refresh=False,
        )

        # workaround - do not show REPL on boot
        self.display.show(Group())
        self.display.auto_refresh = True

        self._font = bitmap_font.load_font(config.FONT_FILENAME)

    def update(self, data: List[WriteCommand]) -> None:
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

            text_area = Label(self._font, text=text, color=0xFFFFFF)
            text_area.x = 0
            text_area.y = (config.FONT_HEIGHT // 2) + config.FONT_HEIGHT * row_idx

            group.append(text_area)

        self.display.show(group)

    def toggle(self) -> None:
        if self.display.is_awake:
            self.display.sleep()
        else:
            self.display.wake()

    @property
    def is_awake(self) -> bool:
        return self.display.is_awake


def init_display() -> Display:
    return Display()


def write(row: int, col: int, text: str, *, cond: Any = True) -> WriteCommand:
    return row, col, text, bool(cond)
