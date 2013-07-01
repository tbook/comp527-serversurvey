# Scrapy settings for serversurvey project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'serversurvey'
#BOT_VERSION = '1.0'

ITEM_PIPELINES = ['serversurvey.pipelines.ServersurveyPipeline']

SPIDER_MODULES = ['serversurvey.spiders']
NEWSPIDER_MODULE = 'serversurvey.spiders'
DEFAULT_ITEM_CLASS = 'serversurvey.items.ServersurveyItem'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36'
LOG_LEVEL = 'INFO'
CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 1

