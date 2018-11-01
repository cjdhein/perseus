from webcrawler import WebCrawler
from pagenode import PageNode
import random
import pdb
from collections import deque

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
        print self.searchType
        if self.searchType == 1:
            self.crawlDFS()
        else:
            self.crawlBFS()

    def crawlDFS(self):
        wc = self.webCrawler
        keywordHit = False
        if self.searchType == 1: #DFS
            self.activeNode = self.rootNode
            
            while self.curLevel <= self.limit and not keywordHit:
                fo = open("log.txt","a")        
                aNode = self.activeNode
                print "Node: " + str(aNode.uid) + "\t Level: " + str(self.curLevel) + " URL: " + aNode.nodeUrl
                
                if aNode.getCrawledStatus() == False:
                    print "Node not crawled. Crawling"
                    retStat = wc.crawl(aNode)
                    # Return codes:
                    #   0: good return
                    #   1: found keyword
                    #   2: Error opening URL
                    if retStat == 1:
                        fo.write("Keyword found\n")
                        keywordHit = True
                        aNode.setKeywordStatus(True)
                        continue
                        

                    elif retStat == 2:
                        fo.write("Error in page\n")
                        print "Error found, setting activeNode to parent Node. Active: " + str(self.activeNode.uid) + " Parent: " + str(aNode.parentNode.uid)
                        self.activeNode = aNode.parentNode 
                        fo.close()
                        continue
                else:
                    print "Already crawled"
                   
                # get length of urlList
                listLen = len(aNode.urlList)

                # If this page has URLs available
                if listLen >= 1:
                    i = random.randrange(len(aNode.urlList))
                    aNode.urlList[i], aNode.urlList[-1] = aNode.urlList[-1], aNode.urlList[i]
                    newUrl = aNode.urlList.pop()
                    newId = self.getUID()
                    newNode = PageNode(aNode, newId, newUrl)
                    aNode.nodeDict[newNode] = 0
                    self.curLevel += 1
                    self.activeNode = newNode
                    fo.write(aNode.__str__())
                    fo.write("\n\n")

                # No URLs available
                else:
                    print "list length < 1"
                    # Set aNode to the parent node in order to grab a new URL from there
                    if aNode.parentNode is None:
                        self.currentLevel = self.limit + 1
                    self.activeNode = aNode.parentNode 

                fo.close()


    def crawlBFS(self):
        wc = self.webCrawler
        
        q = deque()
        q.append(self.rootNode)
        
        while self.curLevel <= self.limit or len(q) == 0:
            self.activeNode = q.popleft()
            fo = open("log.txt","a")
            aNode = self.activeNode
            print "Node: " + str(aNode.uid) + "\t Level: " + str(self.curLevel) + " URL: " + aNode.nodeUrl

            if aNode.getCrawledStatus() == False:
                print "Node not crawled. Crawling"
                retStat = wc.crawl(aNode)
                
                # Return codes:
                #   0: good return
                #   1: found keyword
                #   2: Error opening URL
                if retStat == 1:
                    fo.write("Keyword found\n")
                elif retStat == 2:
                    fo.write("Error in page\n")
                    print "Error found, setting activeNode to parent Node. Active: " + str(self.activeNode.uid) + " Parent: " + str(aNode.parentNode.uid)
                    self.activeNode = aNode.parentNode
                    fo.close()
                    continue
            else:
                print "Already crawled"
            
            while (len(aNode.urlList)) >= 1:
                newUrl = aNode.urlList.pop()
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl)
                aNode.nodeDict[newNode] = 0
                q.append(newNode)
                fo.write(newNode.__str__())
                fo.write("\n\n")
            
            self.curLevel += 1

            
            # get length of urlList
            listLen = len(aNode.urlList)

            # If this page has URLs available
            if listLen >= 1:
                i = random.randrange(len(aNode.urlList))
                aNode.urlList[i], aNode.urlList[-1] = aNode.urlList[-1], aNode.urlList[i]
                newUrl = aNode.urlList.pop()
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl)
                aNode.nodeDict[newNode] = 0
                self.curLevel += 1
                self.activeNode = newNode
                fo.write(aNode.__str__())
                fo.write("\n\n")

            # No URLs available
            else:
                print "list length < 1"
                # Set aNode to the parent node in order to grab a new URL from there
                if aNode.parentNode is None:
                    self.currentLevel = self.limit + 1
                self.activeNode = aNode.parentNode

            fo.close()

                
    def getUID(self):
        self.idCount += 1
        return self.idCount

    def printTree(self):

        self.activeNode = self.rootNode
        stack = []
        self.traverse(self.activeNode,stack)
        
    def traverse(self, node, stack):
        if node.hasUnvisited():
            stack.append(node)
            nextNode = node.getUnvisited()
            self.traverse(nextNode,stack)
            
            nextNode = stack.pop()
            self.traverse(nextNode,stack)
        else:
            print node
            print ""
            



