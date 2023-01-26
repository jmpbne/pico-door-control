import asyncio

from adafruit_datetime import time

from pdc.hardware import display, keys

DISPLAY_BUTTON_A_COL = 0
DISPLAY_BUTTON_B_COL = 5
DISPLAY_BUTTON_C_COL = 10
DISPLAY_BUTTON_D_COL = 15
DISPLAY_LAST_ROW = 4
DISPLAY_MENU_CURSOR_ROW = 1
DISPLAY_MENU_ROWS = 4
DISPLAY_VALUE_ROW = 1

BUTTON_A = 0
BUTTON_B = 1
BUTTON_C = 2
BUTTON_D = 3
BUTTON_ESC = 4
BUTTON_OK = 5


# Base scenes


class Scene:
    def __init__(self, manager, parent=None):
        self.manager = manager
        self.parent = parent

    def handle_event(self, event):
        self.refresh_screen()

    def refresh_screen(self):
        display.update(self.display_data)

    @property
    def display_data(self):
        return [display.write(0, 0, self.__class__.__name__)]


class MenuScene(Scene):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)

        self.entries = []
        self.cursor_position = 0

    def handle_event(self, event):
        if event.key_number == BUTTON_B:
            if self.cursor_position > 0:
                self.cursor_position -= 1
                self.refresh_screen()
        if event.key_number == BUTTON_C:
            if self.cursor_position < len(self.entries) - 1:
                self.cursor_position += 1
                self.refresh_screen()
        if event.key_number == BUTTON_ESC:
            self.manager.switch_to_parent_scene()
        if event.key_number == BUTTON_OK:
            self.manager.switch_to_new_scene(self.entries[self.cursor_position])

    @property
    def display_data(self):
        data = [
            display.write(DISPLAY_MENU_CURSOR_ROW, 0, "*"),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_A_COL, "<Back "),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_B_COL, "  Up  "),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_C_COL, " Down "),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_D_COL, "   OK>"),
        ]

        for idx in range(DISPLAY_MENU_ROWS):
            position = self.cursor_position - 1 + idx
            if 0 <= position < len(self.entries):
                screen_class = self.entries[position]
                try:
                    name = screen_class.name
                except AttributeError:
                    name = screen_class.__name__

                data.append(display.write(idx, 1, name))

        return data


class NumberScene(Scene):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.current_digits = [0, 0, 0, 0]

    def _get_digit_str(self, position):
        digit = self.current_digits[position]

        if digit is None:
            return "-"
        if digit == 0:
            return "O"

        return str(digit)

    def _get_current_value(self):
        return int("".join(str(d) for d in self.current_digits))

    def _increment_digit(self, position):
        _, digit = divmod(self.current_digits[position] + 1, 10)
        self.current_digits[position] = digit

    def handle_event(self, event):
        if event.key_number == BUTTON_A:
            self._increment_digit(0)
            self.refresh_screen()
        if event.key_number == BUTTON_B:
            self._increment_digit(1)
            self.refresh_screen()
        if event.key_number == BUTTON_C:
            self._increment_digit(2)
            self.refresh_screen()
        if event.key_number == BUTTON_D:
            self._increment_digit(3)
            self.refresh_screen()
        if event.key_number == BUTTON_OK:
            print(f"DEBUG current value: {self._get_current_value()}")
            self.manager.switch_to_parent_scene()

    @property
    def display_data(self):
        return [
            display.write(DISPLAY_VALUE_ROW, 4, self._get_digit_str(0)),
            display.write(DISPLAY_VALUE_ROW, 8, self._get_digit_str(1)),
            display.write(DISPLAY_VALUE_ROW, 12, self._get_digit_str(2)),
            display.write(DISPLAY_VALUE_ROW, 16, self._get_digit_str(3)),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_D_COL, "   OK>"),
        ]


class TimeScene(NumberScene):
    def _get_current_value(self):
        hh_str = self.current_digits[0] * 10 + self.current_digits[1]
        mm_str = self.current_digits[2] * 10 + self.current_digits[3]

        return time(hh_str, mm_str)

    @property
    def display_data(self):
        data = super().display_data
        data.append(display.write(DISPLAY_VALUE_ROW, 10, ":"))

        return data


class PercentageScene(NumberScene):
    def _get_current_value(self):
        return super()._get_current_value() / 1000.0

    @property
    def display_data(self):
        data = super().display_data
        data.append(display.write(DISPLAY_VALUE_ROW, 14, "."))
        data.append(display.write(DISPLAY_VALUE_ROW, 18, "%"))

        return data


class DurationScene(NumberScene):
    def _get_current_value(self):
        return super()._get_current_value() / 10.0

    @property
    def display_data(self):
        data = super().display_data
        data.append(display.write(DISPLAY_VALUE_ROW, 14, "."))
        data.append(display.write(DISPLAY_VALUE_ROW, 18, "s"))

        return data


# Scene implementations


class ScreenOffScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_ESC:
            self.manager.switch_to_new_scene(MainMenuScene)

    @property
    def display_data(self):
        return []


class MainMenuScene(MenuScene):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAMenuScene, Scene, Scene]


class MotorAMenuScene(MenuScene):
    name = "Motor A"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAOpenMenuScene, Scene]


class MotorAOpenMenuScene(MenuScene):
    name = "Opening settings"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorAOpenNowScene,
            MotorAOpenTimeScene,
            MotorAOpenSpeedScene,
            MotorAOpenDurationScene,
        ]


class MotorAOpenNowScene(Scene):
    name = "Open now"


class MotorAOpenTimeScene(TimeScene):
    name = "Time"


class MotorAOpenSpeedScene(PercentageScene):
    name = "Speed"


class MotorAOpenDurationScene(DurationScene):
    name = "Duration"


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.switch_to_new_scene(ScreenOffScene)

    def switch_to_scene(self, scene):
        self.current_scene = scene
        self.current_scene.refresh_screen()

    def switch_to_new_scene(self, scene_class):
        self.switch_to_scene(scene_class(self, parent=self.current_scene))

    def switch_to_parent_scene(self):
        self.switch_to_scene(self.current_scene.parent)

    async def poll(self):
        keys_device = keys.device

        while True:
            key_event = keys_device.events.get()
            if key_event and key_event.released:
                self.current_scene.handle_event(key_event)

            await asyncio.sleep(0)
