from webcrawler import WebCrawler
from pagenode import PageNode
import random
import pdb
from collections import deque
from lxml import etree

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
        self.crawled = dict()

        random.seed()

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
            returnStatus = self.crawlBFS()
            # Error on root node. Write an error log file
            #if returnStatus == 2:
                #self.writeErrorLog()
            # At least one successfully read node, so write normal log file
            #else:
                #self.writeLogFile()
        else:
            returnStatus = self.poolBFS()
            #if returnStatus == 0:
                #self.writeLogFile()

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
                self.crawled[aNode.nodeUrl] = aNode.urlList

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
                        del aNode.parentNode.nodeDict[aNode]
                        aNode.parentNode.nodeDict
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
                # Get random index
                i = random.randrange(len(aNode.urlList))

                # Swap URL at chosen index with the end to speed up the procedure
                aNode.urlList[i], aNode.urlList[-1] = aNode.urlList[-1], aNode.urlList[i]

                # set newUrl, newId and construct the new node
                newUrl = aNode.urlList.pop()
                newId = self.getUID()
                newNode = PageNode(aNode, newId, newUrl, self.currentLevel)

                # Add new node to current node's connections, setting it to 0 to indicate it hasn't been visited
                aNode.nodeDict[newNode] = 0

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

    def buildNodes(self,parentNode,nextCrawl):
        urls = parentNode.urlList

        for url in urls:
            newNode = PageNode(parentNode,self.getUID(),url,self.currentLevel)
            parentNode.nodeDict[newNode] = 0
            if self.currentLevel-1 < self.limit:
                if newNode.nodeUrl not in self.crawled.keys():
                    nextCrawl.append(newNode)

    def poolBFS(self):
        wc = self.webCrawler
        thisCrawl = list()
        thisCrawl.append(self.rootNode)
        
        nextCrawl = list()

        while self.currentLevel <= self.limit:

            # crawlType:    0 = urls, keyword, title
            #               1 = urls, title
            #               2 = title            
            if self.keywordExists:
                wc.crawlPool(thisCrawl,0)
            else:
                wc.crawlPool(thisCrawl,1)
            
            

            while len(thisCrawl) > 0:
                node = thisCrawl.pop()
                self.crawled[node.nodeUrl] = node
                self.buildNodes(node,nextCrawl)


            self.currentLevel += 1

            # ensure thisCrawl is clear
            # point thisCrawl at nextCrawl
            # make nextCrawl a new list
            thisCrawl.clear()
            thisCrawl = nextCrawl
            nextCrawl = list()
        
        # crawl for titles on last layer
        wc.crawlPool(thisCrawl, 2)
        return 0

        

        

    def crawlBFS(self):
        if DEBUG:
            print("Search BFS")

        wc = self.webCrawler
        
        # Used to efficiently implement BFS method
        # currentQ is the queue currently being processed
        # nextQ is the queue of nodes to be processed after the current nodes are done. 
        #   currentQ will hold all nodes left to process on the current level
        #   nextQ holds all nodes to be processed on the next level deeper
        currentQ = deque()
        nextQ = deque()

        # Start by adding the root node to the queue
        currentQ.append(self.rootNode)

        # Set as activeNode to ensure first loop runs
        self.activeNode = self.rootNode
        
        # Loop while the limit has not been hit, the queue is not empty, and we have not hit the keyword
        while len(currentQ) >= 1 and not self.activeNode.getKeywordStatus():
            
            # Take node from the front of the queue and make it the active node
            self.activeNode = currentQ.popleft()
            aNode = self.activeNode
            tmpList = aNode.urlList
            aNode.urlList = [url for url in tmpList if url not in self.crawled.keys()]

            # If the node was not crawled, crawl it
            if aNode.nodeUrl not in self.crawled:
                
                # Branch depending on whether the current level is the limit. If it is not the limit, we proceed with a full crawl, gather all URLs from the node.
                # If the limit has been reached, we can do a fast crawl to just get the title and check for the keyword.
                # Trigger the crawl with appropriate crawlType and store return status in retStat.
                # 0 = Full, 1= Fast 
                if aNode.level < self.limit:    
                    retStat = wc.crawl(aNode, 0)
                else:
                    retStat = wc.crawl(aNode, 1)
                
                # Add the URL to the crawled dictionary
                self.crawled[aNode.nodeUrl] = aNode

                # Return codes:
                #   0: good return
                #   1: found keyword
                #   2: Error opening URL
                if retStat == 1:
                    # Set keyword status to true and continue to next loop interation to break out
                    aNode.setKeywordStatus(True)
                    continue
                # Error occured, 
                elif retStat == 2:
                    # if this is the root node, we return the error code and exit
                    if self.activeNode == self.rootNode:
                        return 2                    
                    # Otherwise - go back to parent Node for next node 
                    else:
                        self.activeNode = aNode.parentNode 
                    continue
                # else:
                #     if DEBUG:
                #         print "Was: " + str(len(aNode.urlList))
                #     tmpList = aNode.urlList
                #     aNode.urlList = [url for url in tmpList if url not in self.crawled.keys()]
                #     if DEBUG:
                #         print "Is: " + str(len(aNode.urlList))
                #         print "" 
            else:
                continue
                #print "Here!!!"
                #aNode.setTitle(self.crawled[aNode.nodeUrl].getTitle())

            # Loop while there are still URLs to visit
            while (len(aNode.urlList)) >= 1 and self.currentLevel <= self.limit:

                # get new url
                newUrl = aNode.urlList.pop()
                
                if newUrl in self.crawled:
                    continue
                else:
                    # get next unique ID
                    newId = self.getUID()
                    
                    # create a new node
                    newNode = PageNode(aNode,newId,newUrl,self.currentLevel)
                    
                    # Add the new node to the current node's dict, with a 0 to indicate it has not been visited                    
                    aNode.nodeDict[newNode] = 0
                    nextQ.append(newNode)
                

            # Check if current queue is empty and we still have levels left
            if len(currentQ) <= 0 and self.currentLevel <= self.limit:

                # set to nextQ to start the next level
                currentQ = nextQ

                # reset the next queue
                nextQ = deque()
                
                self.currentLevel += 1

            self.crawled[aNode.nodeUrl] = aNode

                
    def getUID(self):
        self.idCount += 1
        return self.idCount

    def writeLogFile(self):
        xmlRoot = etree.Element("crawler_log")
        xmlDoc = etree.ElementTree(xmlRoot)
        
        self.activeNode = self.rootNode
        q = deque()
        q.append(self.activeNode)
        
        while len(q) > 0:
            node = q.popleft()

            if not node.visited:
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
            
            if node.hasUnvisited():
                # For each child in the nodeDict
                for child in node.nodeDict.keys():
                    if child.visited == False:
                        q.append(child)

        xmlOut = open(LOGDIRECTORY + self.outfile,"wb")
        xmlDoc.write(xmlOut,pretty_print=True)
        xmlOut.close()

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
