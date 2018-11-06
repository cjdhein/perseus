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
        print "Search DFS"

        wc = self.webCrawler
        self.activeNode = self.rootNode
        
        # Loop while we have not hit the limit and the keyword status is false
        while self.curLevel <= self.limit and not self.activeNode.getKeywordStatus():
            fo = open("log.txt","a")        
            aNode = self.activeNode
            
            # if the active node has not been crawled
            if aNode.getCrawledStatus() == False:

                # trigger the crawl and store return status in retStat
                retStat = wc.crawl(aNode)

                # Return codes:
                #   0: good return
                #   1: found keyword
                #   2: Error opening URL
                if retStat == 1:
                    fo.write("Keyword found\n")
                    # Set keyword status to true and continue to next loop interation to break out
                    aNode.setKeywordStatus(True)
                    continue
                  

                # Error occurred, so we back-up to parent node
                elif retStat == 2:
                    fo.write("Error in page\n")
                    self.activeNode = aNode.parentNode 
                    fo.close()
                    continue
             
            # Execution here means the node has been crawled
            
            # get length of urlList
            listLen = len(aNode.urlList)

            # If this page has URLs available
            if listLen >= 1:
                # Get random index
                i = random.randrange(len(aNode.urlList))

                # Swap URL at chosen index with the end to speed up the procedure
                aNode.urlList[i], aNode.urlList[-1] = aNode.urlList[-1], aNode.urlList[i]

                # set newUrl, newId and construct the new node
                newUrl = aNode.urlList.pop()
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl)

                # Add new node to current node's connections, setting it to 0 to indicate it hasn't been visited
                aNode.nodeDict[newNode] = 0

                # Set a new active node, and go down a level
                self.curLevel += 1
                self.activeNode = newNode
                fo.write(aNode.__str__())
                fo.write("\n\n")

            # No URLs available
            else:
                # Set aNode to the parent node in order to grab a new URL from there
                if aNode.parentNode is None:
                    self.currentLevel = self.limit + 1
                self.activeNode = aNode.parentNode 

            fo.close()


    def crawlBFS(self):
        print "Search BFS"
        wc = self.webCrawler
        
        # Used to efficiently implement BFS method
        q = deque()

        # Start by adding the root node to the queue
        q.append(self.rootNode)

        # Set as activeNode to ensure first loop runs
        self.activeNode = self.rootNode
       
        # Loop while the limit has not been hit, the queue is not empty, and we have not hit the keyword
        while self.curLevel <= self.limit and len(q) >= 1 and not self.activeNode.getKeywordStatus():

            # Take node from the front of the queue and make it the active node
            self.activeNode = q.popleft()
            fo = open("log.txt","a")
            aNode = self.activeNode
            # If the node was not crawled, crawl it
            if aNode.getCrawledStatus() == False:
                retStat = wc.crawl(aNode)
                
                # Return codes:
                #   0: good return
                #   1: found keyword
                #   2: Error opening URL
                if retStat == 1:
                    fo.write("Keyword found\n")
                    # Set keyword status to true and continue to next loop interation to break out
                    aNode.setKeywordStatus(True)
                    continue
                # Error occured, go back to parent Node for next node 
                elif retStat == 2:
                    fo.write("Error in page\n")
                    print "Error found, setting activeNode to parent Node. Active: " + str(self.activeNode.uid) + " Parent: " + str(aNode.parentNode.uid)
                    self.activeNode = aNode.parentNode
                    fo.close()
                    continue
            
            # Loop while there are still URLs to visit
            while (len(aNode.urlList)) >= 1:
                newUrl = aNode.urlList.pop()
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl)
                aNode.nodeDict[newNode] = 0
                q.append(newNode)
                fo.write(newNode.__str__())
                fo.write("\n\n")
            
            self.curLevel += 1
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
            if node.visited == False:
                node.visitNode()
                print ""
                print node



