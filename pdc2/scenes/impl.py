from adafruit_datetime import datetime

from pdc.hardware import rtc
from pdc2.scenes.base import BUTTON_ESC, INVALID_OUTPUT, Scene


class ScreenOffScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_ESC:
            self.manager.switch_to_new_scene(MainMenuScene)

    @property
    def display_data(self):
        return []


class MainMenuScene(Scene.Menu):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAMenuScene, Scene, SystemTimeScene]


class MotorAMenuScene(Scene.Menu):
    name = "Motor A"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAOpenMenuScene, Scene]


class MotorAOpenMenuScene(Scene.Menu):
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


class MotorAOpenTimeScene(Scene.Time):
    name = "Time"


class MotorAOpenSpeedScene(Scene.Percentage):
    name = "Speed"


class MotorAOpenDurationScene(Scene.Duration):
    name = "Duration"


class SystemTimeScene(Scene.Time):
    name = "System time"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)

        if rtc.device.lost_power:
            self._set_input_value(None)
        else:
            self._set_input_value(datetime.now())

    def handle_save(self):
        value = super().handle_save()
        if value is INVALID_OUTPUT or None:
            return INVALID_OUTPUT

        dt = datetime(2000, 1, 1, value.hour, value.minute, 0)
        rtc.device.datetime = dt.timetuple()

        return value
