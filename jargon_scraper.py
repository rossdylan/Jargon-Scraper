#!/usr/bin/python
"""
jargon_scraper.py
Author: Ross Delinger
Scrape the Entirety of the Jargon file and convert it to a python dict. 
Fetched through tor to experiment with proxy's within python
"""

from HTMLParser import HTMLParser
from time import sleep

def fetchThroughTor(url):
    """
    Fetch a webpage through a local tor proxy, also spoof the user agent
    """
    import urllib2
    proxy_support = urllib2.ProxyHandler({"http":"http://127.0.0.1:8118"})
    opener = urllib2.build_opener(proxy_support)
    opener.addheaders = [('User-agent', 'Lynx/2.8.8dev.5 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.8.62011-08-01 14:40:01c')]
    page = opener.open(url)
    return page.read()

class linkParser(HTMLParser):
    """
    An HTMLParser to grab the links to the various pages of the jargon file
    Also acts as a filter to prevent the scraper from picking up unwanted webpages
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = list()
        self.getNextData = False
        self.lastLink = ""
        self.filterList = ["0.html","1.html","A.html","B.html","C.html","D.html","E.html","F.html","G.html","H.html","I.html","J.html","K.html","L.html","M.html","N.html","O.html","P.html","Q.html","R.html","S.html","T.html","U.html","V.html","W.html","X.html","Y.html","Z.html"]
    #We could probably make this a bit prettier/cleaner
    def handle_starttag(self, tag, attrs):
        if tag == 'a' and attrs[0][0] == 'href':
            link = attrs[0][1]
            if not link in self.filterList and not "mav.html" in link:
                self.lastLink = "http://www.catb.org/jargon/html/" + link
                self.getNextData = True
    
    def handle_data(self,data):
        if self.getNextData:
            self.data.append((self.lastLink, data))
            self.getNextData = False
    
    def gimmeMaData(self):
        return self.data

class definitionParser(HTMLParser):
    """
    Parse the webpages containing defintions of words in the jarogn file
    and grab the text we care about
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.data = str()
        self.getNextData = False
    
    def handle_starttag(self,tag,attrs):
        if tag == "p":
            self.getNextData = True

    def handle_data(self,data):
        if self.getNextData:
            self.data = self.data + data
    
    def handle_endtag(self,tag):
        if tag == "p":
            self.getNextData = False
    
    def gimmeMaData(self):
        return self.data

def fetchIndex():
    """
    Fetch and parse the index page of the jargon file
    """

    data = fetchThroughTor("http://www.catb.org/jargon/html/go01.html")
    p = linkParser()
    p.feed(data)
    p.close()
    return p.gimmeMaData()

def fetchDef(url):
    """
    Fetch and parse a jargon file definitions
    """
    fail = False
    try:
        data = fetchThroughTor(url)
    except Exception as e:
        fail = True
    if fail:
        return ""
    p = definitionParser()
    p.feed(data)
    p.close()
    return p.gimmeMaData()

def writeOutFileHeader(f):
    """"
    write a { to signal the start of a python dict in the file
    """
    f.write("{")
    f.flush()

def writeOutFileFooter(f):
    """
    write a } to signal the end of a python dict in the file
    """
    f.write("}")
    f.flush()
    f.close()

def writeDefToOutFile(f, title, laDef):
    """
    Write a definition to the output file in a python dict format
    """
    f.write('"""%s""":"""%s""",' % (title,laDef))
    f.flush()
 
if __name__ == "__main__":
    print "Engaging Jargon File Scraper"
    outFile = file("jargon.lol","wa")
    writeOutFileHeader(outFile)
    indexList = fetchIndex()
    print 'Fetched index of %s definitions' % len(indexList)
    counter = 0
    
    for jargonDef in indexList:
        title = jargonDef[1]
        link = jargonDef[0]
        
        if counter >= 20:
            sleep(30)
            counter = 1

        leDef = fetchDef(link)
        print "fetched %s with %s chars" % (title, len(leDef))
        writeDefToOutFile(outFile,title,leDef)
        counter = counter + 1
        sleep(2)
        
    writeOutFileFooter(outFile)
    print "Scraping of the Jargon file Complete"
    

    
