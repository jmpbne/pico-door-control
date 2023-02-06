from controller.core import rtc
from controller.menu import display, keys

BUTTON_LEFT = 0
BUTTON_UP = 1
BUTTON_DOWN = 2
BUTTON_RIGHT = 3
BUTTON_OK = 4


# Base scenes


class Scene:
    def __init__(self, manager, parent):
        self.manager = manager
        self.parent = parent

    def handle_event(self, event):
        pass

    @property
    def render_data(self):
        return ()


class OptionsScene(Scene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.position = 0
        self.children = []

    def move_cursor_up(self):
        if self.position == 0:
            self.position = len(self.children)

        self.position -= 1
        self.manager.render()

    def move_cursor_down(self):
        if self.position == len(self.children) - 1:
            self.position = -1

        self.position += 1
        self.manager.render()

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_UP:
            self.move_cursor_up()
        if event.key_number == BUTTON_DOWN:
            self.move_cursor_down()
        if event.key_number == BUTTON_OK:
            self.manager.switch_to_new_scene(self.children[self.position])


# Scene implementations


class IdleScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(SystemOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(OpenOptionsScene)

    @property
    def render_data(self):
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

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(IdleScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(SystemOptionsScene)

    @property
    def render_data(self):
        return (
            (0, self.position, "*"),
            (1, 0, "OTWORZ TERAZ"),
            (1, 1, "DLUGOSC"),
            (1, 2, "PREDKOSC"),
            (1, 3, "GODZINA"),
            (1, 4, "MINUTA"),
            (1, 5, "ILOSC POWTORZEN"),
            (1, 6, "POWTORZ CO"),
        )


class SystemOptionsScene(OptionsScene):
    def __init__(self, manager, parent):
        super().__init__(manager, parent)

        self.children = (DummyScene, DummyScene)

    def handle_event(self, event):
        super().handle_event(event)

        if event.key_number == BUTTON_LEFT:
            self.manager.switch_to_new_scene(OpenOptionsScene)
        if event.key_number == BUTTON_RIGHT:
            self.manager.switch_to_new_scene(IdleScene)

    @property
    def render_data(self):
        return (
            (0, self.position, "*"),
            (1, 0, "CZAS SYSTEMOWY"),
            (1, 1, "WERSJA"),
        )


class DummyScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_OK:
            self.manager.switch_to_parent_scene()

    @property
    def render_data(self):
        return ((0, 0, "DummyScene"),)


# Scene manager


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.switch_to_new_scene(IdleScene)

    def switch_to_parent_scene(self):
        if parent := self.current_scene.parent:
            self.current_scene = parent
            self.render()

    def switch_to_new_scene(self, scene_class):
        self.current_scene = scene_class(self, self.current_scene)
        self.render()

    def render(self):
        display.render(self.current_scene.render_data)

    def poll(self):
        event = keys.get_event()
        if event:
            self.current_scene.handle_event(event)
