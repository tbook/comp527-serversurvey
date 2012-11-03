# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

import csv

from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter

class ServersurveyPipeline(object):

    def __init__(self):
        self.files = {}
        #TODO: Need to close file.  Should be moved to spider_opened
        self.csvwriter = csv.writer(open('%s_data.csv' % 'survey', 'wb'))

    #@classmethod
    """
    def from_crawler(self, cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        
        print 'from_crawler **************'
        return pipeline

    def spider_opened(self, spider):
        print 'spider opened ******'
    
        file = open('%s_data.csv' % spider.name, 'w+b')
        self.files[spider] = file
        self.exporter = CsvItemExporter(file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close() """



    def process_item(self, item, spider):
        #self.exporter.export()

        row = []

        if item['url'] == None: 
            row.append( '' )
        else:
            row.append( item['url'] )
            
        if item['status'] == None: 
            row.append( '' )
        else:
            row.append( item['status'] )
            
        if item['requestMethod'] == None: 
            row.append( '' )
        else:
            row.append( item['requestMethod'] )
            
        if item['requestHeader'] == None: 
            row.append( '' )
        else:
            row.append( item['requestHeader'] )

        if item['version'] == None: 
            row.append( '' )
        else:
            row.append( item['version'] )

        if item['contentType'] == None: 
            row.append( '' )
        else:
            row.append( item['contentType'] )

        if item['header'] == None: 
            row.append( '' )
        else:
            row.append( item['header'] )



        
        self.csvwriter.writerow(row)
        
        return item
