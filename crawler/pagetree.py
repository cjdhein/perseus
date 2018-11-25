from webcrawler import WebCrawler
import sys
from pagenode import PageNode
import random
import pdb
from collections import deque
from lxml import etree
import gc
# print debug text if true
DEBUG = False

# hold directory path for the log directory
#LOGDIRECTORY = "../server/public/log_files/"
LOGDIRECTORY = "./"
class PageTree:

    def __init__ (self,outfile, startUrl, limit, searchType, keyword):
        self.outfile = outfile
        self.startPage = startUrl
        self.limit = limit
        
        if keyword is None:
            self.keywordExists = False
        else:
            self.keywordExists = True
            self.keyword = keyword

        self.searchType = searchType
        self.currentLevel = 1
        self.webCrawler = WebCrawler(keyword)
        self.idCount = -1
        # 0 represents root level
        self.rootNode = PageNode(None,self.getUID(),startUrl,0) 
        self.activeNode = None
        self.rootError = None
        self.crawled = set()

        # seed the random integer generator for DFS method
        random.seed()

    # Called to start the process. Branches to DFS or BFS depending on the search type
    def beginCrawl(self):

        if self.searchType == 1:
            returnStatus = self.crawlDFS()
            # Error on root node. Write an error log file
            if returnStatus == 2:
                self.writeErrorLog()
            # At least one successfully read node, so write normal log file
            else:
                self.writeLogFile()            
        elif self.searchType == 2:
            returnStatus = self.asyncBFS()
            if returnStatus == 2:
                self.writeErrorLog()
            else:
                self.writeLogFile()

    # Performs a depth first search
    def crawlDFS(self):
        if DEBUG:
            print("Search DFS")

        wc = self.webCrawler
        self.activeNode = self.rootNode
        
        # Loop while we have not hit the limit and the keyword status is false
        while self.currentLevel <= self.limit+1:
            aNode = self.activeNode
            
            # if the active node has not been crawled
            if aNode.nodeUrl not in self.crawled:

                # trigger the crawl and store return status in retStat. 0 for full crawl.
                if self.currentLevel <= self.limit:
                    retStat = wc.crawl(aNode, 0)
                else:
                    retStat = wc.crawl(aNode, 1)

                # Add the URL to the crawled dictionary
                self.crawled.add(aNode.nodeUrl)
                
                # Return codes:
                #   0: good return
                #   1: found keyword
                #   2: Error opening URL
                if retStat == 1:
                    # Set keyword status to true and continue to next loop interation to break out
                    aNode.setKeywordStatus(True)
                    return 1

                # Error occurred
                elif retStat == 2:
                    # if this is the root node, we return the error code and exit
                    if self.activeNode == self.rootNode:
                        return 2                    
                    # If not, we back set the active node to the parent node
                    else:
                        aNode.parentNode.nodeList.remove(aNode)
                        self.activeNode = aNode.parentNode 
                    continue                    

            if aNode.getLevel() == self.limit:
                self.currentLevel += 1
                continue
             
            # Execution here means the node has been crawled
            # get length of urlList
            listLen = len(aNode.urlList)

            # If this page has URLs available
            if listLen >= 1:
                # Get random url from the set
                newUrl = random.choice(aNode.urlList)
                aNode.urlList.remove(newUrl)

                # get newId and construct the new node
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl, self.currentLevel)

                # Add new node to current node's connections, setting it to 0 to indicate it hasn't been visited
                aNode.nodeList.append(newNode)

                # Set a new active node, and go down a level
                self.currentLevel += 1
                self.activeNode = newNode

            # No URLs available
            else:
                # Set aNode to the parent node in order to grab a new URL from there
                if aNode.parentNode is None:
                    break
                else:
                    self.activeNode = aNode.parentNode 

    # Performs a breadth first search asynchronously
    def asyncBFS(self):
        if DEBUG:
            print("Search BFS - Pooled")
        wc = self.webCrawler
        thisCrawl = list()
        thisCrawl.append(self.rootNode)
        
        nextCrawl = list()

        while self.currentLevel <= self.limit:
            # crawlTypes:
            #   0: full crawl (urls, title, keyword)
            #   1: fast crawl (title, keyword)
            ret = wc.crawlPool(thisCrawl,0)

            # If this is the root node and it errored, return 2 (fatal error on crawl)
            if thisCrawl[0] == self.rootNode and self.rootNode.getError() is not None:
                return 2
            
            
            while len(thisCrawl) > 0:
                node = thisCrawl.pop()
                self.crawled.add(node.nodeUrl)
                self.buildNodes(node,nextCrawl)
                node.urlList = None

            self.currentLevel += 1

            # ensure thisCrawl is clear
            # point thisCrawl at nextCrawl
            # make nextCrawl a new list
            thisCrawl.clear()
            thisCrawl = nextCrawl
            nextCrawl = list()
            if ret == 2:
                return 0
        # crawl for titles on last layer
        wc.crawlPool(thisCrawl, 1)
        return 0

    # Builds a node for each URL in the parent node's urlList
    # and adds them to nextCrawl
    def buildNodes(self,parentNode,nextCrawl):
        urls = parentNode.urlList

        for url in urls:
            newNode = PageNode(parentNode,self.getUID(),url,self.currentLevel)
            parentNode.nodeList.append(newNode)
            
            if self.currentLevel-1 < self.limit:
                if newNode.nodeUrl not in self.crawled:
                    nextCrawl.append(newNode)

    # Returns a new UID       
    def getUID(self):
        self.idCount += 1
        return self.idCount

    # Writes a log file by traversing the generated tree
    def writeLogFile(self):
        xmlRoot = etree.Element("crawler_log")
        xmlDoc = etree.ElementTree(xmlRoot)
        
        self.activeNode = self.rootNode
        q = deque()
        q.append(self.activeNode)
        
        while len(q) > 0:
            node = q.popleft()

            if not node.visited and node.getCrawledStatus():
                node.visitNode()

                page = etree.SubElement(xmlRoot,"page")

                uid = etree.SubElement(page,"id")
                uid.text = str(node.getUid())

                lvl = etree.SubElement(page,"level")
                lvl.text = str(node.getLevel())

                url = etree.SubElement(page,"url")
                url.text = node.getUrl()

                title = etree.SubElement(page,"title")
                title.text = str(node.getTitle())

                if node.getParentUid() is not None:
                    puid = etree.SubElement(page,"parent_id")
                    puid.text = str(node.getParentUid())

                if node.getKeywordStatus():
                    key = etree.SubElement(page,"keyword")
                    key.text = str(True)

                if DEBUG:
                    print(etree.tostring(page,pretty_print=True))
            
            child = node.getUnvisited()

            while child is not None:
                q.append(child)
                child = node.getUnvisited()
                
        xmlOut = open(LOGDIRECTORY + self.outfile,"wb")
        xmlDoc.write(xmlOut,pretty_print=True)
        xmlOut.close()

    # Writes the error log
    def writeErrorLog(self):
        xmlRoot = etree.Element("crawler_log")
        xmlDoc = etree.ElementTree(xmlRoot)

        errorNode = etree.SubElement(xmlRoot,"error")
        errorCode = etree.SubElement(errorNode,"code")
        errorCode.text = str(1)
        errorText = etree.SubElement(errorNode,"text")
        errorText.text = self.rootNode.getError()

        xmlOut = open(LOGDIRECTORY + self.outfile,"wb")
        xmlDoc.write(xmlOut,pretty_print=True)
        xmlOut.close()            
