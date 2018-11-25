import sys
import requests_html
import pdb
import re



class WebParser(object):

    __slots__ = []

    def parseKeyword(html, keyword):

        # convert keyword to lowercase unicode for searching
        ukey = str(keyword).lower()

        # obtain full text contents of the page (as unicode) and make it lowercase
        fullText = html.full_text.lower()
        
        if fullText.count(ukey) > 0:
            return True
        else:
            return False


    def getPageTitle(html):
        try:

            if type(html) == str:
                return html
            # Returns a list of all matching elements
            title = html.find('title')

            # Title will have zero length if no matching tag is found
            if len(title) < 1:
                title = "Page had no title"
            else:
                title = title[0].text
        except:
            pdb.set_trace()
            e = sys.exc_info()
            sys.stderr.write(str(e[1]))
            exit(1)
        return title

    # parseUrls
    # Desc:     parses provided Requests-http object for all links in absolute form
    # Args:     html - a Requests-HTTP representation of the HTML content fetched from the url
    # Returns:  a set containing each unique absolute link found in the html
    def parseUrls(html):

        try:
            allLinks = list(html.absolute_links)
            scrubbedlinks = WebParser._scrubExtensions(allLinks)
            return scrubbedlinks
        except UnicodeDecodeError:
            raise
        except:
            e = sys.exc_info()
            sys.stderr.write(e[1])
            sys.exit(1)

    # Remove all links that end in invalid extensions
    def _scrubExtensions(links):
        scrubbed = list()
        preLen = len(links)
        while len(links) >= 1:
            link = links.pop()
            match = re.search(r".*(?:jpe?g|png|svg|gif|bmp|exe|pdf|zip)$",link)
            if match is None:
                scrubbed.append(link)

        return scrubbed
