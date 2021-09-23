from scrapy.cmdline import execute

import sys
import os

website = 'meiju'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy", "crawl", website])
