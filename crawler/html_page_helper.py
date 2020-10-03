from langdetect import detect, detect_langs
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import operator
import re

class HTMLPageHelper:

    #  'English': 'en', 'Chinese': 'zh-cn', 'Spanish': 'es'
    languages = ['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he',
                'hi', 'hr', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml', 'mr', 'ne', 'nl', 'no', 'pa', 'pl',
                'pt', 'ro', 'ru', 'sk', 'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']
    language_tracker_pattern = {lan: 0 for lan in languages}

    @staticmethod
    def detect_language(html_content: str):
        language_tracker = HTMLPageHelper.language_tracker_pattern.copy()
        soup = BeautifulSoup(html_content, features = 'lxml') 
        texts = set(soup.findAll(text = True)) # Only extract text
        for text in texts:
            try: language_tracker[detect(text)] += 1
            except Exception as e: pass
        return max(language_tracker.items(), key=operator.itemgetter(1))[0] # Most frequent language
    
    @staticmethod
    def count_out_links(page_url: str, html: str) -> set:
        # soup = BeautifulSoup(html, features='lxml')
        soup = BeautifulSoup(html, features='html.parser')
        all_a_tags = soup.find_all('a')
        all_a_tags = filter(lambda tag: tag.get('href') is not None, all_a_tags)
        all_href = {tag['href'] for tag in all_a_tags}
        all_href = {page_url + href if href.startswith('/') else href for href in all_href} # Append the link to current URL if it is a relative path
        return all_href

    @staticmethod
    def extract_host_name(page_url: str) -> str:
        url_pattern = '(?:http.*://)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*'
        return re.search(url_pattern, page_url).group('host')
