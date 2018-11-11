from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2
import sys
from webparser import WebParser
from pagenode import PageNode
import pdb

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

    # Return codes:
    #   0: good return
    #   1: found keyword
    #   2: Error opening URL
    def crawl(self, page):
        fetched = self._fetch(page.nodeUrl)
  
        loadedUrl = fetched[1]
        theSoup = fetched[0]
        
        # if we got a string back, there was an error fetching
        # return code 2 (error)
        if type(theSoup) == str:
            page.setTitle(theSoup)
            page.setCrawledStatus(True)
            return 2
        
        print self.parser.getPageTitle(theSoup)
        page.setTitle(self.parser.getPageTitle(theSoup))

        # Parse the URLs from gathered soup
        self.urlDict = self.parser.parseUrls(theSoup, loadedUrl)
        
        page.setCrawledStatus(True)
        
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
        
    def titleCrawl(self,page):
        fetched = self._fetch(page.nodeUrl)
        loadedUrl = fetched[1]
        theSoup = fetched[0]

        if type(theSoup) == str:
            page.setTitle(theSoup)
            page.setCrawledStatus(True)
            return 2

        page.setTitle(self.parser.getPageTitle(theSoup))

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
            e = sys.exc_info()[1]
            print "EXCEPTION:"
            print str(e)
            print "\n"
            #print("Error " + str(e.code) + ": " + str(e.reason))
            #return("Error " + str(e.code) + ": " + str(e.reason))
            return (str(e),followed)
        return (bs(html,'lxml'),followed)

        
    def _parseForUrls(self, soup, urlString):
        temp = self.parser.parseUrls(soup,urlString)
        self.urlDict = temp
        if len(self.urlDict.keys()) <= 0:
            return False 
        else:
            return True
        


    


