# Built-in
import board
import displayio
import rtc
from busio import I2C
from displayio import Group, I2CDisplay
from keypad import Keys

# CircuitPython library bundle
import asyncio
from adafruit_bitmap_font import bitmap_font
from adafruit_datetime import datetime, time
from adafruit_display_text.label import Label
from adafruit_displayio_sh1106 import SH1106

BUTTON_A = board.GP18
BUTTON_B = board.GP19
BUTTON_C = board.GP20
BUTTON_D = board.GP21
BUTTONS = [BUTTON_A, BUTTON_B, BUTTON_C, BUTTON_D]
BUTTONS_VALUE_WHEN_PRESSED = False  # True = VCC, False = GND

DISPLAY_ADDRESS = 0x3C
DISPLAY_HEIGHT = 64
DISPLAY_SCL = board.GP17
DISPLAY_SDA = board.GP16
DISPLAY_OFFSET_X = 2
DISPLAY_WIDTH = 128

FONT_FILENAME = "/bizcat.pcf"
FONT_HEIGHT = 16

MOTOR_MIN_SPEED = 20
MOTOR_MAX_SPEED = 100

LOCALE = "pl"


# Translations

TRANSLATIONS = {
    "en": {
        "Reset": "Reset",
        "OK": "  OK",
        "Open time": "Open time",
        "Manual control": "Manual control",
    },
    "pl": {
        "Reset": "Reset",
        "OK": "  OK",
        "Open time": "Czas otwarcia",
        "Manual control": "Sterowanie reczne",
    },
}


def _(phrase):
    try:
        return TRANSLATIONS[LOCALE][phrase]
    except KeyError:
        return "???"


# Menu


class MenuManager:
    """
    This class is responsible for controlling the input and output
    (OLED display module and buttons).
    """

    def __init__(self, *, scenes, display, keys):
        self.display = display
        self.keys = keys

        self.scenes = list(scenes)
        self.current_scene_id = None
        self.current_scene = None

        self.switch_to_scene(0)

    def switch_to_scene(self, scene_id):
        if self.current_scene:
            self.current_scene.on_exit()

        if scene_id == len(self.scenes):
            scene_id = 0

        self.current_scene_id = scene_id
        self.current_scene = self.scenes[self.current_scene_id](self)
        self.current_scene.on_enter()

    def switch_to_next_scene(self):
        self.switch_to_scene(self.current_scene_id + 1)

    async def task(self):
        while True:
            key_event = self.keys.events.get()
            if key_event and key_event.released:
                self.current_scene.on_press(key_event)

            await asyncio.sleep(0)


class Scene:
    def __init__(self, manager):
        self.manager = manager

    def on_enter(self):
        self.update_display()
        print(f"enter {self.__class__.__name__}")

    def on_press(self, event):
        self.manager.switch_to_next_scene()

    def on_exit(self):
        print(f"leave {self.__class__.__name__}")

    def update_display(self):
        self.manager.display.update(self.text_lines)

    @property
    def text_lines(self):
        return [self.__class__.__name__]


class IdleScene(Scene):
    pass


class ManualControlScene(Scene):
    def on_press(self, event):
        if event.key_number == 1:
            print("close the door")
        elif event.key_number == 2:
            print("open the door")
        elif event.key_number == 3:
            super().on_press(event)

    @property
    def text_lines(self):
        return [
            _("Manual control"),
            "",
            "",
            f"      v  ^  {_('OK')}",
        ]


class AutoOpenTimeScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = [0, 0, 0, 0]
        self.default_time = [0, 0, 0, 0]

        self.cursor_position = 0

    def on_press(self, event):
        if event.key_number == 0:
            self.time = list(self.default_time)
            self.update_display()
        elif event.key_number == 1:
            digit = self.time[self.cursor_position]
            digit += 1
            if digit > self._get_max_digit(self.cursor_position):
                digit = 0
            self.time[self.cursor_position] = digit
            self.update_display()
        elif event.key_number == 2:
            pos = self.cursor_position
            pos += 1
            if pos == len(self.time):
                pos = 0
            self.cursor_position = pos
            self.update_display()
        elif event.key_number == 3:
            if self._is_date_valid():
                super().on_press(event)

    def _is_date_valid(self):
        hour = 10 * self.time[0] + self.time[1]
        minute = 10 * self.time[2] + self.time[3]

        try:
            time(hour, minute)
        except ValueError:
            return False
        else:
            return True

    def _get_max_digit(self, position):
        if position == 0:
            return 2
        if position == 2:
            return 5

        return 9

    def _get_time_string(self):
        return f"{self.time[0]}{self.time[1]}:{self.time[2]}{self.time[3]}"

    def _get_cursor_string(self):
        pos = self.cursor_position
        if pos > 1:
            pos += 1  # offset for colon

        return " " * pos + "^"

    @property
    def text_lines(self):
        ok_str = _("OK") if self._is_date_valid() else ""

        return [
            _("Open time"),
            self._get_time_string(),
            self._get_cursor_string(),
            f"{_('Reset')} v  >  {ok_str}",
        ]


# Display


class Display:
    def __init__(self):
        displayio.release_displays()

        i2c = I2C(DISPLAY_SCL, DISPLAY_SDA)
        bus = I2CDisplay(i2c, device_address=DISPLAY_ADDRESS)

        self.display = SH1106(
            bus,
            width=DISPLAY_WIDTH,
            height=DISPLAY_HEIGHT,
            colstart=DISPLAY_OFFSET_X,
            auto_refresh=False,
        )

        # workaround - do not show REPL on boot
        self.display.show(Group())
        self.display.auto_refresh = True

        self.font = bitmap_font.load_font(FONT_FILENAME)

    def update(self, text_lines):
        group = Group()

        for idx, text_line in enumerate(text_lines):
            text_area = Label(self.font, text=text_line, color=0xFFFFFF)
            text_area.x = 0
            text_area.y = (FONT_HEIGHT // 2) + FONT_HEIGHT * idx

            group.append(text_area)

        self.display.show(group)


def init_display():
    return Display()


# Keys


def init_keys():
    return Keys(BUTTONS, value_when_pressed=BUTTONS_VALUE_WHEN_PRESSED)


# Clock


def init_clock():
    clock = rtc.RTC()
    clock.datetime = datetime(2000, 1, 1, 0, 0, 0).timetuple()

    return clock


# Main


async def main():
    display = init_display()
    keys = init_keys()
    init_clock()

    menu = MenuManager(
        scenes=[IdleScene, ManualControlScene, AutoOpenTimeScene],
        display=display,
        keys=keys,
    )

    await asyncio.create_task(menu.task())


if __name__ == "__main__":
    asyncio.run(main())
