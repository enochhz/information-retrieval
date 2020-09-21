import csv
import re
from bs4 import BeautifulSoup
# from selenium import webdriver
from urllib.request import urlopen
import time
import pandas as pd

class Crawler:

    page_limit = 10
    html_folder = 'folder' 
    page_map = {}
    page_stack = []

    def __init__(self, seed_url, language: str):
        self.page_stack.append(seed_url)
        self.lang  = language

    def parse_pages(self):
        while len(self.page_stack) > 0:
            if (len(self.page_map.keys()) > self.page_limit): break 
            try:
                page_url = self.page_stack.pop()
                # check language (page_url): 80% 
                # checkRobots(page_url)
                # duplicates(page_url)
                print(page_url)
                html = urlopen(page_url).read().decode('utf-8')
                self.store_html(page_url, html)
                self.count_links(page_url, html)
            except Exception as e:
                print(str(e))
        self.write_to_csv('./info.csv')
    
    def store_html(self, page_url: str, html: str):
        path_name = page_url.split('https://')[1]
        path_name = path_name.replace('/', '#')
        print(path_name)
        file_name = f'{self.html_folder}/{path_name}.html'
        text_file = open(file_name, 'w')
        text_file.write(html)
        text_file.close()

    def count_links(self, page_url: str, html: str):
        soup = BeautifulSoup(html, features='lxml')
        all_href = soup.find_all('a')
        all_href = [l['href'] for l in all_href]
        self.page_map[page_url] = len(all_href)
        for link in all_href:
            self.page_stack.append(link)

    def write_to_csv(self, file_name: str):
        new_dict = {
            'root_url': [k for k in self.page_map.keys()], 
            'num_of_out_links': [v for v in self.page_map.values()]
        }
        pandas_df = pd.DataFrame.from_dict(new_dict)
        pandas_df.to_csv(file_name)
        # with open(file_name, 'w', newline='') as file:
        #     write = csv.writer(file)
        #     write.writerow(['root_url', 'num_of_out_links'])
        #     for url, num in self.page_map.items():
        #         write.writerow([url, num])

seed = 'https://techcrunch.com/'
seed = 'https://www.yahoo.com/'
crawler = Crawler(seed, 'English')
crawler.parse_pages()
