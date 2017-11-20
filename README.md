# A web crawler prototype
A simple web crawler prototype built with tornado and redis.

## Design decisions
* Failed requests lead to skipped pages. Reason: simplicity.

Steps to run the crawler:
1. Run redis: `redis-server redis.conf`
2. Run app: `python crawler/crawler.py`
