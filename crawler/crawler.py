import json
import re

from bs4 import BeautifulSoup
from tornado import ioloop, httpclient, gen, process
from urlparse import urljoin, urlparse
from storage import RedisStorage

class Crawler(object):
    def __init__(self, storage):
        self.client = httpclient.AsyncHTTPClient()
        self.storage = storage

    @gen.coroutine
    def run(self):
        while True:
            url = yield self.storage.next_url()
            if not url:
                return
            yield self.fetch(url)

    @gen.coroutine
    def fetch(self, url):
        try:
            response = yield self.client.fetch(url)
        except:
            return
        page_info = Crawler.extract_features(url, BeautifulSoup(response.body, 'html.parser'))
        self.storage.url_fetched(page_info)

    @staticmethod
    def normalize_url(url, original_url):
        if not url:
            return url
        re.sub(r'#.*', '', url)
        original_parsed = urlparse(original_url)
        url_parsed = urlparse(url)
        if url_parsed.netloc == original_parsed.netloc:
            return url
        elif not url_parsed.netloc:
            return urljoin(original_url, url)
        return None

    @staticmethod
    def extract_features(url, soup):
        urls = filter(
            None,
            [Crawler.normalize_url(link.get('href'), url) for link in soup.find_all('a')]
        )
        local_img = filter(
            None,
            [Crawler.normalize_url(img.get('src'), url) for img in soup.find_all('img')]
        )
        local_js = filter(
            None,
            [Crawler.normalize_url(script.get('src'), url) for script in soup.find_all('script')]
        )
        return {
            'url': url,
            'title': soup.title.string,
            'links': urls,
            'img': local_img,
            'js': local_js}

@gen.coroutine
def main():
    storage = RedisStorage('localhost', 6379)
    yield storage.url_discovered('https://fulc.ru')
    yield gen.multi([Crawler(storage).run() for i in range(10)])
    print 'All website crawled.'
    page_infos = yield storage.get_all_page_info()
    print '%s pages found:' % len(page_infos)
    for info in page_infos:
        print json.dumps(info, indent=2)

if __name__ == "__main__":
    ioloop.IOLoop.current().run_sync(main)
