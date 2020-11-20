from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import redis
import random
import threading

class WebCrawler:

    page_to_be_visited = set()
    visited_pages = set()
    threads_num = 10

    def __init__(self, domain: str, seed_url: str, page_limit = 100):
        self.domain = domain
        self.page_to_be_visited.add(seed_url)
        self.page_limit = page_limit
        self.redis_db = redis.Redis(host='localhost', port=6379, db=0, charset='utf-8', decode_responses=True)
        all_keys = self.redis_db.scan_iter()
        for key in all_keys: self.redis_db.delete(key) # Delete all key value pairs
    
    def start_parsing(self) -> None:
        while len(self.visited_pages) < self.page_limit and len(self.page_to_be_visited) > 0:
            threads = list()
            for i in range(self.threads_num):
                threads.append(threading.Thread(target = self.parse_new_page))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        print(f'visited pages num: {len(self.visited_pages)}')

    def parse_new_page(self) -> None:
        try:
            current_page = self.page_to_be_visited.pop()
            outlinks = self.extract_outlinks(current_page) 
            outlinks_str = ','.join([link for link in outlinks])
            self.redis_db.set(current_page, outlinks_str)
            self.visited_pages.add(current_page)
            print(f'{len(self.visited_pages)} - {current_page} - {len(outlinks)}')
            self.page_to_be_visited.update({ link for link in outlinks if link not in self.visited_pages}) # Append not-visited pages to the queue
        except Exception as e:
            self.visited_pages.add(current_page)
            print(f'error: {str(e)}')

    def extract_outlinks(self, page_url: str) -> set:
        html = urlopen(page_url).read().decode('utf-8') 
        soup = BeautifulSoup(html, features='html.parser')
        all_a_tags = soup.find_all('a')
        all_a_tags = filter(lambda tag: tag.get('href') is not None, all_a_tags)
        all_href = {tag['href'] for tag in all_a_tags}
        all_href = {page_url + href if href.startswith('/') else href for href in all_href} # Append the link to current URL if it is a relative path
        valid_href = {link for link in all_href if self.extract_host_name(link) == self.domain} # Only extract urls in the specific domain
        return valid_href

    def extract_host_name(self, page_url: str) -> str:
        url_pattern = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        return re.search(url_pattern, page_url).group('host')
    
if __name__ == '__main__':
    start_time = time.time()
    crawler = WebCrawler(domain='www.cdc.gov', seed_url = 'https://www.cdc.gov', page_limit = 1000)
    crawler.start_parsing()
    print(f'time used: {time.time() - start_time}')
