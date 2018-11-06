from urlparse import urlparse
import re
import pdb


class WebParser:

    def parseKeyword(self, soup, keyword):

        # convert keyword to lowercase unicode for searching
        ukey = unicode(keyword).lower()

        # obtain full text contents of the page (as unicode) and make it lowercase
        fullText = soup.get_text().lower()
        
        if fullText.count(ukey) > 0:
            return True
        else:
            return False


    def getPageTitle(self,soup):
        return soup.find('title').string

    def linkFindHelper(self,tag):
        valid = (tag.name == u'a' and tag.has_attr('href'))
        if valid:
            href = tag['href']
            pattern = "(\.(?=(htm|asp|shtm|php|do))\w{2,5}$|\/\w*?$)"
            status = re.search(pattern,href)

        return True if valid and status else False

    # parseUrls
    # Desc:     parses provided BeautifulSoup object for all links and constructs full urls out of them
    # Args:     soup - a beautiful soup 4 object with html; url - the url the soup belongs to
    # Returns:  dict with each unique, full url, link found in the html
    def parseUrls(self,soup,url):

        uniqueLinks = {}

        # all 'a' elements with href
        aTags = soup.find_all(self.linkFindHelper)

        # url info separated
        urlInfo = urlparse(url)

        # base of our url

        if len(urlInfo.scheme) <= 0:
            print "da hek?"
            print urlInfo
            print url

        baseUrl = urlInfo.scheme + '://' + urlInfo.netloc
        baseWithPath = baseUrl + urlInfo.path
        # Obtain full url for each link
        for aTag in aTags:
            urlToAdd = ''

            # confirm the link actually leads somewhere, if it doesn't skip it
            if len(aTag['href']) <= 0:
                continue
                print "\n\n\nBLANK LINK\n\n\n"

            # if base url is not in the href attribute, we need to build out the full url, provided it does not link to another domain / netloc
            if baseUrl not in aTag['href']:
        
                # check if there is another domain/netloc
                hrefNetloc = urlparse(aTag['href']).netloc
                if len(hrefNetloc) > 0:
                    temp = urlparse(aTag['href'])
                    urlToAdd = temp.scheme + "://" + temp.netloc + temp.path # another domain is included, so add as is
                else:
                    if aTag['href'][0] == '/':
                        urlToAdd = baseUrl + aTag['href']
                    else:
                        continue
#                    urlToAdd = baseUrl + aTag['href'] # no other domain is included, so prepend the page url
            # base url is in href, so we can add as is
            else:
                urlToAdd = aTag['href']

            # add urlToAdd to urlDict if it doesn't already exist
#            splitUrl = urlparse(urlToAdd)
 #           urlToAdd = splitUrl.scheme + '://' + splitUrl.netloc + splitUrl.path
  #          uniqueLinks[urlToAdd] = 1
            
            #strip off trailing / to help ensure no duplication
            if urlToAdd[len(urlToAdd)-1] == '/':
                urlToAdd = urlToAdd[:len(urlToAdd)-1]
            if urlToAdd != '':
                uniqueLinks[urlToAdd] = 1

        return uniqueLinks

