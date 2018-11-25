import sys
import asyncio
from requests_html import HTMLSession, AsyncHTMLSession
import requests
from requests import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from webparser import WebParser
from pagenode import PageNode
import pdb
from urllib.parse import urlparse

DEBUG = False

# Performs crawling of provided web address
class WebCrawler(object):

    __slots__ = ['parser','urls','keywordExists','keyword']
    def __init__ (self,keyword=None):
        self.urls = set()

        if keyword is None:
            self.keywordExists = False
        else:
            self.keywordExists = True
            self.keyword = keyword


    # crawlTypes:
    #   0: full crawl (urls, title, keyword)
    #   1: fast crawl (title, keyword)
    # Return codes:
    #   0: good return
    #   1: found keyword
    #   2: Error opening URL
    def crawl(self, page, crawlType):

        resp = self._fetch(page.nodeUrl)

        # response of 2 means error occurred
        if type(resp) is str:
            page.setError(resp)
            return 2

        try:
            self._parsePage(page,resp,crawlType)
        except AttributeError:
            e = sys.exc_info()
            page.setError(str(e[1]))
            return 2
        except KeyboardInterrupt:
            sys.stderr.write("\nKeyboardInterrupt detected... exiting run.\n")
            sys.exit(1)               
        except:
            pdb.set_trace()
            e = sys.exc_info()
            sys.stderr.write(str(e[0]) + " " + str(e[1]))
            page.setError(str(e[0]))
            return 2
        
        # If keyword is found, return code 1 (keyword found)
        if page.getKeywordStatus():
            return 1
        else:
            return 0

    # Perform HTML get request on the provided urlString
    # and returning the response object
    def _fetch(self,urlString):

        returnObj = None
        retry = True

        while(retry):
            try:
                session = HTMLSession()
                response = session.get(urlString, timeout=4, stream=False, verify=False)

                if response.status_code == requests.codes.ok:
                    html = response.html
                else:
                    html = None
                    response.raise_for_status()
                returnObj = response
                retry = False
            except requests.exceptions.MissingSchema:
                pdb.set_trace()
                urlString = 'http://' + urlString
                retry = True
                continue
            except (requests.HTTPError, requests.ConnectionError, requests.ReadTimeout):
                e = sys.exc_info()
                eText = str(e[1])
                returnObj = eText
                retry = False
            except KeyboardInterrupt:
                sys.stderr.write("\nKeyboardInterrupt detected... exiting run.\n")
                sys.exit(1)               
            except:
                e = sys.exc_info()
                sys.stderr.write(str(e[1]))
                returnObj = str(e[1])
            finally:
                if not retry:
                    return returnObj

    # Crawls the provided list of nodes using the provided crawl type. 
    # crawlTypes:
    #   0: full crawl (urls, title, keyword)
    #   1: fast crawl (title, keyword)      
    def crawlPool(self, nodeList, crawlType):

        # Get the active event loop
        loop = asyncio.get_event_loop()

        # If it closed, create and assign a new loop
        if loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()

        # obtain the pool of tasks
        taskPool = self._fetchPool(nodeList)

        # have the loop run until all tasks are complete
        responsePool = loop.run_until_complete(taskPool)
        taskPool = None
        loop.close()

        # Ensure we have a response for each node
        if len(responsePool) != len(nodeList):
            sys.stderr.write("Response/Page mismatch - the number of responses does not equal the number of pages\n")
        else:
            # assign responses as the value for each node key
            if DEBUG:
                print("Parsing pool...")

            # Flag to indicate if keyword was hit and then return proper code
            keywordHit = False
            
            # Loop over nodes and parse each
            for i in range(len(nodeList)):
                if type(responsePool[i]) is str:
                    nodeList[i].setError(responsePool[i])
                else:
                    self._parsePage(nodeList[i],responsePool[i],crawlType)
                if nodeList[i].getKeywordStatus():
                    keywordHit = True
                    break

                # Remove reference to response to enable it to be freed
                responsePool[i] = None
        
            responsePool = None

        if keywordHit:
            return 2
        else:
            return 0       
        
    # Creates, gathers, and returns a set of asyncio tasks that will asynchronously fetche all pages in the nodePool 
    # nodePool: dictionary with pagenodes as keys, returns with requests html responses as values. 
    async def _fetchPool(self, nodePool):
        if DEBUG:
            print("Fetching pool...")

        # The function comprising the asyncio tasks
        async def fetch(self,url):
            try:
                response = await session.get(url,timeout=5, stream=True,verify=False)
                if response.status_code != requests.codes.ok:
                    response.raise_for_status()
                else:
                    # Good response, so return the html
                    return response
            # If schema is missing, retry after prepending http
            except requests.exceptions.MissingSchema:
                url = 'http://' + url
                return await fetch(self,url)
            except (requests.HTTPError, requests.ConnectionError, requests.ReadTimeout):
                e = sys.exc_info()
                eText = str(e[1])
                return eText                
            except KeyboardInterrupt:
                sys.stderr.write("\nKeyboardInterrupt detected... exiting run.\n")
                sys.exit(1)               
            except:
                e = sys.exc_info()
                return (str(e[1]) + "\n")

        # Create async session for performing requests
        session = AsyncHTMLSession()

        # Use a semaphore to limit to 10 simultaneous calls
        semaphore = asyncio.BoundedSemaphore(10)

        tasks = []

        
        # Builds the task for each node
        # await the semaphore so no more that 10 calls happen at once
        for node in nodePool:
            await semaphore.acquire()
            f = asyncio.ensure_future(fetch(self,node.nodeUrl))
            f.add_done_callback(lambda f: semaphore.release())
            tasks.append(f)

        taskPool = await asyncio.gather(*tasks, return_exceptions=True)
        #await session.close()
        tasks = None
        return taskPool


    # parseTypes:
    #   0: full crawl (urls, title, keyword)
    #   1: fast crawl (title, keyword)    
    def _parsePage(self,node,resp,parseType):
        try:
            # If the response was a string, there was an exception
            # and the exception text is assigned as the node title
            if type(resp) == str or resp == None:
                if resp is None:
                    page.setTitle("Invalid, broken, or otherwise unreachable URL")
                else:
                    node.setTitle(resp)
                return 2
            else:
                html = resp.html
             
            # If parseType is zero we are interested in the URLs
            # otherwise just the title and keywords
            if parseType == 0:
                node.urlList = WebParser.parseUrls(html)

            # Parse and assign page title
            title = WebParser.getPageTitle(html)
            node.setTitle(title)
            
            # If a keyword exists, parse for it
            if self.keywordExists:
                    keywordStatus = WebParser.parseKeyword(html, self.keyword)
                    node.setKeywordStatus(keywordStatus)
            
            node.setCrawledStatus(True)

            # Cleanup
            del(resp)
            resp = None

            return 0

        except KeyboardInterrupt:
            sys.stderr.write("\nKeyboardInterrupt detected... exiting run.\n")
            sys.exit(1)               
        except:
            pdb.set_trace()
            e = sys.exc_info()
            sys.stderr.write("In parse page: "+ str(e[1]))
            node.setError(str(e[0]))
            node.setCrawledStatus(True)
            return 1
