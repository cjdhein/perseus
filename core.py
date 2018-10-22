# Used to test class implementations

from webcrawler import WebCrawler


spidey = WebCrawler("brandy")
print spidey.crawl("https://www.nytimes.com/")
print spidey
