import csv

from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from serversurvey.items import ServersurveyItem

class SurveySpider(BaseSpider):
    """
    Reads in a list of URLS and retrieves server software versions.
    """
    name = 'surveyspider'
    allowed_domains = []
    start_urls = []

    def __init__(self):
        BaseSpider.__init__(self)
        
        print 'Opening Alexa URL CSV, please wait.'
        maxSites = 10
        
        csv_file = open('top-1m.csv','r') 
        reader = csv.reader(csv_file)
        
        urls = []
        rank=0
        while(rank < maxSites):
            domain = reader.next()[1]
            self.allowed_domains.append( domain )
            urls.append( 'http://www.' + domain ) 
            rank += 1
        
        self.start_urls += urls
        
        csv_file.close()
        print 'Done opening URLs, starting crawler....'

    def make_requests_from_url(self, url):
        """
        Prepares the requests for the spider
        """
        requests = []
        
        print 'Creating requests for ' + url
        
        #Create a get request
        requests.append(Request(url, method='GET'))
        
        #Create a partial get request
        requests.append(Request(url, method='GET', headers={'bytes': '0-50'}))
        
        #Create a conditional get request
        requests.append(Request(url, method='GET', headers={'If-Modified-Since': 'Sun, 27 Oct 2030 01:00:00 GMT'}))
        
        #Create a head request
        requests.append(Request(url, method='HEAD'))
        
        #Create a options request
        requests.append(Request(url, method='OPTIONS'))
        
        #Create a trace request
        requests.append(Request(url, method='TRACE'))
       
        #Request index.html as a stylesheet request
        requests.append(Request(url, method='GET', headers={'Accept': 'text/css'}))
        
        #Request robots.txt as a stylesheet request
        requests.append(Request(url + "/robots.txt", method='GET', headers={'Accept': 'text/css'}))
        
        return requests

    def parse(self, response):
        """
        Parses stuff
        """
        
        #Save header data
        item = ServersurveyItem()
        item['url'] = response.url
        item['version'] = response.headers.get('Server')
        item['contentType'] = response.headers.get('Content-Type')
        item['header'] = response.headers.__str__()
        item['status'] = response.status
        
        item['requestMethod'] = response.request.method
        item['requestHeaders'] = response.request.headers
        
        item['contentLength'] = response.headers.get('Content-Length')
        
        #response.body
        
        # things to do: - figure how to store and analyze data from crawler
        #               - figure our a way to ask for features on the server
        #               - figure out a way to test server version via behavior (bugs)
        
        return item
