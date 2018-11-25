import sys
import requests_html
import pdb



class WebParser(object):

    __slots__ = []

    def parseKeyword(html, keyword):

        # convert keyword to lowercase unicode for searching
        ukey = str(keyword).lower()

        # obtain full text contents of the page (as unicode) and make it lowercase
        fullText = html.get_text().lower()
        
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
            e = sys.exc_info()
            sys.stderr.write(str(e[1]))
            exit(1)
        return title

    # parseUrls
    # Desc:     parses provided Requests-http object for all links in absolute form
    # Args:     html - a Requests-HTTP representation of the HTML content fetched from the url
    # Returns:  a set containing each unique absolute link found in the html
    def parseUrls(html):

        uniqueLinks = {}

        try:
            all_links = html.absolute_links
            return all_links
        except:
            e = sys.exc_info()
            sys.stderr.write(e[1])
            sys.exit(1)
