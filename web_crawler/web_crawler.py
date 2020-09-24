import requests
from bs4 import BeautifulSoup

seed_url = 'https://www.yahoo.com/'
seed_url = 'http://www.ruanyifeng.com/blog/2020/09/weekly-issue-125.html'
seed_url = 'https://techcrunch.com/'
page = requests.get(seed_url)
# print(page.text.strip()[:1000])
# print()
# print(page.content[:1000])
soup = BeautifulSoup(page.content, 'html.parser')
for a_tag in soup.findAll('a'):
    href = a_tag.attrs.get('href')
    print(href)

