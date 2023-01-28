from adafruit_datetime import datetime

from pdc.hardware import rtc
from pdc2 import state
from pdc2.scenes.base import (
    BUTTON_ESC,
    MenuScene,
    MotorDurationScene,
    MotorPercentageScene,
    MotorTimeScene,
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

    def _get_motor_data(self):
        return state.get("ao")


class MotorAOpenSpeedScene(MotorPercentageScene):
    name = "Speed"

    def _get_motor_data(self):
        return state.get("ao")


class MotorAOpenDurationScene(MotorDurationScene):
    name = "Duration"

    def _get_motor_data(self):
        return state.get("ao")


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
