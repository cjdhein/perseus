import asyncio
from requests_html import HTMLSession
import aiohttp

async def getAll(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.ensure_future(fetchURL(url,session))
            tasks.append(task)
            _ = await asyncio.gather(*tasks)
            return _

async def fetchURL(url,session):
    resp = await session.get(url)
    async with resp:
        return resp.status

urls = ['http://python.org','http://google.com']
loop = asyncio.get_event_loop()
fut = asyncio.ensure_future(getAll(urls))
res = loop.run_until_complete(fut)

for re in res:
    print(re)

