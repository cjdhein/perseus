import sys
import asyncio
from bs4 import BeautifulSoup as bs
from requests_html import HTMLSession
import requests
from requests import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from webparser import WebParser
from pagenode import PageNode
import pdb

DEBUG = True

class WebCrawler:
    # Performs crawling of provided web address

    def __init__ (self,keyword=None):
        self.parser = WebParser()
        self.urls = set()

        if keyword is None:
            self.keywordExists = False
        else:
            self.keywordExists = True
            self.keyword = keyword

    def __str__(self):
        # return string representation of self

        returnString = ''

        if len(self.urlDict.items()) > 0:
            for el in self.urlDict.keys():
                returnString = str(el) + '\n' + returnString

            return returnString
        else:
            return "urlDict is empty"


    # crawlTypes:
    #   0: full crawl (urls, title, keyword)
    #   1: fast crawl (title, keyword)
    # Return codes:
    #   0: good return
    #   1: found keyword
    #   2: Error opening URL
    def crawl(self, page, crawlType):
        fetched = self._fetch(page.nodeUrl)
        loadedUrl = fetched[1]
        html = fetched[0]

        # if we got a string back, there was an error fetching
        # return code 2 (error)
        if type(html) == str:
            page.setTitle("Invalid, broken, or otherwise unreachable URL")
            page.setError(html)
            return 2
        
        # if DEBUG:
        #     print self.parser.getPageTitle(html)
        try:
            title = self.parser.getPageTitle(html)
            page.setTitle(title)
            page.setCrawledStatus(True)
        except AttributeError:
            e = sys.exc_info()
            page.setError("html is of type " + str(type(html)) + " but should be html object.")
            sys.stderr.write("\n*****\n" + str(e[0]) + " " + str(e[1]) + "\n")
            sys.stderr.write("URL: " + loadedUrl + "\n\t type: " + str(type(html)))
            return 2
        except:
            e = sys.exc_info()
            sys.stderr.write(str(e[0]) + " " + str(e[1]))
            page.setError("Something went wrong here...")
            sys.stderr.write("\nSomething went wrong here...\n")
            return 2
        
        # CrawlType of 0 means we are interested in the urls
        if crawlType == 0:
            # Parse the URLs from gathered soup
            gotUrls = self._parseForUrls(html)
            # Check if any urls were parsed
            if gotUrls:
                # If they were, pass parsed urls to the pageNode's urlList
                page.urlList = list(self.urls)
        
        # If a keyword exists, look for the keyword in text. Returns True if found
        if self.keywordExists:
            status = self.parser.parseKeyword(html, self.keyword)

            # If keyword is found, return code 1 (keyword found)
            if status == True:  
                return 1
            # Otherwise return code 0 (normal return)
            else:
                return 0
        else:  
            return 0

    def _fetch(self,urlString):

        returnObj = None
        retry = True

        # holds the URL that is actually followed if a redirect occurs
        followed = None
        while(retry):
            try:
                session = HTMLSession()
                response = session.get(urlString, timeout=3, stream=False, verify=False)
                followed = response.url

                if response.status_code == requests.codes.ok:
                    html = response.html
                else:
                    html = None
                    response.raise_for_status()
                returnObj = (html,followed)
                retry = False
            except requests.exceptions.MissingSchema:
                urlString = 'http://' + urlString
                retry = True
                continue
            except (requests.HTTPError, requests.ConnectionError, requests.ReadTimeout):
                e = sys.exc_info()
                eText = str(e[1])
                returnObj = (eText,followed)
                retry = False
            except KeyboardInterrupt:
                sys.stderr.write("\nKeyboardInterrupt detected... exiting run.\n")
                sys.exit(1)               
            except:
                e = sys.exc_info()
                sys.stderr.write(e[1])
                sys.exit(1)
            finally:
                if not retry:
                    return returnObj
        
    def _parseForUrls(self, html):
        self.urls = self.parser.parseUrls(html)
        if len(self.urls) <= 0:
            return False 
        else:
            return True

    # Accepts list of nodes
    def crawlPool(self, nodeList, crawlType):
        nodePool = dict((node,0) for node in nodeList)


        ret = self._fetchPool(nodePool)

        if ret == 0:
            self._parsePool(nodePool, crawlType)
        
        

    # Concurrently fetches all pages in the nodePool and returns once all are complete
    # nodePool: dictionary with pagenodes as keys, returns with requests html responses as values. 
    def _fetchPool(self, nodePool):
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()

        session = HTMLSession()
        async def fetchPage(url):
            try:
                response = session.get(url, timeout=3, stream=False,verify=False)
                return response
            except requests.exceptions.MissingSchema:
                url = 'http://' + url
                return await fetchPage(url)
            except requests.exceptions.ReadTimeout:
                return "Timed out"
            except requests.ConnectionError:
                return "connection error"
            except:
                e = sys.exc_info()
                return str(e[1])
                sys.exit()

        runningPool = asyncio.gather( *[fetchPage(rawNode.nodeUrl) for rawNode in nodePool.keys()] )
        responsePool = loop.run_until_complete(runningPool)

        loop.close()

        if len(responsePool) != len(nodePool):
            return 1
        else:
            responseIter = 0
            for key in nodePool.keys():
                nodePool[key] = responsePool[responseIter]
                responseIter += 1
            return 0

    # Concurrently parses all pages in the nodePool and returns once all are complete.
    # Parses for urls, keywords, and/or Title depending on parseType (0=all, 1=url+title, 2=title)
    # nodePool: dictionary of (pageNode, requests-html response) key,value pairs
    def _parsePool(self, nodePool, parseType):
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
        
        async def getURLs(poolItem, parseType):
            try:
               
                node = poolItem[0]
                resp = poolItem[1]
                html = resp.html

                title = self.parser.getPageTitle(html)
                node.setTitle(title)
                
                if parseType == 1 or parseType == 0:
                    links = self.parser.parseUrls(html)
                    node.urlList = list(links)

                if parseType == 0:
                    keywordStatus = self.parser.parseKeyword(html, self.keyword)
                    node.setKeywordStatus(keywordStatus)
                
                node.setCrawledStatus(True)
                return 0
            except:
                e = sys.exc_info()
                sys.stderr.write(str(e[1]))
                node.setCrawledStatus(True)
                return 1

        runningPool = asyncio.gather( *[getURLs(item,1) for item in nodePool.items()] )
        
        parsedPool = loop.run_until_complete(runningPool)
        loop.close()
        return 0
