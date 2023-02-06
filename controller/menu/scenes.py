from controller.core import rtc
from controller.menu import display, keys


# Base scenes


class Scene:
    def __init__(self, manager):
        self.manager = manager

    def handle_event(self, event):
        print(event)

    @property
    def render_data(self):
        return ()


class StaticScene(Scene):
    pass


class MenuScene(Scene):
    pass


class EditScene(Scene):
    pass


# Scene implementations


class IdleScene(StaticScene):
    @property
    def render_data(self):
        if rtc.get_datetime() is None:
            return ((0, 0, "NIE USTAWIONO ZEGARA"),)

        return ()


# Scene manager


class SceneManager:
    def __init__(self):
        self.current_scene = None
        self.switch_scene(IdleScene(self))

    def switch_scene(self, scene):
        self.current_scene = scene
        self.render()

    def render(self):
        display.render(self.current_scene.render_data)

    def poll(self):
        event = keys.get_event()
        if event:
            self.current_scene.handle_event(event)
