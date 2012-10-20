# Scrapy settings for serversurvey project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'serversurvey'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['serversurvey.spiders']
NEWSPIDER_MODULE = 'serversurvey.spiders'
DEFAULT_ITEM_CLASS = 'serversurvey.items.ServersurveyItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

