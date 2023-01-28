import asyncio
import math

from adafruit_datetime import time

from pdc.hardware import display, keys
from pdc2 import state
from pdc2.scenes.exceptions import SceneValueError

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


class MessageScene(Scene):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.message = "No message"

    def handle_event(self, event):
        self.manager.switch_to_parent_scene()

    @property
    def display_data(self):
        return [
            display.write(0, 0, self.message),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_D_COL, "   OK>"),
        ]


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

    def _get_output_value(self):
        return int("".join(str(d) for d in self.current_digits))

    def _increment_digit(self, position):
        digit = self.current_digits[position]

        if digit == 9:
            digit = 0
        else:
            digit += 1

        self.current_digits[position] = digit

    def _set_input_value(self, value):
        for idx in range(4):
            value, self.current_digits[3 - idx] = divmod(value, 10)

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
        if event.key_number == BUTTON_ESC:
            self.manager.switch_to_parent_scene()
        if event.key_number == BUTTON_OK:
            try:
                self.handle_save()
            except SceneValueError:
                print("Ignoring invalid scene value")
            else:
                self.manager.switch_to_parent_scene()

    def handle_save(self):
        value = self._get_output_value()

        print(f"Current value: {value}")
        return value

    @property
    def display_data(self):
        return [
            display.write(DISPLAY_VALUE_ROW, 4, self._get_digit_str(0)),
            display.write(DISPLAY_VALUE_ROW, 8, self._get_digit_str(1)),
            display.write(DISPLAY_VALUE_ROW, 12, self._get_digit_str(2)),
            display.write(DISPLAY_VALUE_ROW, 16, self._get_digit_str(3)),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_A_COL, "<Cancel"),
            display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_D_COL, "   OK>"),
        ]


class TimeScene(NumberScene):
    def _get_output_value(self):
        if all(d is None for d in self.current_digits):
            return None

        try:
            hh = self.current_digits[0] * 10 + self.current_digits[1]
            mm = self.current_digits[2] * 10 + self.current_digits[3]
            return time(hh, mm)
        except (TypeError, ValueError):
            raise SceneValueError

    def _increment_digit(self, position):
        digit = self.current_digits[position]

        if digit is None:
            digit = 0
        elif position == 0 and digit == 2:
            digit = None
        elif position != 0 and digit == 9:
            digit = None
        else:
            digit += 1

        self.current_digits[position] = digit

    def _set_input_value(self, value):
        if value is None:
            self.current_digits = [None, None, None, None]
            return

        h1, h2 = divmod(value.hour, 10)
        m1, m2 = divmod(value.minute, 10)

        self.current_digits = [h1, h2, m1, m2]

    @property
    def display_data(self):
        data = super().display_data
        data.append(display.write(DISPLAY_VALUE_ROW, 10, ":"))

        return data


class MotorTimeScene(TimeScene):
    motor_id = None

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self._set_input_value(state.get_motor_data(self.motor_id))

    def _get_output_value(self):
        value = super()._get_output_value()
        if value:
            return {"h": value.hour, "m": value.minute}
        else:
            return {"h": None, "m": None}

    def _set_input_value(self, value):
        try:
            h1, h2 = divmod(value.get("h"), 10)
            m1, m2 = divmod(value.get("m"), 10)
            self.current_digits = [h1, h2, m1, m2]
        except TypeError:
            self.current_digits = [None, None, None, None]

    def handle_save(self):
        value = self._get_output_value()

        state.update_motor_data(self.motor_id, value)
        return value


class PercentageScene(NumberScene):
    def _get_output_value(self):
        value = super()._get_output_value()
        if not (0 <= value <= 1000):
            raise SceneValueError

        return value / 1000.0

    def _increment_digit(self, position):
        digit = self.current_digits[position]

        if position == 0 and digit == 1:
            digit = 0
        elif position != 0 and digit == 9:
            digit = 0
        else:
            digit += 1

        self.current_digits[position] = digit

    def _set_input_value(self, value):
        super()._set_input_value(math.ceil(value * 1000))

    @property
    def display_data(self):
        data = super().display_data
        data.append(display.write(DISPLAY_VALUE_ROW, 14, "."))
        data.append(display.write(DISPLAY_VALUE_ROW, 18, "%"))

        return data


class MotorPercentageScene(PercentageScene):
    motor_id = None

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self._set_input_value(state.get_motor_data(self.motor_id).get("p"))

    def handle_save(self):
        value = self._get_output_value()

        state.update_motor_data(self.motor_id, {"p": value})
        return value


class DurationScene(NumberScene):
    def _get_output_value(self):
        return super()._get_output_value() / 10.0

    def _set_input_value(self, value):
        super()._set_input_value(math.ceil(value * 10))

    @property
    def display_data(self):
        data = super().display_data
        data.append(display.write(DISPLAY_VALUE_ROW, 14, "."))
        data.append(display.write(DISPLAY_VALUE_ROW, 18, "s"))

        return data


class MotorDurationScene(DurationScene):
    motor_id = None

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self._set_input_value(state.get_motor_data(self.motor_id).get("d"))

    def handle_save(self):
        value = self._get_output_value()

        state.update_motor_data(self.motor_id, {"d": value})
        return value


class SceneManager:
    def __init__(self, start_scene_class):
        self.current_scene = None
        self.switch_to_new_scene(start_scene_class)

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
            if key_event and key_event.pressed:
                self.current_scene.handle_event(key_event)

            await asyncio.sleep(0)
