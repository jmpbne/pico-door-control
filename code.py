import board
from busio import I2C
from displayio import Group, I2CDisplay, release_displays

from adafruit_displayio_sh1106 import SH1106

DISPLAY_ADDRESS = 0x3C
DISPLAY_HEIGHT = 64
DISPLAY_SCL = board.GP15
DISPLAY_SDA = board.GP14
DISPLAY_WIDTH = 128
DISPLAY_OFFSET_X = 2


class Display:
    def __init__(self) -> None:
        release_displays()

        i2c = I2C(DISPLAY_SCL, DISPLAY_SDA)
        bus = I2CDisplay(i2c, device_address=DISPLAY_ADDRESS)

        self.display = SH1106(
            bus,
            width=DISPLAY_WIDTH,
            height=DISPLAY_HEIGHT,
            colstart=DISPLAY_OFFSET_X,
            auto_refresh=False
        )

        self.display.show(Group())
        self.display.auto_refresh = True


if __name__ == "__main__":
    display = Display()

    while True:
        pass
