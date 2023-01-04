import board
from busio import I2C
from displayio import Group, I2CDisplay, release_displays

from adafruit_bitmap_font.bitmap_font import load_font
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

        self.font = load_font(FONT_FILENAME)

    def update(self, text: str) -> None:
        group = Group()

        for idx, text_line in enumerate(text.splitlines()):
            text_area = Label(self.font, text=text_line, color=0xFFFFFF)
            text_area.x = 0
            text_area.y = (FONT_HEIGHT // 2) + FONT_HEIGHT * idx

            group.append(text_area)

        self.display.show(group)


if __name__ == "__main__":
    text = "Motor avg speed:\n20%\n0123456789:01\n S+    S-    OK "

    display = Display()
    display.update(text)

    while True:
        pass
