from adafruit_datetime import datetime

from pdc.hardware import rtc
from pdc2 import state
from pdc2.scenes.base import (
    BUTTON_ESC,
    DurationScene,
    MenuScene,
    MotorTimeScene,
    PercentageScene,
    Scene,
    TimeScene,
)
from pdc2.scenes.exceptions import SceneValueError


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
        self.entries = [MotorAMenuScene, Scene, SystemTimeScene]


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


class MotorAOpenTimeScene(MotorTimeScene):
    name = "Time"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self._set_input_value(self._get_motor_data())

    def _get_motor_data(self):
        return state.get("ao")

    def handle_save(self):
        value = self._get_output_value()

        self._get_motor_data().update(**value)
        return value


class MotorAOpenSpeedScene(PercentageScene):
    name = "Speed"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self._set_input_value(self._get_motor_data().get("p"))

    def _get_motor_data(self):
        return state.get("ao")

    def handle_save(self):
        value = self._get_output_value()

        self._get_motor_data()["p"] = value
        return value


class MotorAOpenDurationScene(DurationScene):
    name = "Duration"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self._set_input_value(self._get_motor_data().get("d"))

    def _get_motor_data(self):
        return state.get("ao")

    def handle_save(self):
        value = self._get_output_value()

        self._get_motor_data()["d"] = value
        return value


class SystemTimeScene(TimeScene):
    name = "System time"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)

        if rtc.device.lost_power:
            self._set_input_value(None)
        else:
            self._set_input_value(datetime.now())

    def handle_save(self):
        value = super().handle_save()
        if value is None:
            raise SceneValueError

        dt = datetime(2000, 1, 1, value.hour, value.minute, 0)
        rtc.device.datetime = dt.timetuple()

        return value
