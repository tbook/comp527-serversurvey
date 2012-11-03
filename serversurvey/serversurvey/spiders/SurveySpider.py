import csv, sys

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
        
        self.handle_httpstatus_list = range(0,1000)
        
        print 'Opening Alexa URL CSV, please wait.'
        maxSites = 500
        
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
        requests.append(Request(url, method='GET', meta={'REQUEST_TYPE':'GET'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Create a partial get request
        requests.append(Request(url, method='GET', headers={'bytes': '0-50'}, meta={'REQUEST_TYPE':'PARTIAL_GET'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Create a conditional get request
        requests.append(Request(url, method='GET', headers={'If-Modified-Since': 'Sun, 27 Oct 2030 01:00:00 GMT'}, meta={'REQUEST_TYPE':'CONDITIONAL_GET'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Create a head request
        requests.append(Request(url, method='HEAD', meta={'REQUEST_TYPE':'HEAD'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Create a options request
        requests.append(Request(url, method='OPTIONS', meta={'REQUEST_TYPE':'OPTIONS'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Create a trace request
        requests.append(Request(url, method='TRACE', meta={'REQUEST_TYPE':'TRACE'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
       
        #Request index.html as a stylesheet request
        requests.append(Request(url, method='GET', meta={'REQUEST_TYPE':'GET_HTML_AS_CSS'}, headers={'Accept': 'text/css'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Request robots.txt as a stylesheet request
        requests.append(Request(url + "/robots.txt", method='GET', meta={'REQUEST_TYPE':'GET_TXT_AS_CSS'}, headers={'Accept': 'text/css'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Request a relative URL
        requests.append(Request(url + "/../", method='GET', meta={'REQUEST_TYPE':'GET_RELATIVE_URL'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        #Request the Favicon
        requests.append(Request(url + "/favicon.ico", method='GET', meta={'REQUEST_TYPE':'GET_FAVICON'}, dont_filter=True, callback=self.parse, errback=self.parseFailure))
        
        return requests

    def parse(self, response):
        """
        Parses stuff
        """
        
        #Save header data
        item = ServersurveyItem()
        item['responseUrl'] = response.url
        item['requestUrl'] = response.request.url
        item['version'] = response.headers.get('Server')
        item['contentType'] = response.headers.get('Content-Type')
        item['header'] = response.headers.__str__()
        item['status'] = response.status
        
        item['requestMethod'] = response.request.method
        item['requestHeaders'] = response.request.headers
        
        item['contentLength'] = response.headers.get('Content-Length')
        
        item['actualBodyLength'] = sys.getsizeof(response.body)
        
        item['requestType'] = response.request.meta.get('REQUEST_TYPE')
        
        # things to do: - figure how to store and analyze data from crawler
        #               - figure our a way to ask for features on the server
        #               - figure out a way to test server version via behavior (bugs)
        
        return item
        
    def parseFailure(self, failure):
        """
        Parses the TwistedFailure failure and hands it along to parse TODO: just print error to screen for now
        """
        print 'Parse Failure:'
        print failure.getErrorMessage()
