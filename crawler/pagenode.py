import unicodedata
from types import *
import pdb

class PageNode:

    #represents a node in the tree - each node being a web page

    def __init__(self, parent, uid, url):
        self.nodeUrl = url
        self.keywordFound = False
        self.uid = uid
        self.parentNode = parent
        self.nodeDict = dict() #constructed nodes that are children of this node
        self.urlList = [] #raw urls found from the crawler - NOT visited
        self.nodeTitle = "No title for node"
        self.crawled = False
        self.visited = False
    def __str__(self):
        if self.parentNode == None:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nkeyword:\t" + str(self.keywordFound) + "\nPARENT UID:\tROOT NODE"
        else:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nkeyword:\t" + str(self.keywordFound) +  "\nPARENT UID:\t" + str(self.parentNode.uid)
        return retString

    def getCrawledStatus(self):
        return self.crawled

    def setCrawledStatus(self, status):
        self.crawled = status

    def setTitle(self, title):
        # if the title is in unicode, we have to scrub it and convert to ascii
        titleString = ''
        title = unicode(title)
        scrubbed = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
        titleString = scrubbed
        self.nodeTitle = titleString

    def getTitle(self):
        return self.nodeTitle

    def getUid(self):
        return self.uid

    def getParentUid(self):
        if self.parentNode is not None:
            return self.parentNode.uid
        else:
            return "root"

    def getUrl(self):
        return self.nodeUrl

    def printUrls(self):
        for elem in self.urlList.items():
            print elem

    def visitNode(self):
        self.visited = True


    # Returns the first unvisited child node
    # NOTE: Must follow a call to hasUnvisited() to ensure there are unvisited children
    def getUnvisited(self):
        vals = self.nodeDict.values()
        keys = self.nodeDict.keys()
        index =  -1
        
        key = None

        index = vals.index(0) # get index of first unvisited 
        key = keys[index]
        self.nodeDict[key] = 1 #Set to 1 to mark as visited

        return key # return the first unvisited node

    # Returns boolean indicating if the node has unvisited children
    def hasUnvisited(self):
        vals = self.nodeDict.values()
        if vals.count(0) >= 1:
            return True
        else:
            return False

    def getKeywordStatus(self):
        return self.keywordFound

    
    def setKeywordStatus(self,status):
        self.keywordFound = status