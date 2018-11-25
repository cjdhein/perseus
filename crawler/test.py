from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import requests
import pdb
import sys
import asyncio
from pagenode import PageNode
from pagetree import PageTree
import time
url ="http://www.nytimes.com"
tree1 = PageTree('tree1.xml',url,1,2,None)
tree2 = PageTree('tree1.xml',url,1,2,None)

poolStart = time.time()
pdb.set_trace()
tree1.beginCrawl()
poolStop = time.time()

print("Async runtime = %s seconds" % (poolStop - poolStart))

singleStart = time.time()
#tree2.beginCrawl()
singleStop = time.time()


#print("Normal runtime = %s seconds" % (singleStop - singleStart))
