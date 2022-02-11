

import aiohttp
import asyncio

async def main():

    async with aiohttp.ClientSession() as session:
        async with session.get('https://n01.radiojar.com/rrqf78p3bnzuv.mp3?rj-ttl=5&rj-tok=AAABfuJ2WWEAX08W4nZtedAAzA') as resp:
            print(await resp.content.read(10))

            # print("Status:", response.status)
            # print("Content-type:", response.headers['content-type'])

            # html = await response.text()
            # print("Body:", html[:15], "...")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
