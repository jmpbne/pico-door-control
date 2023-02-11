import asyncio


async def run():
    while True:
        print("ping")
        await asyncio.sleep(1.0)
