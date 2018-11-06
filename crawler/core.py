# Used to test class implementations

from pagetree import PageTree
from pagenode import PageNode
import pdb
import sys

args = sys.argv



# Set a starting URL
startUrl = "http://www.nytimes.com"
startUrl = args[1]

# Number of links to follow
limit = 3
limit = int(args[2])

# Searchtype: 1 = DFS, 2 = BFS 
search = 1
search = int(args[3])

# Keyword search not implemented into pagetree / pagenode yet
keyword = None

if len(args) >= 5:
	keyword = args[4]
else:
	keyword = None


# Create new PageTree with above variables
testTree = PageTree(startUrl, limit, keyword, search)

# Begin the crawl
testTree.beginCrawl()
testTree.printTreeXML()

