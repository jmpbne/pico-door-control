from adafruit_datetime import datetime

from pdc.hardware import rtc
from pdc2 import state
from pdc2.scenes.base import (
    BUTTON_ESC,
    MenuScene,
    MotorDurationScene,
    MotorNowScene,
    MotorPercentageScene,
    MotorTimeScene,
    Scene,
    TimeScene,
)
from pdc2.scenes.exceptions import SceneValueError
from pdc2.strings import _


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
    name = _("Motor A")

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAOpenMenuScene, MotorACloseMenuScene]


class MotorAOpenMenuScene(MenuScene):
    name = _("Opening settings")

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorAOpenNowScene,
            MotorAOpenTimeScene,
            MotorAOpenSpeedScene,
            MotorAOpenDurationScene,
        ]


class MotorAOpenNowScene(MotorNowScene):
    motor_id = "ao"


class MotorAOpenTimeScene(MotorTimeScene):
    motor_id = "ao"


class MotorAOpenSpeedScene(MotorPercentageScene):
    motor_id = "ao"


class MotorAOpenDurationScene(MotorDurationScene):
    motor_id = "ao"


class MotorACloseMenuScene(MenuScene):
    name = _("Closing settings")

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorACloseNowScene,
            MotorACloseTimeScene,
            MotorACloseSpeedScene,
            MotorACloseDurationScene,
        ]


class MotorACloseNowScene(MotorNowScene):
    motor_id = "ac"


class MotorACloseTimeScene(MotorTimeScene):
    motor_id = "ac"


class MotorACloseSpeedScene(MotorPercentageScene):
    motor_id = "ac"


class MotorACloseDurationScene(MotorDurationScene):
    motor_id = "ac"


class MotorBMenuScene(MenuScene):
    name = _("Motor B")

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorBOpenMenuScene, MotorBCloseMenuScene]


class MotorBOpenMenuScene(MenuScene):
    name = _("Opening settings")

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorBOpenNowScene,
            MotorBOpenTimeScene,
            MotorBOpenSpeedScene,
            MotorBOpenDurationScene,
        ]


class MotorBOpenNowScene(MotorNowScene):
    motor_id = "bo"


class MotorBOpenTimeScene(MotorTimeScene):
    motor_id = "bo"


class MotorBOpenSpeedScene(MotorPercentageScene):
    motor_id = "bo"


class MotorBOpenDurationScene(MotorDurationScene):
    motor_id = "bo"


class MotorBCloseMenuScene(MenuScene):
    name = _("Closing settings")

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [
            MotorBCloseNowScene,
            MotorBCloseTimeScene,
            MotorBCloseSpeedScene,
            MotorBCloseDurationScene,
        ]


class MotorBCloseNowScene(MotorNowScene):
    motor_id = "bc"


class MotorBCloseTimeScene(MotorTimeScene):
    motor_id = "bc"


class MotorBCloseSpeedScene(MotorPercentageScene):
    motor_id = "bc"


class MotorBCloseDurationScene(MotorDurationScene):
    motor_id = "bc"


class SystemTimeScene(TimeScene):
    name = _("System time")

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
        state.reset_motors_timestamp()

        return value
