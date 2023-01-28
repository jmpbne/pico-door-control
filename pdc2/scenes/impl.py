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
        self.entries = [MotorAMenuScene, MotorBMenuScene, SystemTimeScene]


class MotorAMenuScene(MenuScene):
    name = "Motor A"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAOpenMenuScene, MotorACloseMenuScene]


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


class MotorACloseMenuScene(MenuScene):
    name = "Closing settings"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorACloseNowScene,
            MotorACloseTimeScene,
            MotorACloseSpeedScene,
            MotorACloseDurationScene,
        ]


class MotorACloseNowScene(Scene):
    name = "Close now"


class MotorACloseTimeScene(MotorTimeScene):
    name = "Time"

    def _get_motor_data(self):
        return state.get("ac")


class MotorACloseSpeedScene(MotorPercentageScene):
    name = "Speed"

    def _get_motor_data(self):
        return state.get("ac")


class MotorACloseDurationScene(MotorDurationScene):
    name = "Duration"

    def _get_motor_data(self):
        return state.get("ac")


class MotorBOpenMenuScene(MenuScene):
    name = "Opening settings"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorBOpenNowScene,
            MotorBOpenTimeScene,
            MotorBOpenSpeedScene,
            MotorBOpenDurationScene,
        ]


class MotorBMenuScene(MenuScene):
    name = "Motor B"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorBOpenMenuScene, MotorBCloseMenuScene]


class MotorBOpenNowScene(Scene):
    name = "Open now"


class MotorBOpenTimeScene(MotorTimeScene):
    name = "Time"

    def _get_motor_data(self):
        return state.get("bo")


class MotorBOpenSpeedScene(MotorPercentageScene):
    name = "Speed"

    def _get_motor_data(self):
        return state.get("bo")


class MotorBOpenDurationScene(MotorDurationScene):
    name = "Duration"

    def _get_motor_data(self):
        return state.get("bo")


class MotorBCloseMenuScene(MenuScene):
    name = "Closing settings"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorBCloseNowScene,
            MotorBCloseTimeScene,
            MotorBCloseSpeedScene,
            MotorBCloseDurationScene,
        ]


class MotorBCloseNowScene(Scene):
    name = "Close now"


class MotorBCloseTimeScene(MotorTimeScene):
    name = "Time"

    def _get_motor_data(self):
        return state.get("bc")


class MotorBCloseSpeedScene(MotorPercentageScene):
    name = "Speed"

    def _get_motor_data(self):
        return state.get("bc")


class MotorBCloseDurationScene(MotorDurationScene):
    name = "Duration"

    def _get_motor_data(self):
        return state.get("bc")


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
