# Used to test class implementations

from pagetree import PageTree
from pagenode import PageNode
import pdb
import sys

# ARG Format
#   2: Start URL
#   3: Limit for BFS or DFS
#   4: Search Type (1 - DFS, 2 - BFS)
#   5: Keyword (optional)

args = sys.argv

# Get output file name
outfile = args[1]

# Set a starting URL
startUrl = args[2]

# Number of links to follow
limit = int(args[3])

# Searchtype: 1 = DFS, 2 = BFS 
search = int(args[4])

# Keyword search not implemented into pagetree / pagenode yet
keyword = None

if len(args) >= 6:
	keyword = args[5]
else:
	keyword = None


# Create new PageTree with above variables
testTree = PageTree(outfile, startUrl, limit, search, keyword)
# Begin the crawl
testTree.beginCrawl()
