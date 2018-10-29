from webcrawler import WebCrawler
from pagenode import PageNode
import random

class PageTree:

    def __init__ (self, startUrl, limit, keyword, searchType):
        self.startPage = startUrl
        self.limit = limit
        
        if keyword is None:
            self.keywordExists = False
        else:
            self.keywordExists = True
            self.keyword = keyword
        self.searchType = searchType
        self.curLevel = 0
        self.webCrawler = WebCrawler(keyword)
        self.idCount = -1
        self.rootNode = PageNode(None,self.getUID(),startUrl) 
        self.activeNode = None

        random.seed()
    def beginCrawl(self):
        wc = self.webCrawler
        
        if self.searchType == 1: #DFS
            self.activeNode = self.rootNode
            
            while self.curLevel <= self.limit:
                aNode = self.activeNode
                wc.crawl(aNode)
                print aNode                
                print ""
                
                i = random.randrange(len(aNode.urlList))
                aNode.urlList[i], aNode.urlList[-1] = aNode.urlList[-1], aNode.urlList[i]
                newUrl = aNode.urlList.pop()
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl)
                aNode.nodeList.append(newNode)
                self.curLevel += 1
                self.activeNode = newNode
                
    def getUID(self):
        self.idCount += 1
        return self.idCount
