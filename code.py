import asyncio

from pdc.hardware import display, i2c, keys


async def main():
    i2c.init_i2c()
    display.init_display()
    keys.init_keys()

    print("Done")

    while True:
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
