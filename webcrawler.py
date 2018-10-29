from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2
import sys
from webparser import WebParser
from pagenode import PageNode


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
    #   1: good return
    #   2: hit depth (won't trigger in webcrawler)
    #   3: found keyword
    #   4: Error opening URL
    def crawl(self, page):
        theSoup = self._fetch(page.nodeUrl)
        if type(theSoup) == str:
            return theSoup
        page.setTitle(self.parser.getPageTitle(theSoup))

        # Parse the URLs from gathered soup
        self.urlDict = self.parser.parseUrls(theSoup, page.nodeUrl)
        
        # Check if any urls were parsed
        if len(self.urlDict.keys()) > 0:
            # If they were, pass parsed urls to the pageNode's urlList
            page.urlList = self.urlDict.keys()
        
        # If a keyword exists, look for the keyword in text. Returns True if found
        if self.keywordExists:
            status = self.parser.parseKeyword(theSoup, self.keyword)

            # If keyword is found, return code 3 (keyword found)
            if status == True:  
                return 3
            # Otherwise return code 1 (normal return)
            else:
                return 1
        else:  
            return 1
        

    # fetch the web page and pull all href elements / build urls
    def _fetch(self, urlString):
        # flesh out
        url = urlString
        try:
            html = urllib2.urlopen(url)
            html = html.read()
        except:
            e = sys.exc_info()[1]
            print e
            #print("Error " + str(e.code) + ": " + str(e.reason))
            #return("Error " + str(e.code) + ": " + str(e.reason))
            return e
        return bs(html,'lxml')

        
    def _parseForUrls(self, soup, urlString):
        temp = self.parser.parseUrls(soup,urlString)
        self.urlDict = temp
        if len(self.urlDict.keys()) <= 0:
            return False 
        else:
            return True
        


    


