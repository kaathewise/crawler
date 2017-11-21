import unittest

from crawler import Crawler

class TestCrwaler(unittest.TestCase):
    def testExtractFeatures(self):
        url = 'http://website.com/'
        page = '''
        <html>
            <head><script src="/main.js"></script></head>
            <body>
                <img src="/logo.png">
                <img src="http://google.com/favicon.ico">
                <a href="/contacts">
                <a href="http://google.com">
                <a href="https://website.com/admin"
            </body>
        </html>
        '''
        expected_features = {
            'url': url,
            'title': '',
            'links': ['http://website.com/contacts', 'https://website.com/admin'],
            'img': ['http://website.com/logo.png'],
            'js': ['http://website.com/main.js']
        }
        self.assertEqual(Crawler.extract_features(url, page), expected_features)

    def testNormalizeUrl(self):
        url = 'http://website.com/main'
        self.assertEqual(Crawler.normalize_url('/admin#hashtag', url), 'http://website.com/admin')
        self.assertEqual(Crawler.normalize_url('http://google.com', url), None)
        self.assertEqual(Crawler.normalize_url('https://website.com/admin', url), 'https://website.com/admin')

if __name__ == '__main__':
    unittest.main()
