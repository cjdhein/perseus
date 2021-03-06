from types import *
import pdb
    
#represents a node in the tree - each node being a web page

class PageNode(object):

    __slots__ = ['nodeUrl','keywordFound','uid','parentNode','nodeList','urlList','nodeTitle','crawled','visited','level','error']
    
    def __init__(self, parent, uid, url, level):
        self.nodeUrl = url
        self.keywordFound = False
        self.uid = uid
        self.parentNode = parent
        
        # Constructed nodes that are children of this node
        self.nodeList = list()
        
        # Raw urls found from the crawler
        self.urlList = list() 

        self.nodeTitle = "No title for node"
        self.crawled = False
        self.visited = False

        # Holds the tree level for this node
        self.level = level
        
        # starts as none, if there is an error it will be the error reason
        #   This will be set by the web crawler
        self.error = None

    def __str__(self):
        if self.parentNode == None:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nkeyword:\t" + str(self.keywordFound) + "\nPARENT UID:\tROOT NODE"
        else:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nkeyword:\t" + str(self.keywordFound) +  "\nPARENT UID:\t" + str(self.parentNode.uid)
        return retString

    def getLevel(self):
        return self.level
    
    def getCrawledStatus(self):
        return self.crawled

    def setCrawledStatus(self, status):
        self.crawled = status

    def setTitle(self, title):
        titleString = ''
        titleString = str(title)
        self.nodeTitle = titleString

    def getTitle(self):
        return self.nodeTitle

    def setError(self,errText):
        self.error = errText

    def getError(self):
        return self.error

    def getUid(self):
        return self.uid

    def getParentUid(self):
        if self.parentNode is not None:
            return self.parentNode.uid
        else:
            return None

    def getUrl(self):
        return self.nodeUrl

    def printUrls(self):
        for elem in self.urlList:
            print(elem)

    def visitNode(self):
        self.visited = True


    # Returns the first unvisited child node
    # NOTE: Must follow a call to hasUnvisited() to ensure there are unvisited children
    def getUnvisited(self):
        if len(self.nodeList) >= 1:
            return self.nodeList.pop()
        else:
            return None


    # Returns boolean indicating if the node has unvisited children
    def hasUnvisited(self):
        vals = list(self.nodeDict.values())
        if vals.count(0) >= 1:
            return True
        else:
            return False

    def getKeywordStatus(self):
        return self.keywordFound

    
    def setKeywordStatus(self,status):
        self.keywordFound = status

    
