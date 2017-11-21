import unittest
import tornadis

from tornado import gen, ioloop, testing
from storage import RedisStorage

class TestRedisStorage(testing.AsyncTestCase):
    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    @testing.gen_test
    def testFullCycle(self):
        rs = RedisStorage('localhost', 6154)
        yield rs.client.call('FLUSHDB')

        sitemap = [
            {
                'url': 'http://website.com',
                'links': ['http://website.com/main', 'https://website.com/admin'],
                'js': [],
                'img': [],
                'title': ''
            },
            {
                'url': 'http://website.com/main',
                'links': ['http://website.com/main/contacts', 'https://website.com/admin'],
                'js': [],
                'img': [],
                'title': ''
            },
            {
                'url': 'https://website.com/admin',
                'links': ['http://website.com/main', 'https://website.com/admin'],
                'js': [],
                'img': [],
                'title': ''
            },
            {
                'url': 'http://website.com/main/contacts',
                'links': ['http://website.com/main', 'https://website.com/admin'],
                'js': [],
                'img': [],
                'title': ''
            }
        ]

        page_info_by_url = dict((p['url'], p) for p in sitemap)
        yield rs.url_discovered('http://website.com')

        for i in xrange(4):
            url = yield rs.next_url()
            yield rs.url_fetched(page_info_by_url[url])
        url = yield rs.next_url()
        self.assertIsNone(url)

        actual_sitemap = yield rs.get_all_page_info()
        self.assertSitemapsEqual(actual_sitemap, sitemap)

    def assertSitemapsEqual(self, map1, map2):
        c = lambda a, b: cmp(a['url'], b['url'])
        self.assertEqual(sorted(map1, c), sorted(map2, c))


if __name__ == '__main__':
    unittest.main()
