import os
import csv
import re
from bs4 import BeautifulSoup
# from selenium import webdriver
from urllib.request import urlopen
import time
import pandas as pd
import collections
import requests
from helper import detect_language
# from robots_deteor import robot_detector

class Crawler:

    html_content_folder = 'folder' 
    page_map = {}
    error_map = {}
    to_be_visited_queue = []
    recent_visited_hosts = collections.deque([], maxlen = 10)
    visited_hosts = set()
    skip = 0
    page_limit = 5
    banned_hosts = [] # To keep track of websites in different language

    def __init__(self, seed_url, language: str, page_limit: int):
        self.to_be_visited_queue = [seed_url]
        self.page_map, self.error_map = {}, {}
        self.banned_hosts = []
        self.visited_hosts = set()
        self.lang  = language
        self.page_limit = page_limit
        self.make_directories()
    
    def make_directories(self) -> None: 
        """
        Initializes necessary folder structures
        """
        if not os.path.isdir((f'./{self.html_content_folder}')):
            os.makedirs((f'./{self.html_content_folder}'))
        if not os.path.isdir((f'./{self.html_content_folder}/{self.lang}')):
            os.makedirs((f'./{self.html_content_folder}/{self.lang}'))

    def parse_pages(self):
        while (len(self.to_be_visited_queue) > 0) and (len(self.page_map.keys()) < self.page_limit): # Limit is not hit
            try:
                page_url = self.to_be_visited_queue.pop(0) # Poll the first page from the to be visited queue
                host_name = self.extract_host_name(page_url)
                if not self.evaluate_host_name(host_name): 
                    continue
                print(page_url)
                self.check_robots_txt() # TODO
                if not self.parse_and_store_page(host_name, page_url): continue
            except Exception as e: 
                self.error_map[page_url] = str(e)
        self.write_to_csv(self.page_map, 'root_url', 'num_of_out_links', './info.csv') # Write outlinks analysis csv
        self.write_to_csv(self.error_map, 'root_url', 'error_info', './error.csv') # Write error csv

    def extract_host_name(self, page_url: str) -> str:
        url_pattern = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        return re.search(url_pattern, page_url).group('host')
    
    def evaluate_host_name(self, host_name: str) -> bool: 
        """
        Evaluates whether the host of the page is valid to visit
        """
        if host_name in self.banned_hosts: return False
        elif (host_name not in self.recent_visited_hosts) or (self.skip == 10):
            if host_name not in self.recent_visited_hosts: self.recent_visited_hosts.append(host_name) # Append the current host to the queue
            self.visited_hosts.add(host_name)
            self.skip = 0
            return True
        # If the site is visited recently
        self.to_be_visited_queue.append(host_name) # Apppend the url to the to be visited queue
        self.skip += 1
        return False

    def check_robots_txt(self): # TODO
        pass
    
    def parse_and_store_page(self, host_name: str, page_url: str) -> bool:
        """
        Extract the html content and store it in the folder
        :return: False if the page is in the wrong language
        """
        if page_url.endswith('.html'): # Parse html file (e.g., https://www.test.com/main.html)
            print('html: ' + page_url)
            html = requests.get(page_url).content.decode('utf-8') 
        else: # Parse regular URL (e.g., https://www.techcruntch.com)
            html = urlopen(page_url).read().decode('utf-8')
        if not self.valid_language(host_name, html): return False
        self.store_html_content(page_url, html)
        self.count_out_links(page_url, html)
        return True
    
    def valid_language(self, host_name: str, html_content: str) -> bool: 
        language = detect_language(html_content)
        if language != self.lang: self.banned_hosts.append(host_name) # block the website if it is in different langauge
        return language == self.lang
    
    def store_html_content(self, page_url: str, html: str):
        path_name = re.split('http[s]?://', page_url)[1]
        path_name = path_name.replace('/', '#')
        if page_url.endswith('.html') or page_url.endswith('.htm'):
            file_name = f'{self.html_content_folder}/{self.lang}/{path_name}'
        else:
            file_name = f'{self.html_content_folder}/{self.lang}/{path_name}.html'
        text_file = open(file_name, 'w')
        text_file.write(html)
        text_file.close()

    def count_out_links(self, page_url: str, html: str):
        # soup = BeautifulSoup(html, features='lxml')
        soup = BeautifulSoup(html, features='html.parser')
        all_a_tags = soup.find_all('a')
        all_a_tags = filter(lambda tag: tag.get('href') is not None, all_a_tags)
        all_href = {tag['href'] for tag in all_a_tags}
        self.page_map[page_url] = len(all_href)
        for link in all_href:
            if link.startswith('/'): link = page_url + link # Append the link to current URL if it is a relative path
            self.to_be_visited_queue.append(link)
    
    def write_to_csv(self, dictionary: dict, col1_name: str, col2_name: str, file_name: str) -> None:
        new_dict = {
            col1_name: [k for k in dictionary.keys()], 
            col2_name: [v for v in dictionary.values()]
        }
        new_df = pd.DataFrame.from_dict(new_dict)
        if os.path.exists(file_name):
            exist_df = pd.read_csv(file_name, index_col=0)
            exist_df.append(new_df).reset_index(drop=True).to_csv(file_name)
        else:
            new_df.reset_index(drop=True).to_csv(file_name)

english_seed_url = 'https://www.yahoo.com/'
english_seed_url = 'https://techcrunch.com/'
Crawler(english_seed_url, 'en', 5).parse_pages()

# chinese_seed_url = 'http://www.ruanyifeng.com/blog/2020/09/weekly-issue-125.html'
# Crawler(chinese_seed_url, 'zh-cn', 5).parse_pages()

# spanish_seed_url = 'https://espndeportes.espn.com/'
# # spanish_seed_url = 'https://www.milanuncios.com/'
# Crawler(spanish_seed_url, 'es', 5).parse_pages()
