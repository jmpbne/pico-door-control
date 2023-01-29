import asyncio
import time

from pdc.hardware import display, eeprom, i2c, keys, rtc
from pdc2.scenes.base import SceneManager
from pdc2.scenes.impl import ScreenOffScene
from pdc2.scheduler import scheduler


async def main():
    # workaround for I2C issues and accessing the serial console
    time.sleep(5)

    i2c.init_i2c()
    eeprom.init_eeprom()
    rtc.init_rtc()
    display.init_display()
    keys.init_keys()

    sm = SceneManager(ScreenOffScene)

    await asyncio.gather(sm.poll(), scheduler())


if __name__ == "__main__":
    asyncio.run(main())
