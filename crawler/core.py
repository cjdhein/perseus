# Used to test class implementations

from pagetree import PageTree

# Set a starting URL
startUrl = "https://www.taylorstitch.com/"

# Number of links to follow
limit = 8
# Searchtype: 1 = DFS, 2 = BFS !!!! BFS NOT IMPLEMENTED !!!!
search = 1

# Keyword search not implemented into pagetree / pagenode yet
keyword = None

# Create new PageTree with above variables
testTree = PageTree(startUrl, limit, keyword, 1)

# Begin the crawl
testTree.beginCrawl()
