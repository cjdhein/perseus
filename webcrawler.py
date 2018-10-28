from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2
import sys
from webparser import WebParser
from pagenode import pageNode


class WebCrawler:
    # Performs crawling of provided web address
    

    def __init__ (self, keyword):
        self.keyword = keyword
        self.parser = WebParser()
        self.urlDict = {}
    
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
        if self._parseForUrls(theSoup,page.nodeUrl):
            print "no links?"
        if self._parseForKeyword(theSoup):
            return 3
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
            print("Error " + str(e.code) + ": " + str(e.reason))
            return("Error " + str(e.code) + ": " + str(e.reason))
        return bs(html,'lxml')

        


    def _parseForUrls(self, soup,urlString):
        temp = self.parser.parseUrls(soup,urlString)
        self.urlDict = temp
        if len(self.urlDict.keys()) <= 0:
            return True 
        else:
            return False
        

    def _parseForKeyword(self, soup):
        return self.parser.parseKeyword(soup,self.keyword)
    


