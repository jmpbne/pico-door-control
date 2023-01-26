import asyncio

from pdc.hardware import display, keys

LINE_CURSOR = 1
LINE_COUNT = 5

BUTTON_ESC = 0
BUTTON_UP = 1
BUTTON_DOWN = 2
BUTTON_OK = 3


class Scene:
    def __init__(self, manager, parent=None):
        self.manager = manager
        self.parent = parent

    def handle_event(self, event):
        self.refresh_screen()

    def refresh_screen(self):
        display.update([display.write(0, 0, self.__class__.__name__)])


class MenuScene(Scene):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)

        self.entries = []
        self.cursor_position = 0

    def handle_event(self, event):
        if event.key_number == BUTTON_ESC:
            if self.parent:
                self.manager.current_scene = self.parent
        if event.key_number == BUTTON_DOWN:
            if self.cursor_position > 0:
                self.cursor_position -= 1
                self.refresh_screen()
        if event.key_number == BUTTON_UP:
            if self.cursor_position < len(self.entries) - 1:
                self.cursor_position += 1
                self.refresh_screen()
        if event.key_number == BUTTON_OK:
            scene = self.entries[self.cursor_position](self.manager, parent=self)
            self.manager.current_scene = scene

    def refresh_screen(self):
        data = [display.write(LINE_CURSOR, 0, "*")]

        for idx in range(LINE_COUNT):
            position = self.cursor_position - 1 + idx
            if 0 <= position < len(self.entries):
                screen_class = self.entries[position]
                try:
                    name = screen_class.name
                except AttributeError:
                    name = screen_class.__name__

                data.append(display.write(idx, 1, name))

        display.update(data)


class MainMenuScene(MenuScene):
    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAMenuScene, Scene, Scene]


class MotorAMenuScene(MenuScene):
    name = "Motor A"

    def __init__(self, manager, parent=None):
        super().__init__(manager, parent)
        self.entries = [MotorAOpenMenuScene, Scene]


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


class MotorAOpenTimeScene(Scene):
    name = "Time"


class MotorAOpenSpeedScene(Scene):
    name = "Speed"


class MotorAOpenDurationScene(Scene):
    name = "Duration"


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
