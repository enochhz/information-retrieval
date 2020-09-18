import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
import time

class Crawler:

    page_limit = 100
    page_map = {}
    page_stack = []

    def __init__(self, seed_url, language: str):
        self.page_stack.append(seed_url)
        self.lang  = language

    def parse_pages(self):
        while len(self.page_stack) > 0:
            if (len(self.page_map.keys()) > self.page_limit): return
            # print(self.page_map)
            page_url = self.page_stack.pop()
            # check language (page_url): 80% 
            # checkRobots(page_url)
            # duplicates(page_url)
            print(page_url)
            html = urlopen(page_url).read().decode('utf-8')
            soup = BeautifulSoup(html, features='lxml')
            all_href = soup.find_all('a')
            all_href = [l['href'] for l in all_href]
            self.page_map[page_url] = len(all_href)
            print(self.page_map)
            for link in all_href:
                self.page_stack.append(link)
            # time.sleep(0.5)

    def write_to_csv(self, file_name):
        with open(file_name, 'w', newline='') as file:
            write = csv.writer(file)
            write.writerow(['book_title', 'description'])
            for title, description in self.book_dict.items():
                write.writerow([title, description])

# techcren: 50 links
# google: 100 links          
# 
seed = 'https://techcrunch.com/'
# seed = 'https://morvanzhou.github.io/tutorials/data-manipulation/scraping/2-01-beautifulsoup-basic/'
# seed = 'https://morvanzhou.github.io/tutorials/data-manipulation/scraping/2-01-beautifulsoup-basic/'
crawler = Crawler(seed)
crawler.parse_pages()

# doubanParser.write_to_csv('books.csv')
