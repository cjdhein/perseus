
class PageNode:

    #represents a node in the tree - each node being a web page

    def __init__(self, parent, uid, url):
        self.nodeUrl = url
        self.keywordFound = False
        self.uid = uid
        self.parentNode = parent
        self.nodeList = []

    def __str__(self):
        if self.parentNode == None:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nPARENT UID:\tROOT NODE"
        else:
            retString = "UID:\t" + str(self.uid) + "\nURL:\t" + self.nodeUrl + "\nTITLE:\t" + self.nodeTitle + "\nPARENT UID:\t" + str(self.parentNode.uid)
        return retString


