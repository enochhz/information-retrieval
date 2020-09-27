import csv
from bs4 import BeautifulSoup
# for selennium import webdriver
from urllib.request import urlopen
import time

import unittest
from test import support

from urllib import parse
from urllib import robotparser

class Crawler:
    page_limit = 100
    page_map = {}
    page_stack = []
    disallow_stack = []
    allow_stack = []
    disallow_stack = []
    
    def __init__(self, seed_url, language:str):
        self.page_stack.append(seed_url)
        self.lang = language
        
    def parse_pages(self):
        while len(self.page_stack) > 0: 
            if (len(self.page_map.keys()) > self.page_limit): return
            
            page_url = self.page_stack.pop() #DFS
            
            print(page_url)
            
            html = urlopen(page_url).read().decode('utf-8')
            soup = BeautifulSoup(html, features='lxml')
            all_href = soup.find_all("a")
            all_href = [l['href'] for l in all_href]
            self.page_map[page_url] = len(all_href)
            # do we need to check if the page is exist
#             print(self.page_map)
            for link in all_href:
                self.page_stack.append(link)
    
    # checkRobots(page_url) 
    def check_robots_url(self, page_url, check_url) -> bool:
        agent_name = '*'
        if page_url.endswith('/'):
            url_base = page_url
        else: 
            url_base = page_url + '/'
            
        parser = robotparser.RobotFileParser()
        parser.set_url(parse.urljoin(url_base, 'robots.txt'))
        parser.read()

        if parser.can_fetch(agent_name, check_url):
            self.allow_stack.append(check_url)
            return True
        else:
            self.disallow_stack.append(check_url)
            return False


# seed = 'https://techcrunch.com/'
# seed = 'https://www.google.com/'
# seed = 'https://news.yahoo.com/'
seed = 'https://yahoo.com/'
# seed = 'https://www.doughellmann.com/blog/'
crawler = Crawler(seed, '')

yahoo_PATHS = [
    '/',
    '/p/',
    '/blank.html',
    '/myjs',
    '/bin/',
    '/gma/sitemaps/gma-sitemap_articles_US_en-US.xml'     
]

for path in yahoo_PATHS:
    crawler.check_robots_url(seed, path)

print("allow: ", crawler.allow_stack)
print("disallow: ", crawler.disallow_stack)