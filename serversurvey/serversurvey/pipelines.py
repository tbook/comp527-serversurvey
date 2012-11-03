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

        headerRow = ['requestUrl',
                     'responseUrl', 
                     'status',
                     'requestType',
                     'requestMethod',
                     'version',
                     'contentType',
                     'contentLength',
                     'actualBodyLength',
                     'header',
                     'requestHeaders'
                     ]
        row = []

        for columnName in headerRow:
            # pick out the thing in the dictionary 
            if item[ headerRow[columnName] ] == None: 
                row.append( '' )
            else:
                row.append( item[ headerRow[columnName] ] )

        self.csvwriter.writerow(headerRow)
        self.csvwriter.writerow(row)
        
        return item
