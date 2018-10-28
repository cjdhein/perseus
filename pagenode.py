import unicodedata

class PageNode:

    #represents a node in the tree - each node being a web page

    def __init__(self, parent, uid, url):
        self.nodeUrl = url
        self.keywordFound = False
        self.uid = uid
        self.parentNode = parent
        self.nodeList = [] #constructed nodes that are children of this node
        self.urlList = [] #raw urls found from the crawler - NOT visited
        self.nodeTitle = ""
    def __str__(self):
        if self.parentNode == None:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nPARENT UID:\tROOT NODE"
        else:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nPARENT UID:\t" + str(self.parentNode.uid)
        return retString

    def setTitle(self, title):
        scrubbed = unicodedata.normalize('NFKD', title).encode('ascii','ignore')
        self.nodeTitle = scrubbed

    def printUrls(self):
        for elem in self.urlList.items()    :
            print elem
