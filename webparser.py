from urlparse import urlparse

class WebParser:

    # parseUrls
    # Desc:     parses provided BeautifulSoup object for all links and constructs full urls out of them
    # Args:     soup - a beautiful soup 4 object with html; url - the url the soup belongs to
    # Returns:  dict with each unique, full url, link found in the html

    def parseUrls(self,soup,url):

        uniqueLinks = {}

        # all 'a' elements with href
        aTags = soup.find_all('a', href=True)
        # url info separated
        urlInfo = urlparse(url)

        # base of our url
        baseUrl = urlInfo.scheme + '://' + urlInfo.netloc

        # Obtain full url for each link
        for aTag in aTags:
            fullUrl = ''

            # if base url is not in the href attribute, we need to build out the full url, provided it does not link to another domain / netloc
            if baseUrl not in aTag['href']:

                # check if there is another domain/netloc
                hrefNetloc = urlparse(aTag['href']).netloc
                if len(hrefNetloc) > 0:
                    fullUrl = aTag['href'] # another domain is included, so add as is
                else:
                    fullUrl = baseUrl + aTag['href'] # no other domain is included, so prepend the base url
            # base url is in href, so we can add as is
            else:
                fullUrl = aTag['href']

            # add fullUrl to urlDict if it doesn't already exist
            splitUrl = urlparse(fullUrl)
            urlToAdd = splitUrl.scheme + '://' + splitUrl.netloc + splitUrl.path
            uniqueLinks[urlToAdd] = 1

        return uniqueLinks

