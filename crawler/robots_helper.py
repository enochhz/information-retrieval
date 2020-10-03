from urllib import parse
from urllib import robotparser
from usp.tree import sitemap_tree_for_homepage

class RobotsHelper:

    @staticmethod
    def allow_to_visit(host_name: str, page_url: str) -> list:
        """
        Evaluate whether a page can be visit or not by parsing the robots.txt of the host website.
        :return: True if the url is allowed to visit, False otherwise
        """
        agent_name = '*'
        if host_name.endswith('/'):
            url_base = 'https://'+host_name
        else: 
            url_base = 'https://'+host_name + '/'
        parser = robotparser.RobotFileParser()
        parser.set_url(parse.urljoin(url_base, 'robots.txt'))
        parser.read()
        disallow_pages = [], []
        return parser.can_fetch(agent_name, page_url)
    
    @staticmethod
    def pages_from_sitemap(page_url: str) -> list:
        tree = sitemap_tree_for_homepage(page_url)
        return [page.url for page in tree.all_pages()]
