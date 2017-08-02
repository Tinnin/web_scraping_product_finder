from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib import parse
import redis

class MyHTMLParser(BeautifulSoup):

    def __init__(self, url):
        self.baseUrl = url
        response = urlopen(url)
        if response.getheader('Content-Type').find('text/html') > -1:
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            super(MyHTMLParser, self).__init__(htmlString, 'html.parser')

    def getLinks(self):
        self.links = []
        for link in self.find_all('a'):
            newUrl = parse.urljoin(self.baseUrl, link.get('href'))
            self.links.append(newUrl)
        return self.links

    def getProduct(self):
        productElement = self.select('h1.ProductDetailsProductName span')
        if productElement:
            print('Product found!')
            print(productElement[0].getText())
            priceElement = self.select('#lblPrice')
            print(priceElement[0].getText())
                

def spider(baseUrl):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.delete('visited_urls')
    pagesToVisit = [baseUrl]
    numberVisited = 0
    while pagesToVisit != []:
        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        if not r.sismember('visited_urls', url) and url.find(baseUrl) > -1:
            r.sadd('visited_urls', url)
            numberVisited = numberVisited + 1
            print(numberVisited, "Visiting:", url)
            try:
                parser = MyHTMLParser(url)
                parser.getLinks()
                pagesToVisit = pagesToVisit + parser.getLinks()
                parser.getProduct()
            except:
                print(" **Failed!**")

spider("http://www.trossenrobotics.com")

