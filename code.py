# Built-in
import board
import displayio
from busio import I2C
from digitalio import DigitalInOut, Direction
from displayio import Group, I2CDisplay
from keypad import Keys
from rtc import RTC

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

LOCALE = "pl"

MOTOR_PHASE_A = board.GP26
MOTOR_PHASE_B = board.GP27


# Translations

TRANSLATIONS = {
    "en": {
        "Current time": "Current time",
        "Manual control": "Manual control",
        "OK": "  OK",
        "Open time": "Open time",
        "Reset": "Reset",
    },
    "pl": {
        "Current time": "Aktualny czas",
        "Manual control": "Sterowanie reczne",
        "OK": "  OK",
        "Open time": "Czas otwarcia",
        "Reset": "Reset",
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
    def __init__(self, manager):
        super().__init__(manager)
        self.update_clock_task = None

    def on_enter(self):
        super().on_enter()
        self.update_clock_task = asyncio.create_task(self.update_clock())

    def on_exit(self):
        super().on_exit()
        self.update_clock_task.cancel()

    async def update_clock(self):
        while True:
            await asyncio.sleep(5)
            self.update_display()

    @property
    def text_lines(self):
        time = datetime.now()
        return [f"{time.hour:02}:{time.minute:02}"]


class ManualControlScene(Scene):
    BACKWARDS = 0
    FORWARDS = 1

    def __init__(self, manager):
        super().__init__(manager)
        self.manual_control_task = None

    def on_press(self, event):
        if self.manual_control_task:
            return

        if event.key_number == 1:
            coro = self.manual_control(ManualControlScene.BACKWARDS)
            self.manual_control_task = asyncio.create_task(coro)
            self.update_display()
        elif event.key_number == 2:
            coro = self.manual_control(ManualControlScene.FORWARDS)
            self.manual_control_task = asyncio.create_task(coro)
            self.update_display()
        elif event.key_number == 3:
            super().on_press(event)

    async def manual_control(self, direction):
        phase_a = DigitalInOut(MOTOR_PHASE_A)
        phase_a.direction = Direction.OUTPUT

        phase_b = DigitalInOut(MOTOR_PHASE_B)
        phase_b.direction = Direction.OUTPUT

        if direction == ManualControlScene.BACKWARDS:
            phase_a.value = True
            phase_b.value = False
        elif direction == ManualControlScene.FORWARDS:
            phase_a.value = False
            phase_b.value = True

        await asyncio.sleep(1.0)

        phase_a.value = False
        phase_b.value = False

        self.manual_control_task = None
        self.update_display()

    @property
    def text_lines(self):
        if not self.manual_control_task:
            last_line = f"      v  ^  {_('OK')}"
        else:
            last_line = ""

        return [
            _("Manual control"),
            "",
            "",
            last_line,
        ]


class AbstractTimeScene(Scene):
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
        try:
            self._array_to_datetime(self.time)
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

    def _datetime_to_array(self, datetime):
        a, b = divmod(datetime.hour, 10)
        c, d = divmod(datetime.minute, 10)

        return [a, b, c, d]

    def _array_to_datetime(self, array):
        hour = 10 * array[0] + array[1]
        minute = 10 * array[2] + array[3]

        return datetime(2000, 1, 1, hour, minute, 0)

    def _get_time_string(self):
        return f"{self.time[0]}{self.time[1]}:{self.time[2]}{self.time[3]}"

    def _get_cursor_string(self):
        pos = self.cursor_position
        if pos > 1:
            pos += 1  # offset for colon

        return " " * pos + "^"


class AutoOpenTimeScene(AbstractTimeScene):
    @property
    def text_lines(self):
        ok_str = _("OK") if self._is_date_valid() else ""

        return [
            _("Open time"),
            self._get_time_string(),
            self._get_cursor_string(),
            f"{_('Reset')} v  >  {ok_str}",
        ]


class CurrentTimeScene(AbstractTimeScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = self._datetime_to_array(datetime.now())
        self.default_time = list(self.time)

    def on_exit(self):
        if self.default_time != self.time:
            dt = self._array_to_datetime(self.time)
            RTC().datetime = dt.timetuple()
            print("setting up new time")
        else:
            print("no time change")

        super().on_exit()

    @property
    def text_lines(self):
        ok_str = _("OK") if self._is_date_valid() else ""

        return [
            _("Current time"),
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
    clock = RTC()
    clock.datetime = datetime(2000, 1, 1, 0, 0, 0).timetuple()

    return clock


# Main


async def main():
    display = init_display()
    keys = init_keys()
    init_clock()

    menu = MenuManager(
        scenes=[IdleScene, ManualControlScene, AutoOpenTimeScene, CurrentTimeScene],
        display=display,
        keys=keys,
    )

    await menu.task()


if __name__ == "__main__":
    asyncio.run(main())
