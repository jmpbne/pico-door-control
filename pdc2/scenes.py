import asyncio

from pdc.hardware import display, keys


class Scene:
    def __init__(self, manager):
        self._manager = manager

    def handle_event(self, event):
        pass

    def refresh_screen(self):
        pass


class MainScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.entries = [MockedScene1, MockedScene2, MockedScene3]

    def handle_event(self, event):
        self.refresh_screen()

    def refresh_screen(self):
        display.update([
            display.write(0, 0, str(self.entries[0])),
            display.write(1, 0, str(self.entries[1])),
            display.write(2, 0, str(self.entries[2])),
        ])


class MockedScene1(Scene):
    pass


class MockedScene2(Scene):
    pass


class MockedScene3(Scene):
    pass


class SceneManager:
    def __init__(self):
        self.current_scene = MainScene(self)

    async def poll(self):
        keys_device = keys.device

        while True:
            key_event = keys_device.events.get()
            if key_event and key_event.released:
                self.current_scene.handle_event(key_event)

            await asyncio.sleep(0)
