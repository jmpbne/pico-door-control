from controller.menu import display, keys
from controller.service.control import ControlService
from controller.service.system import SystemOptionsService

BUTTON_LEFT = 0
BUTTON_DOWN = 1
BUTTON_UP = 2
BUTTON_RIGHT = 3
BUTTON_OK = 4


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
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 0
        self.current_value = None

    def decrease_value(self, step=1):
        if self.current_value is None:
            return

        self.current_value = max(self.current_value - step, self.min_value)

    def increase_value(self, step=1):
        if self.current_value is None:
            self.current_value = -step

        self.current_value = min(self.current_value + step, self.max_value)

    def get_current_value_string(self):
        if self.current_value is None:
            return "--"

        return str(self.current_value).replace("0", "O")

    def get_render_data(self):
        return (0, 0, "Podaj nowa wartosc:"), (0, 2, self.get_current_value_string())

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


# Scene implementations


class IdleScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(SystemOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(OpenOptionsScene)

    def get_render_data(self):
        if SystemOptionsService.get_hour() is None:
            return ((0, 0, "Nie ustawiono zegara"),)

        return ()


class ControlOptionsScene(OptionsScene):
    motor_id = None

    def get_render_data(self):
        return super().get_render_data() + (
            (1, 1, "Dlugosc"),
            (1, 2, "Predkosc"),
            (1, 3, "Godzina"),
            (1, 4, "Minuta"),
            (1, 5, "Ilosc powtorzen"),
            (1, 6, "Powtorz co"),
            (17, 1, f"{ControlService.get_duration(self.motor_id)}s"),
            (17, 2, f"{ControlService.get_speed(self.motor_id)}%"),
            (17, 3, f"{ControlService.get_hour(self.motor_id)}"),
            (17, 4, f"{ControlService.get_minute(self.motor_id)}"),
            (17, 5, f"{ControlService.get_count(self.motor_id)}"),
            (17, 6, f"{ControlService.get_rate(self.motor_id)}m"),
        )


class ControlDurationScene(EntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 1
        self.max_value = 120
        self.current_value = ControlService.get_duration(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            ControlService.set_duration(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlSpeedScene(EntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 20
        self.max_value = 100
        self.current_value = ControlService.get_speed(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            ControlService.set_speed(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlHourScene(EntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 23
        self.current_value = ControlService.get_hour(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            ControlService.set_hour(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlMinuteScene(EntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 59
        self.current_value = ControlService.get_minute(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            ControlService.set_minute(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlCountScene(EntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 20
        self.current_value = ControlService.get_count(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            ControlService.set_count(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class ControlRateScene(EntryScene):
    motor_id = None

    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 2
        self.max_value = 120
        self.current_value = ControlService.get_rate(self.motor_id)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            ControlService.set_rate(self.motor_id, self.current_value)
            self.manager.switch_to_parent_scene()


class OpenMotorMixin:
    motor_id = "o"


class OpenOptionsScene(OpenMotorMixin, ControlOptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (
            DummyScene,
            OpenDurationScene,
            OpenSpeedScene,
            OpenHourScene,
            OpenMinuteScene,
            OpenCountScene,
            OpenRateScene,
        )

    def get_render_data(self):
        return super().get_render_data() + ((1, 0, "Otworz teraz"),)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(IdleScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(CloseOptionsScene)


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
    motor_id = "c"


class CloseOptionsScene(CloseMotorMixin, ControlOptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (
            DummyScene,
            CloseDurationScene,
            CloseSpeedScene,
            CloseHourScene,
            CloseMinuteScene,
            CloseCountScene,
            CloseRateScene,
        )

    def get_render_data(self):
        return super().get_render_data() + ((1, 0, "Zamknij teraz"),)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(OpenOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(SystemOptionsScene)


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
        return super().get_render_data() + (
            (1, 0, "Godzina systemu"),
            (1, 1, "Minuta systemu"),
            # (1, 2, "Wersja"),
            (17, 0, f"{SystemOptionsService.get_hour()}"),
            (17, 1, f"{SystemOptionsService.get_minute()}"),
        )

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(CloseOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(IdleScene)


class DummyScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_OK:
            self.manager.switch_to_parent_scene()

    def get_render_data(self):
        return ((0, 0, "DummyScene"),)


class SystemHourScene(EntryScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 23
        self.current_value = SystemOptionsService.get_hour()

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            SystemOptionsService.set_hour(self.current_value)
            self.manager.switch_to_parent_scene()


class SystemMinuteScene(EntryScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 59

        self.current_value = SystemOptionsService.get_minute()

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            SystemOptionsService.set_minute(self.current_value)
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

    def poll(self):
        event = keys.get_event()
        if event:
            self.current_scene.handle_event(event)
