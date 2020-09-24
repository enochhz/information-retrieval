import csv
import re
from bs4 import BeautifulSoup
# from selenium import webdriver
from urllib.request import urlopen
import time
import pandas as pd
import collections
import requests

class Crawler:

    page_limit = 5
    html_folder = 'folder' 
    page_map = {}
    error_map = {}
    page_stack = []
    recent_visited_hosts = collections.deque([], maxlen = 10)
    visited_hosts = set()
    skip = 0

    def __init__(self, seed_url, language: str):
        self.page_stack.append(seed_url)
        self.lang  = language

    def parse_pages(self):
        while len(self.page_stack) > 0:
            if (len(self.page_map.keys()) > self.page_limit): break 
            try:
                page_url = self.page_stack.pop(0) # poll first 
                host_name = self.extract_host_name(page_url)
                if  host_name not in self.recent_visited_hosts or self.skip == 10:
                    if host_name not in self.recent_visited_hosts: self.recent_visited_hosts.append(host_name)
                    self.visited_hosts.add(host_name)
                    skip = 0
                elif host_name in self.recent_visited_hosts:
                    self.page_stack.append(host_name)
                    skip += 1
                    continue
                self.check_language()
                self.check_robots_txt()
                if page_url.endswith('.html'):
                    print(page_url)
                    html = requests.get(page_url).text # or content
                    self.store_html(page_url, html)
                    self.count_links(page_url, html)
                else:
                    html = urlopen(page_url).read().decode('utf-8')
                    self.store_html(page_url, html)
                    self.count_links(page_url, html)
            except Exception as e:
                self.error_map[page_url] = str(e)
        self.write_to_csv('./info.csv')
        self.write_error_csv('./error.csv')
    
    def store_html(self, page_url: str, html: str):
        path_name = re.split('http[s]?://', page_url)[1]
        path_name = path_name.replace('/', '#')
        if page_url.endswith('.html') or page_url.endswith('.htm'):
            file_name = f'{self.html_folder}/{path_name}'
        else:
            file_name = f'{self.html_folder}/{path_name}.html'
        text_file = open(file_name, 'w')
        text_file.write(html)
        text_file.close()

    def count_links(self, page_url: str, html: str):
        # soup = BeautifulSoup(html, features='lxml')
        soup = BeautifulSoup(html, features='html.parser')
        all_a_tags = soup.find_all('a')
        all_a_tags = filter(lambda tag: tag.get('href') is not None, all_a_tags)
        all_href = {tag['href'] for tag in all_a_tags}
        self.page_map[page_url] = len(all_href)
        host_name = self.extract_host_name(page_url)
        for link in all_href:
            # if link is relative directory: then append it to current url address
            if link.startswith('/'):
                link = page_url + link
                # print(link)
            self.page_stack.append(link)

    def write_to_csv(self, file_name: str):
        new_dict = {
            'root_url': [k for k in self.page_map.keys()], 
            'num_of_out_links': [v for v in self.page_map.values()]
        }
        pd.DataFrame.from_dict(new_dict).to_csv(file_name)
    
    def write_error_csv(self, file_name: str):
        new_dict = {
            'root_url': [k for k in self.error_map.keys()],
            'error_info': [error_info for error_info in self.error_map.values()]
        }
        pd.DataFrame.from_dict(new_dict).to_csv(file_name)

    def extract_host_name(self, page_url: str) -> str:
        url_pattern = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        return re.search(url_pattern, page_url).group('host')
    
    def check_language(self): # Check language 80%
        pass

    def check_robots_txt(self): # TODO
        pass

seed = 'https://www.yahoo.com/'
seed = 'http://www.ruanyifeng.com/blog/2020/09/weekly-issue-125.html'
# seed = 'https://techcrunch.com/'
crawler = Crawler(seed, 'English')
crawler.parse_pages()
