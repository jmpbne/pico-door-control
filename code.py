import asyncio

from controller.core import rtc, scheduler, state
from controller.menu import display, keys
from controller.menu.scenes import SceneManager


async def scheduler_main():
    await scheduler.run()


async def menu_main():
    display.init()
    keys.init()

    manager = SceneManager()
    await manager.poll()


async def main():
    rtc.init()
    state.init()

    await asyncio.gather(scheduler_main(), menu_main())


if __name__ == "__main__":
    asyncio.run(main())
