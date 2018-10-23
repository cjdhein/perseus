from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2
import sys

url = "https://www.gutenberg.org/files/11/11-h/11-h.htm"
keyword = str(sys.argv[1])
print "Searching Alice in Wonderland for the word " + keyword
html = urllib2.urlopen(url).read()

soup = bs(html,'lxml')

theText = soup.get_text().lower()

uniSearch = unicode(keyword)

found = theText.count(uniSearch.lower())

if found >= 1:
    print "Found '" + keyword + "' in the text!"
else:
    print keyword + " was not found in the text."
