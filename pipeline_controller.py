from crawler.web_crawler import WebCrawler
from noise_remover.noise_remover import NoiseRemover
import glob
import nltk
nltk.download('punkt')

class PipelineController:

    def __init__(self, url_map: dict, html_folder: str):
        self.url_maps = url_map
        self.html_folder = html_folder
    
    def start(self):
        self.crawl_pages()
        self.remove_noise()

    def crawl_pages(self):
        for seed_url, language in self.url_maps.items():
            WebCrawler(seed_url, language=language, page_limit=100, html_content_folder = self.html_folder, batch_size=10).parse_pages()

    def remove_noise(self):
        languages = ['en', 'es', 'zh-cn']
        noise_remover = NoiseRemover()
        for language in languages:
            html_list = glob.glob(f"./{self.html_folder}/{language}/*.html")
            for html in html_list:
                noise_remover.remove_noise(html, language)

if __name__ == '__main__':
    url_map = {
        'https://techcrunch.com/': 'en',
        'https://www.chineseinla.com/': 'zh-cn',
        'https://www.bbc.com/mundo/noticias-internacional-54320690': 'es',
    }
    html_folder = 'folder'
    PipelineController(url_map, html_folder).start()
