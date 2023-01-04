import board
import displayio
from busio import I2C
from displayio import Group, I2CDisplay

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_displayio_sh1106 import SH1106

DISPLAY_ADDRESS = 0x3C
DISPLAY_HEIGHT = 64
DISPLAY_SCL = board.GP15
DISPLAY_SDA = board.GP14
DISPLAY_WIDTH = 128
DISPLAY_OFFSET_X = 2

FONT_FILENAME = "/bizcat.pcf"
FONT_HEIGHT = 16


def init_display():
    displayio.release_displays()

    i2c = I2C(DISPLAY_SCL, DISPLAY_SDA)
    bus = I2CDisplay(i2c, device_address=DISPLAY_ADDRESS)

    display = SH1106(
        bus,
        width=DISPLAY_WIDTH,
        height=DISPLAY_HEIGHT,
        colstart=DISPLAY_OFFSET_X,
        auto_refresh=False
    )

    display.show(Group())
    display.auto_refresh = True

    return display


def update_display(display, font, text_lines):
    group = Group()

    for idx, text_line in enumerate(text_lines):
        text_area = Label(font, text=text_line, color=0xFFFFFF)
        text_area.x = 0
        text_area.y = (FONT_HEIGHT // 2) + FONT_HEIGHT * idx

        group.append(text_area)

    display.show(group)


if __name__ == "__main__":
    text_lines = [
        "Motor avg speed:",
        "20%",
        "0123456789:01",
        " S+    S-    OK",
    ]

    font = bitmap_font.load_font(FONT_FILENAME)

    display = init_display()
    update_display(display, font.format(), text_lines)

    while True:
        pass
