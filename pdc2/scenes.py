import asyncio

from pdc.hardware import display, keys

LINE_CURSOR = 1
LINE_COUNT = 5


class Scene:
    name = "Scene"

    def __init__(self, manager):
        self._manager = manager

    def handle_event(self, event):
        self.refresh_screen()

    def refresh_screen(self):
        display.update([display.write(0, 0, self.__class__.__name__)])


class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.entries = []
        self.cursor_position = 0

    def handle_event(self, event):
        if event.key_number == 1 and self.cursor_position > 0:
            self.cursor_position -= 1
        if event.key_number == 2 and self.cursor_position < len(self.entries) - 1:
            self.cursor_position += 1

        self.refresh_screen()

    def refresh_screen(self):
        data = [display.write(LINE_CURSOR, 0, "*")]

        for idx in range(LINE_COUNT):
            position = self.cursor_position - 1 + idx
            if 0 <= position < len(self.entries):
                data.append(display.write(idx, 1, self.entries[position].name))

        display.update(data)


class MainMenuScene(MenuScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.entries = [MockedScene1, MockedScene2, MockedScene3]


class MockedScene1(Scene):
    name = "Mocked Scene 1"


class MockedScene2(Scene):
    name = "Mocked Scene 2"


class MockedScene3(Scene):
    name = "Mocked Scene 3"


class SceneManager:
    def __init__(self):
        self._current_scene = None
        self.current_scene = MainMenuScene(self)

    @property
    def current_scene(self):
        return self._current_scene

    @current_scene.setter
    def current_scene(self, scene):
        self._current_scene = scene
        self._current_scene.refresh_screen()

    async def poll(self):
        keys_device = keys.device

        while True:
            key_event = keys_device.events.get()
            if key_event and key_event.released:
                self.current_scene.handle_event(key_event)

            await asyncio.sleep(0)
