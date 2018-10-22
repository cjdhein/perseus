from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2

url = "https://www.gutenberg.org/files/11/11-h/11-h.htm"

html = urllib2.urlopen(url).read()

soup = bs(html,'lxml')

theText = soup.get_text().lower()

uniSearch = unicode("gutenbe")
print theText.count(uniSearch.lower())
