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
        maxSites = 5
        
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
        
        #Create a get
        print 'Creating request for ' + url
        requests.append(Request(url, method='GET'))
        
        #Create a head
        
        #Create a options
        
        #Create a trace
        

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
        
        # things to do: - figure how to store and analyze data from crawler
        #               - figure our a way to ask for features on the server
        #               - figure out a way to test server version via behavior (bugs)
        
        return item
