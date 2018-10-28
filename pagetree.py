from webcrawler import WebCrawler

class PageTree:

    def __init__ (self, startUrl, limit, keyword, searchType):
        self.startPage = startUrl
        self.levelLimit = limit
        self.keyword = keyword
        self.keywordExists = False
        self.searchType = searchType
        self.curLevel = 0
        self.webCrawler = WebCrawler()
        self.rootNode = PageNode(None,0,startUrl) 

    def beginCrawl(self):
        wc = self.webCrawler

        


        while (self.curLevel <= self.levelLimit) and self.keywordExists == False:
            result = self.webCrawler.crawl
