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
from html_page_helper import HTMLPageHelper
from file_manager import FileManager
# from robots_deteor import robot_detector

class WebCrawler:

    visited_hosts = set()
    recent_visited_hosts = collections.deque([], maxlen = 10)
    banned_hosts = [] # To keep track of websites in different language
    to_be_visited_queue = []
    page_limit = 5
    page_map = {}
    error_map = {}
    skip = 0
    html_content_folder = 'folder' 

    def __init__(self, seed_url, language: str, page_limit: int):
        self.to_be_visited_queue = [seed_url]
        self.page_map, self.error_map = {}, {}
        self.banned_hosts = []
        self.visited_hosts = set()
        self.lang  = language
        self.page_limit = page_limit
        FileManager.make_directories(self.html_content_folder, self.lang)
    
    def parse_pages(self) -> None:
        while (len(self.to_be_visited_queue) > 0) and (len(self.page_map.keys()) < self.page_limit): # Limit is not hit
            try:
                page_url = self.to_be_visited_queue.pop(0) # Poll the first page from the to be visited queue
                host_name = HTMLPageHelper.extract_host_name(page_url)
                if not self.evaluate_host_name(host_name): continue
                print(page_url)
                self.check_robots_txt() # TODO
                if not self.parse_and_store_page(host_name, page_url): continue
            except Exception as e: 
                self.error_map[page_url] = str(e)
        FileManager.write_to_csv(self.page_map, 'root_url', 'num_of_out_links', './info.csv') # Write outlinks analysis csv
        FileManager.write_to_csv(self.error_map, 'root_url', 'error_info', './error.csv') # Write error csv
    
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
        if page_url.endswith('.html'): html = requests.get(page_url).content.decode('utf-8') # Parse html file (e.g., https://www.test.com/main.html)
        else: html = urlopen(page_url).read().decode('utf-8') # Parse regular URL (e.g., https://www.techcruntch.com)
        # Check if the page is in the right language
        # if not self.valid_language(host_name, html): return False
        language = HTMLPageHelper.detect_language(html)
        if language != self.lang: 
            self.banned_hosts.append(host_name) # block the host if it is in different langauge
            return False
        FileManager.store_html_content(page_url, html, f'{self.html_content_folder}/{self.lang}')
        out_links = HTMLPageHelper.count_out_links(page_url, html)
        self.page_map[page_url] = len(out_links)
        self.to_be_visited_queue.extend(out_links)
        return True
    
# english_seed_url = 'https://www.yahoo.com/'
english_seed_url = 'https://techcrunch.com/'
WebCrawler(english_seed_url, 'en', 5).parse_pages()

chinese_seed_url = 'http://www.ruanyifeng.com/blog/2020/09/weekly-issue-125.html'
WebCrawler(chinese_seed_url, 'zh-cn', 5).parse_pages()

spanish_seed_url = 'https://espndeportes.espn.com/'
# spanish_seed_url = 'https://www.milanuncios.com/'
spanish_seed_url = 'https://www.bbc.com/mundo/noticias-internacional-54320690'
WebCrawler(spanish_seed_url, 'es', 5).parse_pages()
