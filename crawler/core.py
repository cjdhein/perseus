# Used to test class implementations

from pagetree import PageTree

startUrl = "https://www.taylorstitch.com/"
limit = 8
search = 1
keyword = None
testTree = PageTree(startUrl, limit, keyword, 1)

testTree.beginCrawl()
