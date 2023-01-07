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

# Custom code
from pdc.date import (
    datetime_to_timearray,
    format_datetime,
    format_timearray,
    format_timearray_cursor,
    get_max_value_for_timearray_digit,
    is_timearray_valid,
    timearray_to_datetime,
)

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

OPENING_TIME = None

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

        self.scheduled_control_task = None
        self.update_clock_task = None

    def on_enter(self):
        super().on_enter()
        self.update_clock_task = asyncio.create_task(self.update_clock())

    def on_exit(self):
        super().on_exit()
        self.update_clock_task.cancel()

    def on_press(self, event):
        if self.scheduled_control_task:
            return

        super().on_press(event)

    async def scheduled_control(self):
        self.update_display()

        # todo: encapsulate and reuse motor code (create, deinit, control)
        phase_a = DigitalInOut(MOTOR_PHASE_A)
        phase_a.direction = Direction.OUTPUT
        phase_a.value = False

        phase_b = DigitalInOut(MOTOR_PHASE_B)
        phase_b.direction = Direction.OUTPUT
        phase_b.value = True

        await asyncio.sleep(5.0)

        phase_a.value = False
        phase_b.value = False

        phase_a.deinit()
        phase_b.deinit()

        self.scheduled_control_task = None
        self.update_display()

    async def update_clock(self):
        while True:
            if OPENING_TIME:
                d = datetime.now()
                now_time = d.hour, d.minute
                opening_time = OPENING_TIME.hour, OPENING_TIME.minute

                if now_time == opening_time and not self.scheduled_control_task:
                    # todo: open door only once
                    print("opening the door automatically...", datetime.now())
                    coro = self.scheduled_control()
                    self.scheduled_control_task = asyncio.create_task(coro)
                else:
                    print("not opening door", datetime.now())

            await asyncio.sleep(5)
            self.update_display()

    @property
    def text_lines(self):
        current_time_fmt = format_datetime(datetime.now())
        opening_time_fmt = format_datetime(OPENING_TIME)

        if self.scheduled_control_task:
            is_opening_str = "opening..."  # TODO: translate
        else:
            is_opening_str = ""

        return [f"{current_time_fmt}  ->  {opening_time_fmt}", "", "", is_opening_str]


class ManualControlScene(Scene):
    BACKWARDS = 0
    FORWARDS = 1

    def __init__(self, manager):
        super().__init__(manager)
        self.manual_control_task = None
        self.phase_a = None
        self.phase_b = None

    def on_exit(self):
        super().on_enter()

        if self.phase_a:
            self.phase_a.deinit()
        if self.phase_b:
            self.phase_b.deinit()

    def on_press(self, event):
        if self.manual_control_task:
            return

        if event.key_number == 1:
            coro = self.manual_control(ManualControlScene.BACKWARDS)
            self.manual_control_task = asyncio.create_task(coro)
        elif event.key_number == 2:
            coro = self.manual_control(ManualControlScene.FORWARDS)
            self.manual_control_task = asyncio.create_task(coro)
        elif event.key_number == 3:
            super().on_press(event)

    async def manual_control(self, direction):
        self.update_display()

        if not self.phase_a:
            self.phase_a = DigitalInOut(MOTOR_PHASE_A)
            self.phase_a.direction = Direction.OUTPUT
        if not self.phase_b:
            self.phase_b = DigitalInOut(MOTOR_PHASE_B)
            self.phase_b.direction = Direction.OUTPUT

        if direction == ManualControlScene.BACKWARDS:
            self.phase_a.value = True
            self.phase_b.value = False
        elif direction == ManualControlScene.FORWARDS:
            self.phase_a.value = False
            self.phase_b.value = True

        await asyncio.sleep(1.0)

        self.phase_a.value = False
        self.phase_b.value = False

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
            if digit > get_max_value_for_timearray_digit(self.cursor_position):
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
            if is_timearray_valid(self.time):
                super().on_press(event)


class AutoOpenTimeScene(AbstractTimeScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = datetime_to_timearray(OPENING_TIME)
        self.default_time = list(self.time)

    def on_exit(self):
        global OPENING_TIME  # todo: do not use global variables

        if self.time != self.default_time:
            OPENING_TIME = timearray_to_datetime(self.time)
            print("setting up new opening time")
        else:
            print("no opening time change")

        super().on_exit()

    @property
    def text_lines(self):
        if is_timearray_valid(self.time):
            ok_str = _("OK")
        else:
            ok_str = ""

        return [
            _("Open time"),
            format_timearray(self.time),
            format_timearray_cursor(self.cursor_position),
            f"{_('Reset')} v  >  {ok_str}",
        ]


class CurrentTimeScene(AbstractTimeScene):
    def __init__(self, manager):
        super().__init__(manager)

        self.time = datetime_to_timearray(datetime.now())
        self.default_time = list(self.time)

    def on_exit(self):
        if self.time != self.default_time:
            dt = timearray_to_datetime(self.time)
            RTC().datetime = dt.timetuple()
            print("setting up new current time")
        else:
            print("no current time change")

        super().on_exit()

    @property
    def text_lines(self):
        if is_timearray_valid(self.time):
            ok_str = _("OK")
        else:
            ok_str = ""

        return [
            _("Current time"),
            format_timearray(self.time),
            format_timearray_cursor(self.cursor_position),
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
