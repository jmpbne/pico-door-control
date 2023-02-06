from controller.core import rtc
from controller.menu import display, keys

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
        return (0, 0, "PODAJ NOWA WARTOSC:"), (0, 2, self.get_current_value_string())

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
        if rtc.get_datetime() is None:
            return ((0, 0, "NIE USTAWIONO ZEGARA"),)

        return ()


class OpenOptionsScene(OptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (
            DummyScene,
            DummyScene,
            DummyScene,
            DummyScene,
            DummyScene,
            DummyScene,
            DummyScene,
        )

    def get_render_data(self):
        return super().get_render_data() + (
            (1, 0, "OTWORZ TERAZ"),
            (1, 1, "DLUGOSC"),
            (1, 2, "PREDKOSC"),
            (1, 3, "GODZINA"),
            (1, 4, "MINUTA"),
            (1, 5, "ILOSC POWTORZEN"),
            (1, 6, "POWTORZ CO"),
        )

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(IdleScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(SystemOptionsScene)


class SystemOptionsScene(OptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (SystemHourScene, SystemMinuteScene, DummyScene)

    def get_render_data(self):
        return super().get_render_data() + (
            (1, 0, "GODZINA SYSTEMU"),
            (1, 1, "MINUTA SYSTEMU"),
            (1, 2, "WERSJA"),
        )

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(OpenOptionsScene)
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

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            self.manager.switch_to_parent_scene()


class SystemMinuteScene(EntryScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.min_value = 0
        self.max_value = 59

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_OK:
            self.manager.switch_to_parent_scene()


# Scene manager


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.switch_to_new_scene(IdleScene)

    def switch_to_parent_scene(self):
        if parent := self.current_scene.parent:
            self.current_scene = parent
            self.render()

    def switch_to_new_scene(self, scene_class, store_parent=False):
        parent = self.current_scene if store_parent else None

        self.current_scene = scene_class(self, parent)
        self.render()

    def render(self):
        display.render(self.current_scene.get_render_data())

    def poll(self):
        event = keys.get_event()
        if event:
            self.current_scene.handle_event(event)
