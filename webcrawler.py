from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2
from webparser import WebParser


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

    def crawl(self, urlString):
        theSoup = self._fetch(urlString)
        if (self._parseForUrls(theSoup,urlString) == 1):
            print "no links?"
#        self._parseForKeyword()
        

    # fetch the web page and pull all href elements / build urls
    def _fetch(self, urlString):
        # flesh out
        url = urlString
        html = urllib2.urlopen(url).read()
        return bs(html,'lxml')

        


    def _parseForUrls(self, soup,urlString):
        temp = self.parser.parseUrls(soup,urlString)
        self.urlDict = temp
        if len(self.urlDict.keys()) <= 0:
            return 1 
        else:
            return 0
        

    def _parseForKeyword(self):
        return 1 #self.parser.parseKeyword(self.keyword)
    


