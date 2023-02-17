import asyncio

from controller import constants
from controller.core import rtc
from controller.menu import display, keys
from controller.menu.locale import gettext as _
from controller.service import control, system

BUTTON_LEFT = 0
BUTTON_DOWN = 1
BUTTON_UP = 2
BUTTON_RIGHT = 3
BUTTON_OK = 4


def format_number(number, digits=0):
    if number is None:
        return "-" * digits

    return f"{number:0{digits}d}".replace("0", "O")


# Base scenes


class Scene:
    def __init__(self, manager, parent):
        self.manager = manager
        self.parent = parent

    def get_render_data(self):
        return ()

    def handle_event(self, event):
        pass


class OptionsScene(Scene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.position = 0
        self.children = []

    def move_cursor_up(self):
        self.position = max(self.position - 1, 0)

    def move_cursor_down(self):
        self.position = min(self.position + 1, len(self.children) - 1)

    def get_render_data(self):
        return ((0, self.position, "*"),)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_DOWN:
            self.move_cursor_down()
            self.manager.render()
        if event.key_number == BUTTON_UP:
            self.move_cursor_up()
            self.manager.render()
        if event.key_number == BUTTON_OK:
            scene_class = self.children[self.position]
            self.manager.switch_to_new_scene(scene_class, store_parent=True)


class EntryScene(Scene):
    digits = 0
    min_value = 0
    max_value = 0

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = None

    def decrease_value(self, step=1):
        if self.current_value is None:
            return

        self.current_value = max(self.current_value - step, self.min_value)

    def increase_value(self, step=1):
        if self.current_value is None:
            self.current_value = -step

        self.current_value = min(self.current_value + step, self.max_value)

    def get_render_data(self):
        value = self.current_value

        return (
            (0, 0, _("Enter new value:")),
            (0, 2, format_number(value, digits=self.digits)),
        )

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.decrease_value(10)
            self.manager.render()
        if event.key_number == BUTTON_DOWN:
            self.decrease_value()
            self.manager.render()
        if event.key_number == BUTTON_UP:
            self.increase_value()
            self.manager.render()
        if event.key_number == BUTTON_RIGHT:
            self.increase_value(10)
            self.manager.render()


class HourEntryScene(EntryScene):
    digits = 2
    min_value = constants.HOUR_MIN
    max_value = constants.HOUR_MAX


class MinuteEntryScene(EntryScene):
    digits = 2
    min_value = constants.MINUTE_MIN
    max_value = constants.MINUTE_MAX


# Scene implementations


class IdleScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(SystemOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(OpenOptionsScene)

    def get_render_data(self):
        if rtc.get_datetime() is None:
            return ((0, 0, _("System clock not set")),)

        return ()


class ControlOptionsScene(OptionsScene):
    motor_id = None

    def get_render_data(self):
        duration = control.get_duration(self.motor_id)
        speed = control.get_speed(self.motor_id)
        hour = control.get_hour(self.motor_id)
        minute = control.get_minute(self.motor_id)
        count = control.get_count(self.motor_id)
        rate = control.get_rate(self.motor_id)

        return super().get_render_data() + (
            (1, 1, _("Duration")),
            (1, 2, _("Speed")),
            (1, 3, _("Hour")),
            (1, 4, _("Minute")),
            (1, 5, _("Repeat count")),
            (1, 6, _("Repeat every")),
            (16, 1, format_number(duration)),
            (16, 2, format_number(speed)),
            (16, 3, format_number(hour, digits=2)),
            (16, 4, format_number(minute, digits=2)),
            (16, 5, format_number(count)),
            (16, 6, format_number(rate)),
            (20, 1, "s"),
            (20, 2, "%"),
            (20, 6, "m"),
        )


class ControlNowScene(Scene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.success = bool(rtc.get_datetime())

        if self.success:
            control.run_oneshot(self.motor_id)

    def get_render_data(self):
        return (
            (0, 0, _("Done") if self.success else _("Set system time first")),
            (19, 6, _("OK")),
        )

    def handle_event(self, event):
        self.manager.switch_to_parent_scene()


class ControlDurationScene(EntryScene):
    motor_id = None

    min_value = constants.DURATION_MIN
    max_value = constants.DURATION_MAX

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = control.get_duration(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            control.set_duration(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlSpeedScene(EntryScene):
    motor_id = None

    min_value = constants.SPEED_MIN
    max_value = constants.SPEED_MAX

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = control.get_speed(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            control.set_speed(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlHourScene(HourEntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = control.get_hour(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            control.set_hour(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlMinuteScene(MinuteEntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = control.get_minute(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            control.set_minute(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlCountScene(EntryScene):
    motor_id = None

    min_value = constants.COUNT_MIN
    max_value = constants.COUNT_MAX

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = control.get_count(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            control.set_count(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlRateScene(EntryScene):
    motor_id = None

    min_value = constants.RATE_MIN
    max_value = constants.RATE_MAX

    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = control.get_rate(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            control.set_rate(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class OpenMotorMixin:
    motor_id = constants.MOTOR_OPEN_ID


class OpenOptionsScene(OpenMotorMixin, ControlOptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (
            OpenNowScene,
            OpenDurationScene,
            OpenSpeedScene,
            OpenHourScene,
            OpenMinuteScene,
            OpenCountScene,
            OpenRateScene,
        )

    def get_render_data(self):
        return super().get_render_data() + ((1, 0, _("Open now")),)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(IdleScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(CloseOptionsScene)


class OpenNowScene(OpenMotorMixin, ControlNowScene):
    pass


class OpenDurationScene(OpenMotorMixin, ControlDurationScene):
    pass


class OpenSpeedScene(OpenMotorMixin, ControlSpeedScene):
    pass


class OpenHourScene(OpenMotorMixin, ControlHourScene):
    pass


class OpenMinuteScene(OpenMotorMixin, ControlMinuteScene):
    pass


class OpenCountScene(OpenMotorMixin, ControlCountScene):
    pass


class OpenRateScene(OpenMotorMixin, ControlRateScene):
    pass


class CloseMotorMixin:
    motor_id = constants.MOTOR_CLOSE_ID


class CloseOptionsScene(CloseMotorMixin, ControlOptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (
            CloseNowScene,
            CloseDurationScene,
            CloseSpeedScene,
            CloseHourScene,
            CloseMinuteScene,
            CloseCountScene,
            CloseRateScene,
        )

    def get_render_data(self):
        return super().get_render_data() + ((1, 0, _("Close now")),)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(OpenOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(SystemOptionsScene)


class CloseNowScene(CloseMotorMixin, ControlNowScene):
    pass


class CloseDurationScene(CloseMotorMixin, ControlDurationScene):
    pass


class CloseSpeedScene(CloseMotorMixin, ControlSpeedScene):
    pass


class CloseHourScene(CloseMotorMixin, ControlHourScene):
    pass


class CloseMinuteScene(CloseMotorMixin, ControlMinuteScene):
    pass


class CloseCountScene(CloseMotorMixin, ControlCountScene):
    pass


class CloseRateScene(CloseMotorMixin, ControlRateScene):
    pass


class SystemOptionsScene(OptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (SystemHourScene, SystemMinuteScene)

    def get_render_data(self):
        hour = system.get_hour()
        minute = system.get_minute()

        return super().get_render_data() + (
            (1, 0, _("System hour")),
            (1, 1, _("System minute")),
            (16, 0, format_number(hour, digits=2)),
            (16, 1, format_number(minute, digits=2)),
            (0, 6, system.get_system_info()),
        )

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(CloseOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(IdleScene)


class SystemHourScene(HourEntryScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = system.get_hour()

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            system.set_hour(self.current_value)
            self.manager.switch_to_parent_scene()


class SystemMinuteScene(MinuteEntryScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)
        self.current_value = system.get_minute()

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            system.set_minute(self.current_value)
            self.manager.switch_to_parent_scene()


# Scene manager


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.switch_to_new_scene(IdleScene)

    def switch_to_parent_scene(self):
        if parent := self.current_scene.parent:
            print(f"Returning to {parent.__class__.__name__}")
            self.current_scene = parent
            self.render()

    def switch_to_new_scene(self, scene_class, store_parent=False):
        parent = self.current_scene if store_parent else None

        print(f"Switching to {scene_class.__name__}")
        self.current_scene = scene_class(self, parent)
        self.render()

    def render(self):
        display.render(self.current_scene.get_render_data())

    async def poll(self):
        while True:
            event = keys.get_event()
            if event:
                self.current_scene.handle_event(event)
            await asyncio.sleep(0)
