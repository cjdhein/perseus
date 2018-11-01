# Used to test class implementations

from pagetree import PageTree
from pagenode import PageNode
import pdb


# Set a starting URL
startUrl = "http://www.nytimes.com"

# Number of links to follow
limit = 3
# Searchtype: 1 = DFS, 2 = BFS 
search = 1

# Keyword search not implemented into pagetree / pagenode yet
keyword = "Texas"

# Create new PageTree with above variables
testTree = PageTree(startUrl, limit, keyword, search)

# Begin the crawl
testTree.beginCrawl()
testTree.printTree()
