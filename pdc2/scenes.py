import asyncio

from pdc.hardware import display, keys

DISPLAY_BUTTON_A_COL = 0
DISPLAY_BUTTON_B_COL = 5
DISPLAY_BUTTON_C_COL = 10
DISPLAY_BUTTON_D_COL = 15
DISPLAY_CURSOR_ROW = 1
DISPLAY_LAST_ROW = 4
DISPLAY_TOTAL_ROWS = 5

BUTTON_A = 0
BUTTON_B = 1
BUTTON_C = 2
BUTTON_D = 3
BUTTON_ESC = 4
BUTTON_OK = 5


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
        if event.key_number == BUTTON_B:
            if self.cursor_position > 0:
                self.cursor_position -= 1
                self.refresh_screen()
        if event.key_number == BUTTON_C:
            if self.cursor_position < len(self.entries) - 1:
                self.cursor_position += 1
                self.refresh_screen()
        if event.key_number == BUTTON_OK:
            scene = self.entries[self.cursor_position](self.manager, parent=self)
            self.manager.current_scene = scene

    def refresh_screen(self):
        data = [display.write(DISPLAY_CURSOR_ROW, 0, "*")]

        for idx in range(DISPLAY_TOTAL_ROWS):
            position = self.cursor_position - 1 + idx
            if 0 <= position < len(self.entries):
                screen_class = self.entries[position]
                try:
                    name = screen_class.name
                except AttributeError:
                    name = screen_class.__name__

                data.append(display.write(idx, 1, name))

        data.append(display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_A_COL, "      "))
        data.append(display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_B_COL, " Up   "))
        data.append(display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_C_COL, " Down "))
        data.append(display.write(DISPLAY_LAST_ROW, DISPLAY_BUTTON_D_COL, "      "))

        display.update(data)


class ScreenOffScene(Scene):
    def handle_event(self, event):
        if event.key_number == BUTTON_ESC:
            self.manager.current_scene = MainMenuScene(self.manager, parent=self)

    def refresh_screen(self):
        display.update([])


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
        self.current_scene = ScreenOffScene(self)

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