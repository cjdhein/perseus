from bs4 import BeautifulSoup as bs
from urlparse import urlparse
import urllib2

url = "https://www.nytimes.com"

html = urllib2.urlopen(url).read()

soup = bs(html,'lxml')

print(soup.title.string)

all_Links = soup.find_all('a', href=True)

reqInfo = []
parsed = urlparse(url)
baseUrl = parsed.scheme + '://' + parsed.netloc

# Get full urls
for link in all_Links:
    urlToAdd = ''
    
    # If our root url is not in the link
    if baseUrl not in link['href']:
        
        # Check if there is a netlocation in the parsed url
        parsed = urlparse(link['href']).netloc

        # If there is, it links to another domain, so we log the entire url
        if len(parsed) != 0:
            urlToAdd = link['href']
        # Otherwise it is an href to a sub path, so we add the root url to create full link
        else:
            urlToAdd = baseUrl + link['href']
    # if the root url is in the link, we can log the full url
    else:
        urlToAdd = link['href']

    if reqInfo.count((urlToAdd,())) == 0:
        reqInfo.append({'url':urlToAdd})

print reqInfo
