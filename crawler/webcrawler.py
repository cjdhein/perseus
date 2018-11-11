from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2
import sys
from webparser import WebParser
from pagenode import PageNode
import pdb

DEBUG = True

class WebCrawler:
    # Performs crawling of provided web address

    def __init__ (self,keyword=None):
        self.parser = WebParser()
        self.urlDict = {}

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

        # Check if nodeUrl has a valid scheme (http / https). If not, pre-pend http scheme to it
        parsedUrl = urlparse(page.nodeUrl)

        # if a scheme was not found / recognized
        if parsedUrl.scheme == '':
            # First check if it is a scheme agnostic link
            if page.nodeUrl[:2] == '//':
                # If it is, prepend http: and proceed
                page.nodeUrl = 'http:' + page.nodeUrl
            else:
                # Otherwise, prepend with // and proceed
                page.nodeUrl = 'http://' + page.nodeUrl
        
        fetched = self._fetch(page.nodeUrl)
        loadedUrl = fetched[1]
        theSoup = fetched[0]
        
        # if we got a string back, there was an error fetching
        # return code 2 (error)
        if type(theSoup) == str:
            page.setTitle("Invalid, broken, or otherwise unreachable URL")
            page.setError(theSoup)
            return 2
        
        # if DEBUG:
        #     print self.parser.getPageTitle(theSoup)
        page.setTitle(self.parser.getPageTitle(theSoup))
        page.setCrawledStatus(True)
        
        if crawlType == 0:
            # Parse the URLs from gathered soup
            self.urlDict = self.parser.parseUrls(theSoup, loadedUrl)
            # Check if any urls were parsed
            if len(self.urlDict.keys()) > 0:
                # If they were, pass parsed urls to the pageNode's urlList
                page.urlList = self.urlDict.keys()        
        
        # If a keyword exists, look for the keyword in text. Returns True if found
        if self.keywordExists:
            status = self.parser.parseKeyword(theSoup, self.keyword)

            # If keyword is found, return code 1 (keyword found)
            if status == True:  
                return 1
            # Otherwise return code 0 (normal return)
            else:
                return 0
        else:  
            return 0

    # fetch the web page and pull all href elements / build urls
    # returns tuple of (bs4 object, url loaded). url loaded is returned to ensure we use the possibly redirected url
    #   or a string in the even an exception occurred accessing the url
    def _fetch(self, urlString):
        # flesh out
        url = urlString
        followed = None
        try:
            html = urllib2.urlopen(url)
            followed = html.geturl()
            html = html.read()
        except:
            e = sys.exc_info()
            sys.stderr.write("Error " + str(e[0]) + ": " + str(e[1]))

            return("Error: " + str(e[1]), followed)
        return (bs(html,'lxml'),followed)

        
    def _parseForUrls(self, soup, urlString):
        temp = self.parser.parseUrls(soup,urlString)
        self.urlDict = temp
        if len(self.urlDict.keys()) <= 0:
            return False 
        else:
            return True
        


    


