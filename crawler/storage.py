import json
import tornadis

from tornado import gen

class RedisStorage:
    def __init__(self, host, port, queue_timeout=0.5):
        self.client = tornadis.Client(host=host, port=port, autoconnect=True)
        self.queue_timeout = queue_timeout

    @gen.coroutine
    def url_fetched(self, page_info):
        for url in page_info['links']:
            self.url_discovered(url)
        yield self.client.call('SET', 'url:%s' % page_info['url'], json.dumps(page_info))

    @gen.coroutine
    def url_discovered(self, url):
        is_new = yield self.client.call('SADD', 'discovered', url)
        if is_new:
            print('Discovered: ' + url)
            yield self.client.call('SADD', 'fetch_queue', url)

    @gen.coroutine
    def next_url(self):
        url = yield self.client.call('SPOP', 'fetch_queue')
        if not url:
            yield gen.sleep(self.queue_timeout)
            url = yield self.client.call('SPOP', 'fetch_queue')
        raise gen.Return(url)

    @gen.coroutine
    def get_all_page_info(self):
        keys = yield self.client.call('KEYS', 'url:*')
        infos = yield self.client.call('MGET', *keys)
        raise gen.Return([json.loads(info) for info in infos])
