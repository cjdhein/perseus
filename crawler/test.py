from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import requests
import pdb
import sys
import asyncio


session = HTMLSession()


urls = ['http://www.google.com', 'www.python.org', 'www.wikipedia.org']

async def reqUrl(url):
    try:
        response = session.get(url)
        return response
    except requests.exceptions.MissingSchema:
        url = 'http://' + url
        return await reqUrl(url)
    except:
        e = sys.exc_info()
        return str(e[1])


pool = asyncio.gather(*[reqUrl(url) for url in urls])
loop = asyncio.get_event_loop()

results = loop.run_until_complete(pool)
pdb.set_trace()
loop.close()

print("done")
