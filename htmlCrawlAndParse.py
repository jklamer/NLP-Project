from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
import time
import re

class StartreckLinkParser(HTMLParser):

    links=[]
    baseUrl=""
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for key , value in attrs:
                if key == 'href' and re.match("[0-9]{3}.htm",value):
                    self.links.append(parse.urljoin(self.baseUrl,value))

class ScriptParse(HTMLParser):
    pattern = re.compile(r'^.*:')
    def handleLink(self, url):
        responce = urlopen(url)
        if responce.getheader('Content-Type') == 'text/html; charset=windows-1252':
            #time.sleep(100)
            htmlBytes = responce.read()
            self.feed(str(htmlBytes))
        else:
            print("Not Right Content type")

    def parseScriptLinks(self, links, output):
        self.output = output
        for link in links:
            print("Processng "+link)
            self.handleLink(link)

    def handle_data(self, data):
        data = data.replace("\\r\\n"," ").replace("\\'","'")
        if self.pattern.match(data):
            #print(data)
            self.output.write(data)
            self.output.write("\n")


if __name__ == "__main__":
    parser = StartreckLinkParser()
    parser.baseUrl = "http://www.chakoteya.net/DS9/episodes.htm"
    f = open("data/ds9links.html","r")
    data = f.read().replace("\n"," ")
    parser.feed(data)
    sp = ScriptParse()
    sp.parseScriptLinks(parser.links,open("data/ds9scripts3.txt","w",encoding='utf-8'))

