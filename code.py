import asyncio
import board
import displayio
import time
from busio import I2C
from displayio import Group, I2CDisplay
from keypad import Keys

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_displayio_sh1106 import SH1106

BUTTON_A = board.GP18
BUTTON_B = board.GP19
BUTTON_C = board.GP20
BUTTON_D = board.GP21

DISPLAY_ADDRESS = 0x3C
DISPLAY_HEIGHT = 64
DISPLAY_SCL = board.GP17
DISPLAY_SDA = board.GP16
DISPLAY_WIDTH = 128
DISPLAY_OFFSET_X = 2

FONT_FILENAME = "/bizcat.pcf"
FONT_HEIGHT = 16


# Scenes

class SceneManager:
    def __init__(self, scenes):
        print(type(scenes))
        self._scenes = list(scenes)

        self._current_id = 0
        self._current = self._scenes[self._current_id]()

    def next_scene(self):
        self._current_id += 1
        if self._current_id == len(self._scenes):
            self._current_id = 0

        self._current = self._scenes[self._current_id]()

    def get_text(self):
        return self._current.text


class IdleScene:
    @property
    def text(self):
        return "IdleScene"


class ManualControlScene:
    @property
    def text(self):
        return "ManualControlScene"


class AutoOpenTimeScene:
    @property
    def text(self):
        return "AutoOpenTimeScene"


class AutoOpenSpeedScene:
    @property
    def text(self):
        return "AutoOpenSpeedScene"


# Display

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


# Keys

def init_keys(*keys):
    # buttons are connected GPIO-button-GND
    return Keys(keys, value_when_pressed=False)


async def handle_key_events(keys):
    while True:
        key_event = keys.events.get()
        if key_event and key_event.released:
            print(f"pressed key: {key_event.key_number}")

        await asyncio.sleep(0)


# Main

async def main():
    text_lines = [
        "Motor avg speed:",
        "20%",
        "0123456789:01",
        " N/A S+  S-  OK",
    ]

    font = bitmap_font.load_font(FONT_FILENAME)

    display = init_display()
    update_display(display, font, text_lines)

    keypad = init_keys(BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D)
    key_event_task = asyncio.create_task(handle_key_events(keypad))

    await asyncio.gather(key_event_task)


def main2():
    scenes = SceneManager([IdleScene, ManualControlScene, AutoOpenTimeScene, AutoOpenSpeedScene])

    while True:
        print(scenes.get_text())
        time.sleep(1)
        scenes.next_scene()


if __name__ == "__main__":
    # asyncio.run(main())
    main2()
