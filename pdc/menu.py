from keypad import Event, Keys

import asyncio

from pdc.hardware.display import Display, write

try:
    from typing import List, NoReturn, Type

    from pdc.hardware.display import WriteCommand
except ImportError:
    List = ...
    NoReturn = ...
    Type = ...
    WriteCommand = ...


class MenuManager:
    """
    This class is responsible for controlling the input and output
    (OLED display module and buttons).
    """

    def __init__(
        self, *, scenes: List[Type["Scene"]], display: Display, keys: Keys
    ) -> None:
        self.display = display
        self.keys = keys

        self.scenes = list(scenes)
        self.current_scene_id = None
        self.current_scene = None

        self.switch_to_scene(0)

    def switch_to_scene(self, scene_id: int) -> None:
        if self.current_scene:
            self.current_scene.on_exit()

        if scene_id == len(self.scenes):
            scene_id = 0

        self.current_scene_id = scene_id
        self.current_scene = self.scenes[self.current_scene_id](self)
        self.current_scene.on_enter()

    def switch_to_next_scene(self) -> None:
        self.switch_to_scene(self.current_scene_id + 1)

    async def task(self) -> NoReturn:
        while True:
            key_event = self.keys.events.get()
            if key_event and key_event.released:
                self.current_scene.on_press(key_event)

            await asyncio.sleep(0)


class Scene:
    def __init__(self, manager: MenuManager) -> None:
        self.manager = manager

    def on_enter(self) -> None:
        self.update_display()
        print(f"enter {self.__class__.__name__}")

    def on_press(self, event: Event) -> None:
        self.next_scene()

    def on_exit(self) -> None:
        print(f"leave {self.__class__.__name__}")

    def next_scene(self) -> None:
        self.manager.switch_to_next_scene()

    def update_display(self) -> None:
        self.manager.display.update(self.display_commands)

    @property
    def display_commands(self) -> List[WriteCommand]:
        return [write(0, 0, self.__class__.__name__)]
