# A web crawler prototype
A simple web crawler prototype built with tornado and redis.

## Design decisions
* Failed requests lead to skipped pages. Reason: simplicity for prototyping.
* Instead of checking whether there is an url being fetched that could generate
new urls, storage is simply waiting for 0.5s if the queue is empty.
Reason: simplicity for prototyping.

Steps to run the crawler:
1. Run redis: `redis-server redis.conf`
2. Run app: `python crawler/crawler.py --url tomblomfield.com`
