import os
import csv
import re
import random
from bs4 import BeautifulSoup
# from selenium import webdriver
from urllib.request import urlopen
import time
import pandas as pd
import collections
import requests
from crawler.html_page_helper import HTMLPageHelper
from crawler.file_manager import FileManager
from crawler.robots_helper import RobotsHelper
# from robots_deteor import robot_detector

class WebCrawler:

    visited_hosts = set()
    recent_visited_hosts = collections.deque([], maxlen = 10)
    banned_hosts = set() # To keep track of websites in different language
    banned_pages = set()
    to_be_visited_pages = []
    page_limit = 5
    page_map = {}
    error_map = {}
    skip = 0
    site_map = False

    def __init__(self, seed_url, language = 'en', page_limit = 5, site_map = False, html_content_folder = 'folder', csv_folder = 'csv_report'):
        self.to_be_visited_pages = [seed_url]
        self.page_map, self.error_map = {}, {}
        self.banned_hosts = set()
        self.banned_pages = set()
        self.visited_hosts = set()
        self.lang  = language
        self.page_limit = page_limit
        self.site_map = site_map
        self.html_content_folder = html_content_folder
        self.csv_folder = csv_folder
        FileManager.make_directories(self.html_content_folder, self.lang, csv_folder)
    
    def parse_pages(self) -> None:
        while (len(self.to_be_visited_pages) > 0) and (len(self.page_map.keys()) < self.page_limit): # Limit is not hit
            try:
                page_url = random.choices(self.to_be_visited_pages)[0] # Pick a random page from the queue
                self.to_be_visited_pages.remove(page_url)
                host_name = HTMLPageHelper.extract_host_name(page_url)
                if (not self.valid_page_url(host_name, page_url)) or (not self.valid_host_name(host_name)): continue
                if self.site_map:
                    site_map_pages = RobotsHelper.pages_from_sitemap(page_url) # Get pages from sitemap
                    self.to_be_visited_pages.extend(site_map_pages)
                if not self.parse_and_store_page(host_name, page_url): continue
                print(page_url)
            except Exception as e: 
                self.error_map[page_url] = str(e)
        FileManager.write_to_csv(self.page_map, 'root_url', 'num_of_out_links', f'./{self.csv_folder}/info.csv') # Write outlinks analysis csv
        FileManager.write_to_csv(self.error_map, 'root_url', 'error_info', f'./{self.csv_folder}/error.csv') # Write error csv
    
    def valid_page_url(self, host_name: str, page_url: str) -> bool:
        """
        Evaluates whether the page is allowed to visit.
        """
        if page_url in self.banned_pages: return False
        if not RobotsHelper.allow_to_visit(host_name, page_url): 
            self.banned_pages.add(page_url)
            return False
        return True
    
    def valid_host_name(self, host_name: str) -> bool: 
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
        self.to_be_visited_pages.append(host_name) # Apppend the url to the to be visited queue
        self.skip += 1
        return False

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
            self.banned_hosts.add(host_name) # block the host if it is in different langauge
            return False
        FileManager.store_html_content(page_url, html, f'{self.html_content_folder}/{self.lang}')
        out_links = HTMLPageHelper.count_out_links(page_url, html)
        self.page_map[page_url] = len(out_links)
        self.to_be_visited_pages.extend(out_links)
        return True
