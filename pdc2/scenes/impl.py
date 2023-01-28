from adafruit_datetime import datetime

from pdc.hardware import rtc
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


class MotorAOpenNowScene(MotorNowScene):
    name = "Open now"
    motor_id = "ao"


class MotorAOpenTimeScene(MotorTimeScene):
    name = "Time"
    motor_id = "ao"


class MotorAOpenSpeedScene(MotorPercentageScene):
    name = "Speed"
    motor_id = "ao"


class MotorAOpenDurationScene(MotorDurationScene):
    name = "Duration"
    motor_id = "ao"


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


class MotorACloseNowScene(MotorNowScene):
    name = "Close now"
    motor_id = "ac"


class MotorACloseTimeScene(MotorTimeScene):
    name = "Time"
    motor_id = "ac"


class MotorACloseSpeedScene(MotorPercentageScene):
    name = "Speed"
    motor_id = "ac"


class MotorACloseDurationScene(MotorDurationScene):
    name = "Duration"
    motor_id = "ac"


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


class MotorBOpenNowScene(MotorNowScene):
    name = "Open now"
    motor_id = "bo"


class MotorBOpenTimeScene(MotorTimeScene):
    name = "Time"
    motor_id = "bo"


class MotorBOpenSpeedScene(MotorPercentageScene):
    name = "Speed"
    motor_id = "bo"


class MotorBOpenDurationScene(MotorDurationScene):
    name = "Duration"
    motor_id = "bo"


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


class MotorBCloseNowScene(MotorNowScene):
    name = "Close now"
    motor_id = "bc"


class MotorBCloseTimeScene(MotorTimeScene):
    name = "Time"
    motor_id = "bc"


class MotorBCloseSpeedScene(MotorPercentageScene):
    name = "Speed"
    motor_id = "bc"


class MotorBCloseDurationScene(MotorDurationScene):
    name = "Duration"
    motor_id = "bc"


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
