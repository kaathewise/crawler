import argparse
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
        except Exception as e:
            print 'Error while fetching "%s": %s' % (url, e)
            return
        page_info = Crawler.extract_features(url, response.body)
        self.storage.url_fetched(page_info)

    @staticmethod
    def normalize_url(url, original_url):
        if not url:
            return url
        url = re.sub(r'#.*', '', url)
        original_parsed = urlparse(original_url)
        url_parsed = urlparse(url)
        if url_parsed.netloc == original_parsed.netloc:
            return url
        elif not url_parsed.netloc:
            return urljoin(original_url, url)
        return None

    @staticmethod
    def extract_features(url, page):
        soup = BeautifulSoup(page, 'html.parser')
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
            'title': soup.title.string if soup.title else '',
            'links': urls,
            'img': local_img,
            'js': local_js}

parser = argparse.ArgumentParser(description='Simple web crawler')
parser.add_argument('--url', dest='url', required=True, help='website to crawl')
parser.add_argument('--redis', dest='redis', default='localhost:6379', help='redis instance')
parser.add_argument('--workers', dest='workers', type=int, default=10, help='number of workers')

@gen.coroutine
def main():
    args = parser.parse_args()
    r_host, r_port = args.redis.split(':')
    storage = RedisStorage(r_host, int(r_port))
    yield storage.url_discovered(args.url)
    yield gen.multi([Crawler(storage).run() for i in range(args.workers)])
    print 'All website crawled.'
    page_infos = yield storage.get_all_page_info()
    print '%s pages found:' % len(page_infos)
    for info in page_infos:
        print json.dumps(info, indent=2)

if __name__ == "__main__":
    ioloop.IOLoop.current().run_sync(main)
