import asyncio

from pdc.hardware import display, i2c, keys, rtc
from pdc2.scenes.base import SceneManager
from pdc2.scenes.impl import ScreenOffScene


async def main():
    i2c.init_i2c()
    rtc.init_rtc()
    display.init_display()
    keys.init_keys()

    sm = SceneManager(ScreenOffScene)

    await sm.poll()


if __name__ == "__main__":
    asyncio.run(main())
