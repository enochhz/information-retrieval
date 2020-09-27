from langdetect import detect, detect_langs
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import operator

#  'English': 'en', 'Chinese': 'zh-cn', 'Spanish': 'es'
languages = ['af', 'ar', 'bg', 'bn', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'gu', 'he',
              'hi', 'hr', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lt', 'lv', 'mk', 'ml', 'mr', 'ne', 'nl', 'no', 'pa', 'pl',
              'pt', 'ro', 'ru', 'sk', 'sl', 'so', 'sq', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi', 'zh-cn', 'zh-tw']
language_tracker_pattern = {lan: 0 for lan in languages}

def detect_language(html_content: str):
    language_tracker = language_tracker_pattern.copy()
    soup = BeautifulSoup(html_content, features = 'lxml') 
    texts = set(soup.findAll(text = True)) # Only extract text
    for text in texts:
        try: language_tracker[detect(text)] += 1
        except Exception as e: pass
    return max(language_tracker.items(), key=operator.itemgetter(1))[0] # Most frequent language

# seed_url = 'https://techcrunch.com/'
# seed_url = 'https://www.amazon.es/'
# seed_url = 'https://www.milanuncios.com/'
# html_content = requests.get(seed_url).content.decode('utf-8')
# main_language = detect_language(html_content)
# print(main_language)
