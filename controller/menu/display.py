import busio
import displayio
import terminalio

from adafruit_display_text.bitmap_label import Label
from adafruit_displayio_sh1106 import SH1106

from controller import config

DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_XOFFSET = 2

FONT_WIDTH = 6
FONT_HEIGHT = 9

displayio.release_displays()

i2c = busio.I2C(config.I2C_DISPLAY_SCL, config.I2C_DISPLAY_SDA)
display_bus = displayio.I2CDisplay(i2c, device_address=config.I2C_DISPLAY_ADDRESS)

display = SH1106(
    display_bus,
    width=DISPLAY_WIDTH,
    height=DISPLAY_HEIGHT,
    colstart=DISPLAY_XOFFSET,
    auto_refresh=False,
    brightness=0.0,
)


def init():
    display.show(displayio.Group())
    display.auto_refresh = True


def render(commands):
    group = displayio.Group()

    for x, y, text in commands:
        label = Label(terminalio.FONT, text=text, color=0xFFFFFF)
        label.x = int(FONT_WIDTH * x)
        label.y = int(FONT_HEIGHT * (y + 0.5))

        group.append(label)

    display.show(group)
