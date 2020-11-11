from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

class WebCralwer:

    page_to_be_visited = set()
    visited_pages = set()
    visited_page_map = {}
    visited_pages_id = {}

    def __init__(self, seed_url='https://en.wikipedia.org/wiki/Computer_science', page_limit=100):
        self.page_to_be_visited.add(seed_url)
        self.page_limit = page_limit
    
    def start_parsing(self):
        while len(self.visited_pages) < self.page_limit and len(self.page_to_be_visited) > 0:
            try:
                current_page = self.page_to_be_visited.pop()
                outlinks = self.parse_page_content(current_page) 
                self.visited_pages_id[current_page] = len(self.visited_pages)
                self.visited_page_map[current_page] = outlinks
                self.visited_pages.add(current_page)
                print(f'{current_page}: {len(outlinks)}')
                self.page_to_be_visited.update({ link for link in outlinks if link not in self.visited_pages}) # Append pages to be visited
            except Exception as e:
                print(str(e))
    
    def parse_page_content(self, page_url: str) -> set:
        html = urlopen(page_url).read().decode('utf-8') 
        soup = BeautifulSoup(html, features='html.parser')
        all_a_tags = soup.find_all('a')
        all_a_tags = filter(lambda tag: tag.get('href') is not None, all_a_tags)
        all_href = {tag['href'] for tag in all_a_tags}
        all_href = {page_url + href if href.startswith('/') else href for href in all_href} # Append the link to current URL if it is a relative path
        return all_href
    
    def store_info_in_csv(self):
        url_id_df = pd.DataFrame(columns = ['url', 'id'])
        pandas_df = pd.DataFrame(columns = ['source_url', 'link_to_urls'])
        for url, link_to_urls in self.visited_page_map.items():
            self.visited_pages_id[url] = len(self.visited_pages_id.keys())
            url_id = self.visited_pages_id[url]
            url_id_df = url_id_df.append({
                'url': url,
                'id': self.visited_pages_id[url],
            }, ignore_index=True)
            link_to_urls_ids = set()
            for link in link_to_urls:
                self.visited_pages_id[link] = len(self.visited_pages_id.keys())
                url_id_df = url_id_df.append({
                    'url': link,
                    'id': self.visited_pages_id[link],
                }, ignore_index=True)
                link_to_urls_ids.add(self.visited_pages_id[link])
            pandas_df = pandas_df.append({
                'source_url': url_id,
                'link_to_urls': link_to_urls_ids
            }, ignore_index=True)
        pandas_df.to_csv('parsed_pages_id.csv')
        url_id_df.to_csv('url_id.csv')
    
if __name__ == '__main__':
    crawler = WebCralwer()
    crawler.start_parsing()
    crawler.store_info_in_csv()
