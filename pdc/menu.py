import asyncio


class MenuManager:
    """
    This class is responsible for controlling the input and output
    (OLED display module and buttons).
    """

    def __init__(self, *, scenes, display, keys):
        self.display = display
        self.keys = keys

        self.scenes = list(scenes)
        self.current_scene_id = None
        self.current_scene = None

        self.switch_to_scene(0)

    def switch_to_scene(self, scene_id):
        if self.current_scene:
            self.current_scene.on_exit()

        if scene_id == len(self.scenes):
            scene_id = 0

        self.current_scene_id = scene_id
        self.current_scene = self.scenes[self.current_scene_id](self)
        self.current_scene.on_enter()

    def switch_to_next_scene(self):
        self.switch_to_scene(self.current_scene_id + 1)

    async def task(self):
        while True:
            key_event = self.keys.events.get()
            if key_event and key_event.released:
                self.current_scene.on_press(key_event)

            await asyncio.sleep(0)


class Scene:
    def __init__(self, manager):
        self.manager = manager

    def on_enter(self):
        self.update_display()
        print(f"enter {self.__class__.__name__}")

    def on_press(self, event):
        self.manager.switch_to_next_scene()

    def on_exit(self):
        print(f"leave {self.__class__.__name__}")

    def update_display(self):
        self.manager.display.update(self.text_lines)

    @property
    def text_lines(self):
        return [self.__class__.__name__]
