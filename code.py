import asyncio

from pdc.hardware import display, i2c, keys
from pdc2.scenes import SceneManager


async def main():
    i2c.init_i2c()
    display.init_display()
    keys.init_keys()

    sm = SceneManager()

    await sm.poll()


if __name__ == "__main__":
    asyncio.run(main())
